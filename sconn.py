from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ether_types
from ryu.topology import event
from ryu.topology.api import get_switch, get_link

import networkx as nx
import logging


class SconnControllerV9(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SconnControllerV9, self).__init__(*args, **kwargs)
        self.topology_api_app = self

        self.switch_net = nx.DiGraph()     # 有向拓樸
        self.stp_net = nx.DiGraph()        # STP 有向拓樸

        self.mac_to_port = {}
        self.datapaths = {}
        self.manual_link_added = False

        self.logger.setLevel(logging.INFO)

    # Switch 連線
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Table-miss
        match = parser.OFPMatch()
        actions = [
            parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                   ofproto.OFPCML_NO_BUFFER)
        ]
        self.add_flow(datapath, 0, match, actions)
        self.logger.info("Switch %s connected", datapath.id)

    def add_flow(self, dp, priority, match, actions, buffer_id=None, idle=0, hard=0):
        parser = dp.ofproto_parser
        ofproto = dp.ofproto
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]

        mod = parser.OFPFlowMod(
            datapath=dp,
            buffer_id=buffer_id if buffer_id is not None else ofproto.OFP_NO_BUFFER,
            idle_timeout=idle, hard_timeout=hard,
            priority=priority, match=match,
            instructions=inst
        )
        dp.send_msg(mod)

    # ===============================
    #   STP 計算（已修正：空圖防呆）
    # ===============================
    def _calculate_stp(self):

        if len(self.switch_net.nodes()) == 0:
            self.logger.info("No nodes in topology, skip STP")
            self.stp_net.clear()
            return

        if len(self.switch_net.edges()) == 0:
            self.logger.info("No links available. STP = empty")
            self.stp_net.clear()
            return

        undirected = self.switch_net.to_undirected()

        try:
            mst = nx.minimum_spanning_tree(undirected)
        except Exception:
            self.logger.warning("MST calculation failed. Keeping STP empty.")
            self.stp_net.clear()
            return

        self.stp_net.clear()
        for u, v in mst.edges():
            if self.switch_net.has_edge(u, v):
                port = self.switch_net[u][v].get('port')
                if port is not None:
                    self.stp_net.add_edge(u, v, port=port)
            if self.switch_net.has_edge(v, u):
                port = self.switch_net[v][u].get('port')
                if port is not None:
                    self.stp_net.add_edge(v, u, port=port)

        self.logger.info("STP edges: %s", sorted(self.stp_net.edges()))

    # ===============================
    #   拓樸變化處理（已修：LinkDelete 不再 flush）
    # ===============================
    @set_ev_cls([event.EventSwitchEnter, event.EventLinkAdd, event.EventLinkDelete])
    def topology_change_handler(self, ev):

        # Switch 進入
        if isinstance(ev, event.EventSwitchEnter):
            dpid = ev.switch.dp.id
            self.switch_net.add_node(dpid)
            self.logger.info("Switch %s entered", dpid)

            # 手動 AP1 - AP2 mesh link
            if (not self.manual_link_added) and 2 in self.switch_net and 3 in self.switch_net:
                self.switch_net.add_edge(2, 3, port=6)
                self.switch_net.add_edge(3, 2, port=6)
                self.manual_link_added = True
                self.logger.info("Manually added wireless mesh link 2 <-> 3")

        # Link 新增
        elif isinstance(ev, event.EventLinkAdd):
            link = ev.link
            s = link.src
            d = link.dst

            self.switch_net.add_edge(s.dpid, d.dpid, port=s.port_no)
            self.switch_net.add_edge(d.dpid, s.dpid, port=d.port_no)

            self.logger.info("Link add: %s:%s <-> %s:%s",
                             s.dpid, s.port_no, d.dpid, d.port_no)

        # Link 刪除（修正：不 flush flows、不清 MAC、不重建整張圖）
        elif isinstance(ev, event.EventLinkDelete):
            link = ev.link
            s = link.src
            d = link.dst

            removed = False
            if self.switch_net.has_edge(s.dpid, d.dpid):
                self.switch_net.remove_edge(s.dpid, d.dpid)
                removed = True

            if self.switch_net.has_edge(d.dpid, s.dpid):
                self.switch_net.remove_edge(d.dpid, s.dpid)
                removed = True

            if removed:
                self.logger.warning("Link removed: %s <-> %s", s.dpid, d.dpid)
                # ❗ 不要 flush flows 和 mac，保持網路不中斷

        # Recalculate STP
        self._calculate_stp()
        self.logger.info("Current directed edges: %s", sorted(self.switch_net.edges()))

    # ===============================
    #   Packet-in
    # ===============================
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):

        msg = ev.msg
        dp = msg.datapath
        parser = dp.ofproto_parser
        ofproto = dp.ofproto
        dpid = dp.id
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth_pkt = pkt.get_protocol(ethernet.ethernet)

        if eth_pkt.ethertype == ether_types.ETH_TYPE_LLDP:
            return

        src = eth_pkt.src
        dst = eth_pkt.dst

        self.mac_to_port.setdefault(dpid, {})

        # Learn MAC
        if self.mac_to_port[dpid].get(src) != in_port:
            self.mac_to_port[dpid][src] = in_port
            self.logger.info("Learn MAC %s on %s:%s", src, dpid, in_port)

        # 已知目的
        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
            actions = [parser.OFPActionOutput(out_port)]

        # 未知目的 -> STP Flood
        else:
            self.logger.info("Unknown %s on %s, STP Flood", dst, dpid)

            all_ports = list(self.datapaths[dpid].ports.keys())
            inter_ports = []

            # 找 inter-switch ports
            if dpid in self.switch_net:
                for n in self.switch_net.successors(dpid):
                    p = self.switch_net[dpid][n].get("port")
                    if p is not None:
                        inter_ports.append(p)

            flood_ports = []
            for p in all_ports:
                if p == in_port:
                    continue
                if p not in inter_ports:
                    flood_ports.append(p)
                else:
                    nb = self._get_neighbor_by_port(dpid, p)
                    if dpid in self.stp_net and nb in self.stp_net[dpid]:
                        flood_ports.append(p)

            actions = [parser.OFPActionOutput(p) for p in flood_ports]

        # 單播 flow 安裝
        if len(actions) == 1:
            out_port = actions[0].port
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst)
            self.add_flow(dp, 1, match, actions, idle=10, hard=30)

        # 發 packetOut
        data = msg.data if msg.buffer_id == ofproto.OFP_NO_BUFFER else None
        out = parser.OFPPacketOut(
            datapath=dp,
            buffer_id=msg.buffer_id,
            in_port=in_port,
            actions=actions,
            data=data
        )
        dp.send_msg(out)

    # ===============================
    #   由 port 找 neighbor
    # ===============================
    def _get_neighbor_by_port(self, dpid, port):
        if dpid not in self.switch_net:
            return None
        for nb in self.switch_net.successors(dpid):
            if self.switch_net[dpid][nb].get("port") == port:
                return nb
        return None

    # ===============================
    #   Datapath register
    # ===============================
    @set_ev_cls(ofp_event.EventOFPStateChange, [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        dp = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            self.datapaths.setdefault(dp.id, dp)
        elif ev.state == DEAD_DISPATCHER:
            if dp.id in self.datapaths:
                del self.datapaths[dp.id]


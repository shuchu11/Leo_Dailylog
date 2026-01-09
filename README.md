# 2026.01.09

- [ x ] 測試 Pegatron RU

  - [ x ] ---> 用岳桓的 srsRAN + Pegatron RU 進行測試 :
    - [ x ] 一次性確認"RU是否可進行基本操作(登入/configure/M-plane)"
    - [ x ] "srsRAN split7.2 -DPDK version 成功安裝並運行" 

[ x ] ---> 進行 TM500 測試

[ x ] ---> 閱讀 RU 排程-溫度相對關係文件



[ x ] Notify vossic’s PM (Peter) a PDU’s outlet is broken

[ x ] Give vossic VPN and ensure ssh works

[ x ] Register all our server in vossic’s system


# 2026.01.08

----------- Set srsran server IP to 192.168.9.10---------------
sudo ip link add link ens192 name ens192.5 type vlan id 5
sudo ip link set ens192.5 up
sudo ip addr add 192.168.9.10/24 dev ens192.5

sudo ip route add 192.168.9.9/32 via 192.168.9.10 dev ens192.5     
sudo nmap -p 1-65535 -sS 192.168.9.9   



----------- Set TM500 IP to 192.168.9.9 --------

sudo ip addr add 192.168.9.9/24 dev eth2.5
sudo ip link set eth2.5 up


------------------------------------------------



測試 Pegatron RU

---> 用岳桓的 srsRAN + Pegatron RU 進行測試 : 一次性確認"RU是否可進行基本操作(登入/configure/M-plane)" + "srsRAN split7.2 -DPDK version 成功安裝並運行" 

---> 進行 TM500 測試

---> 閱讀 RU 排程-溫度相對關係文件

~~~ 詢問廠商 RU如何維護/放置 

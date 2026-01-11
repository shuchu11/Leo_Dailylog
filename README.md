# 2026.01.09

- [ x ] 測試 Pegatron RU

  - [ x ] ---> 用岳桓的 srsRAN + Pegatron RU 進行測試 :
    - [ x ] 	- 確定srsRAN vmware 可以ssh New Pegatron RU (switch 可以看見server端綁定的mac嗎? 還是只能看見自己端的)
	            - 開啟 Pegatron RU m-plane ( 在server/switch 皆開啟 vlan 104/103 )
    - [ x ] 一次性確認"RU是否可進行基本操作(登入/configure/M-plane)"
    - [ x ] "srsRAN split7.2 -DPDK version 成功安裝並運行" 

[ x ] ---> 進行 TM500 測試

[ x ] ---> 閱讀 RU 排程-溫度相對關係文件



[ x ] Notify vossic’s PM (Peter) a PDU’s outlet is broken

[ x ] Give vossic VPN and ensure ssh works

[ x ] Register all our server in vossic’s system

# 測試 Pegatron RU
## 確定srsRAN vmware 可以ssh New Pegatron RU ( switch 可以看見server端綁定的mac嗎? 還是只能看見自己端的 )
在 VMware 的 srsRAN VM 管理介面可以看到該 VM 配置的 mac address ( vlan5 - `00:0c:29:e2:0a:42` )
<img width="745" height="319" alt="image" src="https://github.com/user-attachments/assets/456be02b-c6a1-41fa-b77f-6296e3413808" />

找到了 srsRAN VM 內對應的網孔 
```
ens193
```
<img width="631" height="135" alt="image" src="https://github.com/user-attachments/assets/cafaf707-5bb7-419d-b8ed-ca4f949d3bb8" />

----> 開始嘗試設定 `ens193` IP 為 192.168.9.10 並 SSH new Pegatron RU

```
----------- Set srsran server IP to 192.168.9.10 / vlan 5---------------
sudo ip link add link ens193 name ens193.5 type vlan id 5
sudo ip link set ens193.5 up
sudo ip addr add 192.168.9.10/24 dev ens193.5

sudo ip route add 192.168.9.9/32 via 192.168.9.10 dev ens193.5     
sudo nmap -p 1-65535 -sS 192.168.9.9   
```

> [!caution]
> Ping 192.168.9.9 : `Unreachable`
> ```
> srsran@srsran-virtual-machine:~$ ping 192.168.9.9
> PING 192.168.9.9 (192.168.9.9) 56(84) bytes of data.
> From 192.168.9.10 icmp_seq=1 Destination Host Unreachable
> From 192.168.9.10 icmp_seq=2 Destination Host Unreachable
> ```
> **原因** : 發現 fronthaul switch 上 vlan  沒通
> 
> <img width="675" height="577" alt="image" src="https://github.com/user-attachments/assets/e589cb4b-d084-49e4-9047-b75ac95b5118" />
>
> **解決方法** : 在 fronthaul switch上新增 vlan 5 ( `xe10` : `vlan5`)  ocnos@192.168.8.25  , ocnos
>  ```
> OcNOS>enable
> OcNOS#configure terminal
> 
>  ! 第一步：切換介面模式
> OcNOS(config)# interface ge3
> OcNOS(config-if)# switchport trunk allowed vlan add 5
> 
> ! 第三步：提交設定使其生效
> OcNOS(config-if)# commit
> 
> ! 第四步: 確認是否生效
> OcNOS(config-if)# exit
> OcNOS(config)# exit
> OcNOS# show vlan brief
> ```
> - **Success to change**
> ```
> Bridge  VLAN ID     Name         State   H/W Status      Member ports
>                                                      (u)-Untagged, (t)-Tagged
> ======= ======= ================ ======= ========== ==========================
> ...
> ...
> 1       5       VLAN0005         ACTIVE  Success    ge3(t) xe8(t) xe10(t)
>                                                     xe12(t) xe15(t) xe16(t)
>                                                     xe18(t)
> 1       6       VLAN0006         ACTIVE  Success    xe8(t) xe12(t) xe16(t)
>                                                     xe17(t) xe18(t)
> 1       7       VLAN0007         ACTIVE  Success    xe8(t) xe12(t) xe16(t)
>                                                     xe18(t)
> 1       102     VLAN0102         ACTIVE  Success
> 1       103     VLAN0103         ACTIVE  Success    xe7(t) xe9(t) xe10(t)
>                                                     xe12(t) xe16(t)
> 1       104     VLAN0104         ACTIVE  Success    xe7(t) xe9(t) xe10(t)
>                                                     xe16(t)
> ```

 **Ping 192.168.9.9 : `Unreachable`**

 **潛在衝突**： 如果您的 VMware Port Group 已經設為 VLAN 4095（會傳送 Tag），而 Linux 內又設了 ens193.5（會再貼一層 Tag），這會導致 Double Tagging，實體 Switch 或 RU 絕對無法讀取這種封包。

 ```
sudo ip link set ens193.5 down
sudo ip addr add 192.168.9.10/24 dev ens193
```

**目前 交換機port - mac address** `xe10` Pega RU , `ge3` vm

```
 Bridge    CVLAN  SVLAN  BVLAN  Port                MAC Address       FWD   Time-out
 ---------+------+------+------+------------------+----------------+------+----------+
 1         1                    xe11                00e0.0c00.ae06    1     300
 1         1                    xe6                 3cec.efb1.db45    1     300
 1         1                    xe8                 3cec.efe4.ca67    1     300
 1         1                    xe9                 4821.0b4b.938e    1     300
 1         1                    xe10                4821.0b4b.dc41    1     300
 1         1                    xe18                507c.6f3b.de8b    1     300
 1         1                    ge0                 6cad.ad00.086d    1     300
 1         1                    ge2                 98f2.b323.8236    1     300
 1         1                    xe12                b496.91cf.0a80    1     300
 1         1                    xe16                d4f5.ef6a.7210    1     300
 1         1                    xe17                e8c7.4f25.80ed    1     300
 1         6                    xe12                0011.2233.4466    1     300
 1         6                    xe17                e8c7.4f25.80ed    1     300
 1         103                  xe9                 4821.0b4b.938e    1     300
 1         104                  xe9                 4821.0b4b.938e    1     300
```


------------------------------------------------------------------------------ 

**VM server故障**
-----> 改用server Lavoisier, ssh `oai72_su@192.168.8.82`


確定成功 ssh 到 Pegatron 的路徑 --> `ens1f1`, `192.168.9.10`
```
╭─oai72_su@Lavoisier ~
╰─$ ip route get 192.168.9.9                                                                                                                                                          255 ↵
192.168.9.9 dev ens1f1 src 192.168.9.10 uid 1000
```
 
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

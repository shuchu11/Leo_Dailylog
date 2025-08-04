# Components now need to be reinstalled

**Problems encountered so far**
- Testmac + FlexRAN + xFAPI + TM500
    -   [inish-script-fail](#11-inish-script-fail)
    -    [cvlsh-script-fail](#12-cvlsh-script-fail)
    -    [gnb-ptp-fail](#13-issue--gnb-ptp-fail)


# Checkpoint

| Item                                                                                                   | Status             |
| ------------------------------------------------------------------------------------------------------ | ------------------ |
| Bring up TM500                                                                                         | :heavy_check_mark: |
| Check TM500 PTP sync                                                                                   | :heavy_check_mark: |
| Use TMA to control TM500                                                                               | :heavy_check_mark: |
| Check csv files                                                                                        | :heavy_check_mark: |
| Connect TM500                                                                                          | :heavy_check_mark: |
| TM500 Connect Preference                                                                               | :heavy_check_mark: |
| Manually Set Configuration with Command                                                                | :heavy_check_mark: |
| gNB PTP synchronization                                                                                | :x:                |
| Prerequisite for gNB                                                                                   | :x:                |
| FlexRAN ( Terminal 1 )                                                                                 | :x:                |
| Testmac ( Terminal 2 )                                                                                 | :x:                |
| Check DU connection at RU side                                                                         | :x:                |
| Check RU connection at DU side                                                                         | :x:                |
| Init                                                                                                   | :x:                |
| Cell Search Result ( Stage 1 ( TM500 + FlexRAN + Testmac ) )                                           | :x:                |
| complete Stage 1 < TM500 + FlexRAN + Testmac >                                                         | :x:                |
| same steps as in Stage 1 TM500 Status                                                                  | :x:                |
| same steps as in Stage 1 Run TM500                                                                      | :x:                |
| gNB PTP synchronization                                                                                | :x:                |
| Prerequisite for gNB                                                                                   | :x:                |
| FlexRAN ( Terminal 1 )                                                                                 | :x:                |
| xFAPI ( Terminal 2 )                                                                                   | :x:                |
| ric_stub ( Terminal 3 )                                                                                | :x:                |
| cu_stub ( Terminal 4 )                                                                                 | :x:                |
| OSC L2 ( Terminal 5 )                                                                                  | :x:                |
| same steps as in Stage 1 Interoperability between DU and RU                                            | :x:                |
| Init                                                                                                   | :x:                |
| Cell Search Result Stage 2 ( TM500+FlexRAN+xFAPI+OSC L2+CU Stub )                                      | :x:                |
| complete Stage 2 < TM500+FlexRAN+xFAPI+OSC L2+CU Stub >                                                | :x:                |
| same steps as in Stage 1 TM500 Status                                                                  | :x:                |
| same steps as in Stage 1 Run TM500                                                                      | :x:                |
| gNB PTP synchronization                                                                                | :x:                |
| Prerequisite for gNB                                                                                   | :x:                |
| FlexRAN ( Terminal 1 )                                                                                 | :x:                |
| xFAPI ( Terminal 2 )                                                                                   | :x:                |
| ric_stub ( Terminal 3 )                                                                                | :x:                |
| OAI CU                                                                                                 | :x:                |
| OSC L2 ( Terminal 5 )                                                                                  | :x:                |
| same steps as in Stage 1 Interoperability between DU and RU                                            | :x:                |
| Init                                                                                                   | :x:                |
| Cell Search Result Stage 3 ( TM500+FlexRAN+xFAPI+OSC L2+OAI CU )                                       | :x:                |


## 1 Start to test server : Testmac + FlexRAN + xFAPI

###  1.1 `ini.sh` script fail 
```
cd
sudo su 
./ini.sh
exit
```
> [!Caution]
>An error occurred when running `./ini.sh`: this is because `ini.sh` was edited using a Windows editor (such as Notepad), where the line endings are in CRLF format (i.e., ^M). However, in a Linux environment, the correct line ending should be LF.
> ```bash
> bash: ./ini.sh: /bin/sh^M: bad interpreter: No such file or directory
> ```
> 
> **Solution :** Use Vim / nano editor (built into Linux)
> ```bash
> nano ini.sh
> # Or
> vim ini.sh
> ```
> Line endings will be automatically saved in **LF** format.


Below is the result of running ./ini.sh again: \
Required files are missing, and the script failed to execute successfully.
The following is the ERROR LOG.
```
root@ubuntu:/home/ubuntu# ./ini.sh
./ini.sh: 6: cd: can't cd to /home/ubuntu/dpdk-stable-22.11.1/usertools/
./ini.sh: 7: ./dpdk-devbind.py: not found
./ini.sh: 9: ./dpdk-devbind.py: not found
tee: /sys/module/vfio_pci/parameters/enable_sriov: No such file or directory
1
tee: /sys/module/vfio_pci/parameters/disable_idle_d3: No such file or directory
1
./ini.sh: 16: cd: can't cd to /home/ubuntu/pf-bb-config
./ini.sh: 17: ./pf_bb_config: not found
./ini.sh: 20: echo: echo: I/O error
```

### 1.2 `cvl.sh` script fail 

> [!Caution]
> Permission denied. Below is the ERROR LOG
> ```bash
> root@ubuntu:/home/ubuntu# ./cvl.sh
> bash: ./cvl.sh: Permission denied
> ```
> **Solution :**
> ```bash
> chmod +x cvl.sh  # Grant execution permission
> ./cvl.sh  # Run the script again
> ```
>
> **ERROR**
> ```bash
> root@ubuntu:/home/ubuntu/phy# dos2unix cvl.sh
> dos2unix: converting file cvl.sh to Unix format...
> root@ubuntu:/home/ubuntu/phy# ./cvl.sh
> ./cvl.sh: line 2: /sys/class/net/ens1f1/device/sriov_numvfs: No such file or directory
> ./cvl.sh: line 4: /sys/class/net/ens1f1/device/sriov_numvfs: No such file or directory
> Cannot find device "ens1f1"
> sudo: /usr/local/bin/dpdk-devbind.py: command not found
> SIOCSIFMTU: No such device
> netlink error: no device matches name (offset 24)
> netlink error: No such device
> ```

**Solution** : change interafce name in `cvl.sh` to `ens1f1np1`(need to change to your interface linked to TM500)

### 1.3 Issue  gNB PTP fail
The required packages are missing on the freshly reinstalled system. You can rebuild the environment by following the steps below.
```
sudo apt update 
sudo apt install linuxptp -y  # Install linuxptp

sudo apt install vim -y  # Install vim
sudo vim /etc/ptp4l.conf
```

Add ptp config in `ptp4l.conf`. And set the config as following.

- **domainNumber**: 24
- **network_transport**: L2
- **time_stamping**: hardware
- **tx_timestamp_timeout** 1
      - When use E810 NIC the tx_timestamp_timeout need to set to 50 or 100 to successful run ptp4l.
- **PTP grandmaster** is reachable via interafce **ens1f1np1**(need to change to your interface linked to TM500)

```
[global]
domainNumber           24
slaveOnly              1
time_stamping          hardware
tx_timestamp_timeout   20
logging_level          6
summary_interval       0

[ens1f1np1]
network_transport      L2
hybrid_e2e             0
```
`:wq` save and quit


```
sudo ptp4l -i ens1f1np1 -m -H -2 -s -f /etc/ptp4l.conf     # start ptp4l
```
<img width="751" height="224" alt="image" src="https://github.com/user-attachments/assets/0b6e0018-0369-4cc9-94e6-308efa75c3ea" />

start `ptp4l` successfully

- Run phc2sys
```
sudo phc2sys -w -m -s ens1f1np1 -R 8 -f /etc/ptp4l.conf
```

### Turn ptp4l/phc2sys into systemd service

1. Create or modify a systemd service

- **ptp4l**
```
sudo nano /etc/systemd/system/ptp4l.service
```
```
[Unit]
Description=Precision Time Protocol (PTP) service
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
EnvironmentFile=-/etc/default/ptp4l
ExecStart=/usr/sbin/ptp4l $OPTIONS

[Install]
WantedBy=multi-user.target
```

Configure parameters
```
sudo nano /etc/default/ptp4l
```
```
OPTIONS="-f /etc/ptp4l.conf -i ens1f1np1 -m -H"
```

- **phc2sys**
  
```
sudo nano /etc/systemd/system/phc2sys.service
```
```
[Unit]
Description=Synchronize system clock or PTP hardware clock (PHC)
After=ptp4l.service

[Service]
Type=simple
EnvironmentFile=-/etc/default/phc2sys
ExecStart=/usr/sbin/phc2sys $OPTIONS

[Install]
WantedBy=multi-user.target
```

Configure parameters
```
sudo nano /etc/default/phc2sys
```
```
OPTIONS="-a -r -r -n 24"
```

2. Reload systemd config
```
sudo systemctl daemon-reload
```

3. Start the configured services
```
sudo systemctl start ptp4l.service
sudo systemctl start phc2sys.service
```

4.Check the services state
```
sudo systemctl status ptp4l.service
sudo systemctl status phc2sys.service
```

5. Enable services to automatically restart them after reboot
```
sudo systemctl enable ptp4l.service
sudo systemctl enable phc2sys.service
```

6.**Issue - phc2sys fail or ptp4l**
If your *rms > 100 ms* or *phc offset > 100*, it is recommended to perform the following action – **Disable Network Time Protocol (NTP)**, because having both **PTP** and **NTP** enabled at the same time can result in two conflicting clocks, which may cause confusion or malfunction in ptp4l or phc2sys.

```
#Disable Network Time Protocol (NTP)
#to check there is NTP enabled or not
sudo timedatectl | grep NTP
// NTP service: active
#to disable
sudo timedatectl set-ntp false
```
Check after setting false
```
sudo timedatectl | grep NTP   
      NTP service: inactive
```

7.If PTP is already configured as a system service, use the following commands to check its status.
```
sudo journalctl -u ptp4l -f
sudo journalctl -u phc2sys -f
```

- **phcsys** RESULT
```
 八  04 15:46:33 ubuntu phc2sys[69201]: [269098.682] ens1f1np1 sys offset        -2 s2 freq   -7440 delay    549
 八  04 15:46:34 ubuntu phc2sys[69201]: [269099.684] ens1f1np1 sys offset        -6 s2 freq   -7445 delay    545
 八  04 15:46:35 ubuntu phc2sys[69201]: [269100.685] ens1f1np1 sys offset        -9 s2 freq   -7450 delay    539
 八  04 15:46:36 ubuntu phc2sys[69201]: [269101.686] ens1f1np1 sys offset        -3 s2 freq   -7446 delay    544
 八  04 15:46:37 ubuntu phc2sys[69201]: [269102.702] ens1f1np1 sys offset        -6 s2 freq   -7450 delay    549
 八  04 15:46:38 ubuntu phc2sys[69201]: [269103.703] ens1f1np1 sys offset        -9 s2 freq   -7455 delay    546
```

- **ptp4l** RESULT
```
 八  04 16:01:12 ubuntu ptp4l[68765]: ptp4l[269977.766]: rms    5 max    9 freq  -7401 +/-   5 delay    55 +/-   1
 八  04 16:01:12 ubuntu ptp4l[68765]: [269977.766] rms    5 max    9 freq  -7401 +/-   5 delay    55 +/-   1
 八  04 16:01:13 ubuntu ptp4l[68765]: ptp4l[269978.759]: rms    9 max   16 freq  -7426 +/-   7 delay    54 +/-   1
 八  04 16:01:13 ubuntu ptp4l[68765]: [269978.759] rms    9 max   16 freq  -7426 +/-   7 delay    54 +/-   1
 八  04 16:01:14 ubuntu ptp4l[68765]: ptp4l[269979.766]: rms    5 max    8 freq  -7409 +/-   5 delay    55 +/-   1
 八  04 16:01:14 ubuntu ptp4l[68765]: [269979.766] rms    5 max    8 freq  -7409 +/-   5 delay    55 +/-   1
```

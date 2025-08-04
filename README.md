# Components now need to be reinstalled
- Testmac + FlexRAN + xFAPI
-   [inish-script-fail](#11-inish-script-fail)
  [cvlsh-script-fail](#12-cvlsh-script-fail)

  -[gnb-ptp-fail](#13-issue--gnb-ptp-fail)


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
sudo ptp4l -i ens1f1np1 -m -H -2 -s -f /etc/ptp4l.conf     # start ptp41
```
<img width="751" height="224" alt="image" src="https://github.com/user-attachments/assets/0b6e0018-0369-4cc9-94e6-308efa75c3ea" />

start `ptp41` successfully

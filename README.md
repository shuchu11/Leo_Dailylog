# Components now need to be reinstalled

# Checkpoint

| Item                                                                                                   | Status             |
| ------------------------------------------------------------------------------------------------------ | ------------------ |
| Prerequisite for gNB : [inish-script-fail](#11-inish-script-fail) ,  [cvlsh-script-fail](#12-cvlsh-script-fail) | :heavy_check_mark: |
| gNB PTP synchronization  [gnb-ptp-fail](#13-issue--gnb-ptp-fail)                                       | :heavy_check_mark: |
| [FlexRAN ( Terminal 1 )](#14-flexran----terminal-1-)                                                   | :x:                |
| Testmac ( Terminal 2 )                                                                                 | :x:                |
| Check DU connection at RU side                                                                         | :x:                |
| Check RU connection at DU side                                                                         | :x:                |
| Cell Search Result ( Stage 1 ( TM500 + FlexRAN + Testmac ) )                                           | :x:                |
| FlexRAN ( Terminal 1 )                                                                                 | :x:                |
| xFAPI ( Terminal 2 )                                                                                   | :x:                |
| ric_stub ( Terminal 3 )                                                                                | :x:                |
| cu_stub ( Terminal 4 )                                                                                 | :x:                |
| OSC L2 ( Terminal 5 )                                                                                  | :x:                |



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

#### 6.**Issue - phc2sys fail or ptp4l**
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




### 1.4 FlexRAN   ( Terminal 1 )
```bash=
sudo su
cd /home/ubuntu/FlexRAN/l1/bin/nr5g/gnb/l1/
source /home/ubuntu/phy/setupenv.sh 
./l1.sh -xran
```

> [!Caution]
> ERROR LOG
> ```bash
> ubuntu@ubuntu:~/phy$ sudo su
> root@ubuntu:/home/ubuntu/phy# cd /home/ubuntu/FlexRAN/l1/bin/nr5g/gnb/l1/
> root@ubuntu:/home/ubuntu/FlexRAN/l1/bin/nr5g/gnb/l1# /home/ubuntu/phy/setupenv.sh 
> bash: /home/ubuntu/phy/setupenv.sh: Permission denied
> root@ubuntu:/home/ubuntu/FlexRAN/l1/bin/nr5g/gnb/l1# chmod +x /home/ubuntu/phy/setupenv.sh
> root@ubuntu:/home/ubuntu/FlexRAN/l1/bin/nr5g/gnb/l1# source /home/ubuntu/phy/setupenv.sh
> root@ubuntu:/home/ubuntu/FlexRAN/l1/bin/nr5g/gnb/l1# ./l1.sh -xran
> Radio mode with XRAN - Sub6 100Mhz
> ## ERROR: Please make sure environment variable RTE_SDK is set to valid DPDK path.
>        To fix, please do: export RTE_SDK=path_to_dpdk_folder    before running this script
> kernel.sched_rt_runtime_us = -1
> kernel.shmmax = 2147483648
> kernel.shmall = 2147483648
> using configuration file phycfg_xran.xml
> using configuration file xrancfg_sub6.xml
> >> Running... taskset -c 9,10 ./l1app --cfgfile=phycfg_xran.xml --xranfile=xrancfg_sub6.xml
> taskset: failed to execute ./l1app: Permission denied
> Cleanup after [PID] 81822
> ```
>
>  **Problem Conclusion**
>
> ```bash
> 1. RTE_SDK is not set
> 2. ' ./l1app ' does not have execution permission
>```

As shown in the log, let's first check the file related to the failed command `./l1.sh -xran`, which is `l1.sh`:
```
 ## ERROR: Please make sure environment variable RTE_SDK is set to valid DPDK path.
>        To fix, please do: export RTE_SDK=path_to_dpdk_folder    before running this script
```

- Below is a portion of the contents in `l1.sh`:


```
...

if [ "x"$1 = "x-xran" ]; then
    phycfg_xml_file="phycfg_xran.xml"
    xrancfg_xml_file="xrancfg_sub6.xml"
    echo "Radio mode with XRAN - Sub6 100Mhz"
    sudo ./dpdk.sh           <------------ The problem lies here.

...
```


- Below is the content of the **dpdk.sh** script:

```
...

if [ -z "$RTE_SDK" ]  # Check whether the `RTE_SDK` environment variable has been successfully set.

then
    echo "## ERROR: Please make sure environment variable RTE_SDK is set to valid DPDK path."
    echo "       To fix, please do: export RTE_SDK=path_to_dpdk_folder    before running this script"
    exit 1
fi

...
```
As shown in the image below, the system recognizes that the `RTE_SDK` environment variable is successfully set, but the `dpdk.sh` script detects `RTE_SDK` as an empty string.

<img width="865" height="47" alt="image" src="https://github.com/user-attachments/assets/74058461-f566-4978-91b7-f12d5dd64446" />

```
root@ubuntu:/home/ubuntu/FlexRAN/l1/bin/nr5g/gnb/l1# echo $RTE_SDK
/root/dpdk-stable-22.11.1
```

For convenience, directly write the relevant parameters into `dpdk.sh` (original parameter location: `setupenv.sh`).

```
export RTE_SDK=$DIR_ROOT/dpdk-stable-22.11.1
export RTE_TARGET=x86_64-native-linuxapp-icc
```

***After verifying everything is correct, run `l1.sh` again, but it seems that many files are still missing.
***  when deploying
```
ldconfig -p | grep dpdk #Verify whether the DPDK .so files have been recognized by the system.` 
```
system does not list `libdpdk.so` or related entries, it indicates that the configuration has failed.

So I decide to reinstall dpdk

#### Download DPDK ( Data Plane Development Kit ) dpdk-stable-20.11.9
- **remove dpdk-stable-22.11.1**
```
sudo rm -rf  dpdk-stable-22.11.1
```
  
- **install meson,ninja-build,pkg-config,libnuma-dev,python3-pyelftools**
```
sudo apt update
sudo apt install meson ninja-build pkg-config libnuma-dev python3-pyelftools  
```
- **unzip DPDK and enter the directory**
```
tar xvf dpdk-20.11.9.tar.xz
cd dpdk-stable-20.11.9
```
- **Use `Meson` to configure the build environment and enable `NUMA` support**
```
meson -Dnuma=true build
```
- **Compile DPDK**
```
ninja -C build #Compile DPDK 

# Install DPDK to the system
sudo ninja -C build install
sudo ldconfig
```

- **Check dpdk config**
```
sudo vi /etc/ld.so.conf.d/dpdk.conf
```
> Add the DPDK library path in this file.
> ```bash
> /usr/local/lib64
> ```

```
sudo ldconfig      #Update the cache
sudo ldconfig -v | grep rte_   #Verify whether the DPDK library is recognized by the system.
```

- **Verify that `pkg-config` can find DPDK**
```
pkg-config --libs libdpdk --static
```

> This will list the linker flags required to compile DPDK applications.      
> ```bash
> -Wl,--whole-archive -ldpdk -Wl,--no-whole-archive -pthread -lm
> ```


**以下是目前進度 ERROR LOG**
```
root@ubuntu:/home/ubuntu# cd /home/ubuntu/intel_sw/FlexRAN/l1/bin/nr5g/gnb/l1/
bash: cd: /home/ubuntu/intel_sw/FlexRAN/l1/bin/nr5g/gnb/l1/: No such file or directory
root@ubuntu:/home/ubuntu# cd /home/ubuntu/FlexRAN/l1/bin/nr5g/gnb/l1/
root@ubuntu:/home/ubuntu/FlexRAN/l1/bin/nr5g/gnb/l1# source /home/ubuntu/phy/setupenv.sh 
root@ubuntu:/home/ubuntu/FlexRAN/l1/bin/nr5g/gnb/l1# ./l1.sh -xran
Radio mode with XRAN - Sub6 100Mhz
## ERROR: Target does not have the DPDK UIO Kernel Module.
       To fix, please try to rebuild target.
Unloading any existing VFIO module
rmmod: ERROR: Module vfio_pci is in use
rmmod: ERROR: Module vfio_iommu_type1 is in use
rmmod: ERROR: Module vfio is in use by: vfio_pci_core vfio_iommu_type1 vfio_pci
Loading VFIO module
chmod /dev/vfio
OK
HOST
./dpdk.sh: line 142: /dpdk-stable-20.11.9/usertools/dpdk-devbind.py: No such file or directory
./dpdk.sh: line 145: /dpdk-stable-20.11.9/usertools/dpdk-devbind.py: No such file or directory
./dpdk.sh: line 146: /dpdk-stable-20.11.9/usertools/dpdk-devbind.py: No such file or directory
./dpdk.sh: line 147: /dpdk-stable-20.11.9/usertools/dpdk-devbind.py: No such file or directory
./dpdk.sh: line 148: /dpdk-stable-20.11.9/usertools/dpdk-devbind.py: No such file or directory
./dpdk.sh: line 149: /dpdk-stable-20.11.9/usertools/dpdk-devbind.py: No such file or directory
./dpdk.sh: line 150: /dpdk-stable-20.11.9/usertools/dpdk-devbind.py: No such file or directory
./dpdk.sh: line 151: /dpdk-stable-20.11.9/usertools/dpdk-devbind.py: No such file or directory
./dpdk.sh: line 152: /dpdk-stable-20.11.9/usertools/dpdk-devbind.py: No such file or directory
./dpdk.sh: line 154: /dpdk-stable-20.11.9/usertools/dpdk-devbind.py: No such file or directory
./dpdk.sh: line 155: /dpdk-stable-20.11.9/usertools/dpdk-devbind.py: No such file or directory
./dpdk.sh: line 156: /dpdk-stable-20.11.9/usertools/dpdk-devbind.py: No such file or directory
./dpdk.sh: line 157: /dpdk-stable-20.11.9/usertools/dpdk-devbind.py: No such file or directory
./dpdk.sh: line 158: /dpdk-stable-20.11.9/usertools/dpdk-devbind.py: No such file or directory
./dpdk.sh: line 159: /dpdk-stable-20.11.9/usertools/dpdk-devbind.py: No such file or directory
./dpdk.sh: line 160: /dpdk-stable-20.11.9/usertools/dpdk-devbind.py: No such file or directory
./dpdk.sh: line 161: /dpdk-stable-20.11.9/usertools/dpdk-devbind.py: No such file or directory
./dpdk.sh: line 171: /dpdk-stable-20.11.9/usertools/dpdk-devbind.py: No such file or directory
kernel.sched_rt_runtime_us = -1
kernel.shmmax = 2147483648
kernel.shmall = 2147483648
using configuration file phycfg_xran.xml
using configuration file xrancfg_sub6.xml
>> Running... taskset -c 9,10 ./l1app --cfgfile=phycfg_xran.xml --xranfile=xrancfg_sub6.xml
taskset: failed to execute ./l1app: Permission denied
Cleanup after [PID] 138386
root@ubuntu:/home/ubuntu/FlexRA
```

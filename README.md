# Leo_Dailylog

#### 2025.08.01

##### EMAIL to Kyle

Dear Kyle,

You can use WireGuard to connect to our server ( Attached is the VPN key ). If you're not sure how to use it, you can refer to the guide below.\
https://github.com/shuchu11/others/blob/c95473d33d94b1b1d241a4cb3bce219871b2a43b/wireGuard_VPN.md 

Below is the server information.\
      IP Address : 192.168.8.76\
      Username : ubuntu\
      Password : bmwlab\
      Root Password : bmwlab    \


Best Regards\
Leo





##### Start to test server : Testmac + FlexRAN + xFAPI
...
##### Testing the `ini.sh` script
```
cd
sudo su 
./ini.sh
exit
```
> [!Caution]
> 執行 ./ini.sh 時出現錯誤：這是因為 `ini.sh` 是用 Windows 編輯器（如 Notepad）編寫的，其中換行符號是 CRLF（也就是 ^M），但在 Linux 環境下，正確的換行符號應該是 LF。
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

###### Testing the `cvl.sh` script

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

Current status: Waiting for Intel to provide assistance. As mentioned on Slack, they will help us rebuild the environment.


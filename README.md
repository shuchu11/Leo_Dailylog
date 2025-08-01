# Leo_Dailylog

#### 2025.08.01
開始測試server : Testmac + FlexRAN + xFAPI



##### 測試 ini.sh 腳本
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
> **Solution** 使用以下方法將檔案轉換為 UNIX 格式
> ```bash
> sudo apt update
> sudo apt install dos2unix
> dos2unix ini.sh
> ```

缺少相關檔案，無法成功執行腳本，以下為 ERROR LOG
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

###### 測試 cvl.sh腳本

> [!Caution]
> 缺乏權限 。 以下為 ERROR LOG
> ```bash
> root@ubuntu:/home/ubuntu# ./cvl.sh
bash: ./cvl.sh: Permission denied
> ```
> 
>
>
> 


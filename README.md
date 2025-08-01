# Leo_Dailylog

#### 2025.08.01
開始測試server : Testmac + FlexRAN + xFAPI

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

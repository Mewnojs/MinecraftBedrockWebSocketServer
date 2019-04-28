import socket
import base64
import hashlib
import re
import threading
import struct
import time
import json
import uuid
from libprocessor import Trigger

class Task:
    def __init__(self):
        self.dealr=[]
        self.deale=[]

class mcWSS(Trigger):
    
    def __init__(self):
        super(Trigger,self).__init__()
        self.locks={}
        self.DELAY=0.1
        self.catchpack=False
        self.HOST = "0.0.0.0"#localhost
        self.PORT = 8080
        self.MAGIC_STRING = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
        self.HANDSHAKE_STRING = "HTTP/1.1 101 Switching Protocols\r\n" \
      "Upgrade:websocket\r\n" \
      "Connection: Upgrade\r\n" \
      "Sec-WebSocket-Accept: {1}\r\n" \
      "WebSocket-Location: ws://{2}/chat\r\n" \
      "WebSocket-Protocol:chat\r\n\r\n"
        self.data=[]
        self.bufsiz=2048
        self.task = Task
        self.inputs = []
        self.users = {}
        self.initsubs=["PlayerMessage"]
        self.initacts=["title @s subtitle §dCredit MnJS","title @s title §a§lHello §b§lWorld !","testfor @s"]
        self.respdict={}
        self.requests=[]
        self.taskdict={}
        
        
    def launch(self):
        # 创建基于tcp的服务器
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        addr = (self.HOST, self.PORT)
        self.serverSocket.bind(addr)
        self.serverSocket.listen(128)
        print("服务器运行，等待Minecraft连接...")
        # 调用监听
        self.handshake()

    def recv_data(self):
        """解码Minecraft发来的JSON数据
        前半段是Web socket通用的"""
        TDEBUG=False#Debug专用区域变量
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
                code_len = info[1] & 0x7f
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
                    extend_payload_len,mask,decoded = None,info[2:6],info[6:]                    
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
            i = token + i.encode()
            self.clientSocket.send(i)



    def handshake(self):
        while True:
            myhost=self.getHostIP() if self.HOST=="0.0.0.0" else self.HOST
            address=myhost+":"+str(self.PORT)
            print("Listening on:",address)
            print("Type command:\n\n/connect "+address)
            self.clientSocket, addressInfo = self.serverSocket.accept()
            print("get connected")
            request = self.clientSocket.recv(2048)
            print(request.decode())
            # 获取Sec-WebSocket-Key
            #ret = re.search(r"Sec-WebSocket-Key: (.*==)", str(request.decode()))
            ret = re.search(r"Sec-WebSocket-Key: (.*=)", str(request.decode()))
            if ret:
                key = ret.group(1)
            else:
                print(request)
                return
            Sec_WebSocket_Key = key + self.MAGIC_STRING
            print("key ", Sec_WebSocket_Key)
            # 将Sec-WebSocket-Key先进行sha1加密,转成二进制后在使用base64加密
            response_key = base64.b64encode(hashlib.sha1(bytes(Sec_WebSocket_Key, encoding="utf8")).digest())
            response_key_str = str(response_key)
            response_key_str = response_key_str[2:30]
            # print(response_key_str)
            # 构建websocket返回数据
            response = self.HANDSHAKE_STRING.replace("{1}", response_key_str).replace("{2}", self.HOST + ":" + str(self.PORT))
            self.clientSocket.send(response.encode())
            # print("send the hand shake data")
            self.task.wss_recv = threading.Thread(target = self.recv_data, args = ())
            self.task.wss_recv.start()
            self.task.wss_send = threading.Thread(target = self.send_data, args = ())
            self.task.wss_send.start()
            self.locks["trigger"] = threading.Condition()
            self.task.trigger = threading.Thread(target = self.trigger, args = ())
            self.task.trigger.start()
    import socket

    def getHostIP(self):
        """查询本机ip地址"""
        try:
            s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            s.connect(('8.8.8.8',80))
            ip=s.getsockname()[0]
        finally:
            s.close()

        return ip


if __name__ == '__main__':
    print(get_host_ip())

def main():
    WSS=mcWSS()
    WSS.launch()

if __name__ == "__main__":
    main()

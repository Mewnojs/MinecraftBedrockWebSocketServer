import socket
import base64
import hashlib
import re
import threading
import struct
import time
import json
import uuid
from libmcwscommon import mcWScommon,Task

class mcWSC(mcWScommon,Task):
    
    def __init__(self):
        
        self.HOST="localhost"
        self.PORT=8080
        self.bufsiz=2048
        self.key=b"imE6AOT1+gbq9zijPeR5Sg=="
        self.MAGIC_STRING =b'258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
        self.handshakedata=b"""GET // HTTP/1.1
Upgrade: websocket
Connection: Upgrade
Host: localhost:8080
Sec-WebSocket-Version: 13
Sec-WebSocket-Key: """+self.key
        self.task = Task
        self.data = []
        self.initsubs=[]
        self.initacts=[]
        self.locks={}
        
    def launch(self):
        # 创建基于tcp的服务器
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        addr = (self.HOST, self.PORT)
        self.clientSocket.connect(addr)
        #self.clientSocket.listen(128)
        print("客户端运行，等待WS服务器连接...")
        # 调用监听
        self.handshake()
        
        
    def handshake(self):
        #while True:
            myhost=self.getHostIP() if self.HOST=="0.0.0.0" else self.HOST
            address=myhost+":"+str(self.PORT)
            print("Listening on:",address)
            print("Type command:\n\n/connect "+address)
            print("get connected")
            self.clientSocket.send(self.handshakedata)
            request = self.clientSocket.recv(2048)
            print(request.decode())
            # 获取Sec-WebSocket-Key
            key=self.key
            Sec_WebSocket_Key = key + self.MAGIC_STRING
            print("key ", Sec_WebSocket_Key)
            # 将Sec-WebSocket-Key先进行sha1加密,转成二进制后在使用base64加密
            """response_key = base64.b64encode(hashlib.sha1(bytes(Sec_WebSocket_Key, encoding="utf8")).digest())
            response_key_str = str(response_key)
            response_key_str = response_key_str[2:30]
            # print(response_key_str)
            # 构建websocket返回数据
            response = self.HANDSHAKE_STRING.replace("{1}", response_key_str).replace("{2}", self.HOST + ":" + str(self.PORT))
            self.serverSocket.send(response.encode())"""
            # print("send the hand shake data")
            self.task.wss_recv = threading.Thread(target = self.recv_data, args = ())
            self.task.wss_recv.start()
            self.task.wss_send = threading.Thread(target = self.send_data, args = ())
            self.task.wss_send.start()
            self.locks["trigger"] = threading.Condition()
            self.task.trigger = threading.Thread(target = self.trigger, args = ())
            self.task.trigger.start()


def main():
    WSC=mcWSC()
    #WSC.HOST="192.168.1.92"
    WSC.launch()

if __name__ == "__main__":
    main()

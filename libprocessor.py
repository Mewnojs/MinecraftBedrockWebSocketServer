#libprocessor.py
import uuid
from libparser import funcparser
from time import sleep
import threading
import json
class Trigger:
    def __init__(self):
        self.inputs=[]
        self.catchpack=False
        self.DELAY=0.1
    def format(self,string):
        formatedstr='\\\"'.join('"'.join('"'.join("\\\\".join(string.split("\\")).split('“')).split('”')).split('"'))
        return formatedstr
    def command(self,command,rid):
        """整合命令（将被取缔）"""
        return '{"body":{"origin":{"type":"player"},"commandLine":"'+command+'","version":1},"header":{"requestId":"'+rid+'","messagePurpose":"commandRequest","version":1,"messageType":"commandRequest"}}'
    
    def sendcommand(self,*comm,response=True,rid=None):
        TDEBUG=False
        commtext=self.format(" ".join(comm))
        if response:
            if rid ==None:
                raise ValueError("No rid provised")
            self.requests.append(rid)
            data=self.command(commtext,rid=rid)
            if TDEBUG:print(data)
            self.data.append(data)
            self.taskdict[rid][1].acquire()
            self.taskdict[rid][1].wait()
            self.requests.remove(rid)
            resp=self.respdict[rid]
        else:
            rid=str(uuid.uuid4())
            resp=None
            data=self.command(commtext,rid)
            if TDEBUG:print(data)
            self.data.append(data)
        return resp
    def subscribe(self,term):
        data='{"body":{"eventName":"'+term+'"},"header":{"requestId":"'+str(uuid.uuid4())+'","messagePurpose":"subscribe","version":1,"messageType":"commandRequest"}}'
        #print(data)
        self.data.append(data)
        return 0
    def tellraw(self,sendto,text,*var):
        textformated=self.format(text)
        if not var:
            self.sendcommand("tellraw",sendto,'{"rawtext":[{"translate":"'+textformated+'"}]}',response=False)
        else:
            self.sendcommand("tellraw",sendto,'{"rawtext":[{"translate":"'+textformated+'","with":',str(list(var)),'}]}',response=False)
    def trigger(self):
        TDEBUG=False
        while True:
            self.locks["trigger"].acquire()
            if TDEBUG:print("WAITING:",self.inputs)
            if not len(self.inputs):
                self.locks["trigger"].wait()
            eventdata=self.inputs.pop(0) if self.inputs else None
            if not eventdata:continue
            """用于对包事件的处理，此为接收侧，self.data为输出区"""
            header=eventdata["header"] if "header" in eventdata else {}
            body=eventdata["body"] if "body" in eventdata else {}
            purpose=header["messagePurpose"] if "messagePurpose" in header else None
            if self.catchpack:
                print("'".join(str(eventdata).split('"')))
                    #self.data.append(command("say "+"'".join(str(eventdata).split('"'))))
            if purpose=="commandResponse":
                #threading.Thread(target = self.dealresponses, args = (body,header)).start()
                self.dealresponses(body,header)
            if purpose=="event":
                UUID=str(uuid.uuid4())
                if TDEBUG:print("====STARTING====:",UUID)
                self.taskdict[UUID] = [threading.Thread(target = self.dealevents, args = (body,header,UUID)),threading.Condition()]
                self.taskdict[UUID][0].start()
                if TDEBUG:print("====STARTED====:",UUID)
                #self.dealevents(body)
            #return 0
    def dealresponses(self,body,header):
        rid=header["requestId"]
        if rid in self.taskdict:
            self.respdict[rid] = body
            self.taskdict[rid][1].acquire()
            self.taskdict[rid][1].notify()
            self.taskdict[rid][1].release()
        else:
            print("\t@@untreated response:",body)
    def dealevents(self,body,header,rid):
        TDEBUG=False
        eventName=body["eventName"] if "eventName" in body else None
        if eventName=="PlayerMessage":
            properties=body["properties"] if "properties" in body else None
            MsgType=properties["MessageType"] if "MessageType" in properties else None
            Msg=properties["Message"]
            Msgd=Msg.split(" ")
            Sender=properties["Sender"]
            Receiver=properties["Receiver"] if "Receiver" in properties else None
            if MsgType == "chat":
                #udata = self.users[Sender] if Sender in self.users else {}
                #if not udata:self.users[Sender] = {}
                #status = udata["group"] if "group" in udata else "users"
                #if status == "operator":
                if 1:
                    if Msg == "@catch on":
                        self.tellraw(Sender,"§bStarted tracking mode.")
                        self.catchpack=True
                    elif Msg == "@catch off":
                        self.tellraw(Sender,"§bStopped tracking mode.")
                        self.catchpack=False
                    elif Msgd == "@debug.listtask":
                        print(self.taskdict)
                    elif Msgd[0] == "@tag" and Msgd[2] == "remove_all":
                        taglist=[]
                        re=self.sendcommand("tag",Msgd[1],"list",rid=rid)
                        if "：" in re["statusMessage"]:
                            taglist="".join("".join(re["statusMessage"][re["statusMessage"].index("：")+1:].split("§a")).split("§r")).split(",")
                        #self.tellraw(Sender,str(taglist))
                        if taglist:
                            for i in taglist:
                                self.tellraw(Sender,str(self.sendcommand("tag",Msgd[1],"remove",i,rid=rid)))
                            self.tellraw(Sender,"成功移除了 "+Msgd[1]+" 的 "+str(len(taglist))+" 个标签")
                        else:
                            self.tellraw(Sender,Msgd[1]+" 没有标签可供移除")
                    elif Msgd[0] =="@sub":
                        self.subscribe(" ".join(Msgd[1:]))
                    elif Msgd[0] =="@f":
                        with open(funcname,"r") as funcfile:
                            self.tellraw(Sender,"Successfully opened file "+funcname+":")
                            commands=funcparser(funcfile.read())
                            for c in commands:
                                self.sendcommand(c,response=False)
                        
                    elif Msg[0] == "@":
                        re = self.sendcommand(Msg[1:],rid=rid)
                        self.tellraw(Sender,str(re))
                        print("Command Response",re)
                #else:#users
                #    pass#unimplemented
                        
                print("<"+Sender+"> "+Msg)           
                #self.data.append(self.command("say ?"))
            elif MsgType == "say":
                print(Msg)
            elif MsgType == "title":
                print("Title from",Sender,"to",Receiver+":"+Msg) 
            elif MsgType == "tell":
                print("Whisper from",Sender,"to",Receiver+":"+Msg) 
        
        if TDEBUG:print("====FINISHED====:",rid)
        self.taskdict.pop(rid)
        return
        
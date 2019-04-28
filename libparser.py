#libparser.py
def funcparser(f):
    pass
class mcfParser:
    
    def __init__(self):
        self.replacedict={";":"\n"}
        self.keywords=list(self.replacedict.keys())+[]
        self.stringPool = []
        self.docPool = []
        self.jsonPool = []#unimplemented
    def putCode(self,code,linear=False):
        if linear:
            self.code = self.code + "\n" + code
        else:
            self.code = code
        
    def _handle_Replace(self,keyword,keyindex,char=None):
        if not char:
            char=self.replacedict[keyword]
        self.code = char.join(self.code.split(keyword))
    
    def _pre_process(self):
        code = self.code.split("\n")[1:]
        for lineIndex in range(len(code)):
            in_string=False
            in_brace=0
            charIndex=0
            string_headIndex=None
            brace_headIndex=None
            while 1:
                if charIndex >= len(code[lineIndex]):
                    break
                if not in_brace:
                    if not in_string:
                        if code[lineIndex][charIndex] == '"':
                            in_string = True
                            string_headIndex = charIndex
                        elif code[lineIndex][charIndex] == "#":
                            #print("@#")
                            offset = str(hex(len(self.docPool)))[::-1]
                            self.docPool.append(code[lineIndex][charIndex+1:])
                            code[lineIndex]=code[lineIndex][:charIndex]+"#d"+offset+"#"
                            break
                        elif code[lineIndex][charIndex:charIndex+2] == "//":
                            #print("@//")
                            code[lineIndex]=code[lineIndex][:charIndex]
                            break
                    elif code[lineIndex][charIndex] == '"':
                        in_string = False
                        offset = str(hex(len(self.stringPool)))[::-1]
                        self.stringPool.append(code[lineIndex][string_headIndex+1:charIndex])
                        code[lineIndex]=code[lineIndex][:string_headIndex]+"#s"+offset+"#"+code[lineIndex][charIndex+1:]
                        print(code)
                        charIndex = string_headIndex+2+len(offset)
                if code[lineIndex][charIndex] == "{" and not in_string:
                    if not in_brace:
                        brace_headIndex=charIndex
                    #print("@{")
                    in_brace += 1
                elif code[lineIndex][charIndex] == "}":
                    in_brace -= 1
                    if not in_brace:
                        offset = str(hex(len(self.jsonPool)))[::-1]
                        self.jsonPool.append(code[lineIndex][brace_headIndex+1:charIndex])
                        code[lineIndex]=code[lineIndex][:brace_headIndex]+"#j"+offset+"#"+code[lineIndex][charIndex+1:]
                        print(code)
                        charIndex = brace_headIndex+2+len(offset)

                charIndex += 1
        self.code = "\n".join(code)
        
        
    def _handle_simplereplace(self):
        for keyword in self.keywords:
            if keyword in self.code:
                keyindex = self.code.index(keyword)
                self._handle_Replace(keyword,keyindex)
        
    def handle(self):
        self._pre_process()
        
        self._handle_simplereplace()
        
"""parser=mcfParser()
parser.code=""
while 1:
    u=input(":")
    if u == ".":
        break
    parser.putCode(u,linear=True)
parser.handle()
for offset in parser.__dict__:
    print(offset+":"+str(parser.__dict__[offset]))"""
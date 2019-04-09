# coding:utf-8

# 本程序用于服务器练习
# 在 tcp 连接中，server 负责启动一个ip和端口，在这个端口监听，
# 当有 client 请求该监听端口时，开启一个新端口与 client 进行连接

# socket 启动监听的过程
# 1. create a socket
# 2. bind port
# 3. start listening
# 4. establish connection and keep listening

import socket
import threading
import re


class Reader(threading.Thread):
    def __init__(self, client):
        threading.Thread.__init__(self)
        self.client = client
        self.ENCODING = 'utf-8'
        self.BUFFERSIZE = 1024
        self.str = ""

    def getStr(self):
        return self.str

    def setStr(self, str):
        self.str = str

    def run(self):
        while True:
            data = self.client.recv(self.BUFFERSIZE)
            if data:
                str = bytes.decode(data, self.ENCODING)
                self.setStr(str=str)
            else:
                break
        print("close:", self.client.getpeername())


class Listener(threading.Thread):
    def __init__(self, ipAddr, port):
        threading.Thread.__init__(self)
        self.port = port
        self.ip = ipAddr
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM,
                                  0)  # AF_INET 表示用IPV4地址族，SOCK_STREAM 是说是要是用流式套接字 0 是指不指定协议类型，系统自动根据情况指定
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((ipAddr, port))
        self.sock.listen(0)  # 如何增加连接数量？
        self.ENCODING = 'utf-8'
        self.BUFFERSIZE = 1024

    # 重写父类 threading.Thread 的 run 方法
    def run(self):
        print("TCP SERVER start...")

        sentence = []
        # 读取英语900文本
        f = open('English900.txt', 'r')
        while 1:
            line = f.readline()
            if not line:
                break
            sentence.append(line)
        f.close()
        while True:
            # 接受客户端数据并响应
            print("waiting for connection")
            client, clientIpAddr = self.sock.accept()
            print('having a connection from {}'.format(clientIpAddr))
            reader = Reader(client=client)
            reader.start()
            reader.join()
            string = reader.getStr()
            print(string)
            string = string[9:]
            print(string)
            if not re.match('[^0-9,]', string):
                print("data format from client match successfully")
                numList = string.split(',')
                data = ''
                for item in numList:
                    if (int(item)-1) < len(sentence):
                        data = data + sentence[int(item)-1]
                byteswritten = 0
                if byteswritten < len(data):
                    startpos = byteswritten
                    endpos = min(byteswritten + self.BUFFERSIZE, len(data))
                    client.send(bytes(data[startpos:endpos], encoding=self.ENCODING))
            else:
                data = 'error in sent data format'
                client.send(bytes(data, encoding=self.ENCODING))

            # print('finish, close current client')
            # client.close()


if __name__ == '__main__':
    ipAddress = socket.gethostbyname(socket.gethostname()) # 默认将host作为ip地址
    print("host:{}".format(ipAddress))
    listener = Listener(ipAddr=ipAddress, port=12233)  # listener 类继承了 threading 类
    listener.start()

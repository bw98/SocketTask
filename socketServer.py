# coding=utf-8

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
from concurrent.futures import ThreadPoolExecutor


# 读取文件对象
class Sentence:
    sentence = []

    def __init__(self):
        self.my_sentence = []  # 需要读取多个文件对象时则实例化并使用 my_sentence

    @classmethod
    def getSentence(cls):
        return cls.sentence

    @classmethod
    def setSentenceByFile(cls, file_name='English900.txt'):
        # 读取英语900文本
        with open(file_name, 'r') as f:
            while True:
                line = f.readline()
                if not line:
                    break
                cls.sentence.append(line)

    def getMySentence(self):
        return self.my_sentence

    def setMySentence(self):
        return self.my_sentence


class Reader():

    def __init__(self, client, client_ip_addr):
        self.client = client
        self.client_ip_addr = client_ip_addr
        self.ENCODING = 'utf-8'
        self.buffersize = 1024
        self.str = ""

    def getStr(self):
        return self.str

    def setStr(self, string):
        self.str = string

    def run(self): 
        while True:
            data = self.client.recv(self.buffersize)
            print("【Reader】从客户端接受到的数据为:", data)
            if data:
                str = bytes.decode(data, self.ENCODING)
                self.setStr(string=str)
            else:
                break
        print("【Reader】 从 {} 接收到数据".format(self.client_ip_addr))
        string = self.getStr()
        string = string[9:]
        if not re.match('[^0-9,]', string):
            print("data format from client match successfully")
            num_list = string.split(',')
            send_data = ''
            sentence = Sentence.getSentence()  # 得到含文件ENglish900所有句子的对象
            for item in num_list:
                if (int(item) - 1) < len(sentence):
                    send_data = send_data + sentence[int(item) - 1]
            byteswritten = 0
            if byteswritten < len(send_data):
                start_pos = byteswritten
                end_pos = min(byteswritten + self.buffersize, len(send_data))
                self.client.send(bytes(send_data[start_pos:end_pos], encoding=self.ENCODING))
        else:
            send_data = 'error in sent data format'
            self.client.send(bytes(send_data, encoding=self.ENCODING))
        self.client.close()


class Listener:

    def __init__(self, ipAddr='127.0.0.1', port=12345):
        self.port = port
        self.ip = ipAddr
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM,
                                  0)  # AF_INET 表示用IPV4地址族，SOCK_STREAM 是说是要是用流式套接字 0 是指不指定协议类型，系统自动根据情况指定
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((ipAddr, port))
        self.sock.listen(10)  # WIN和MAC需要设置最大连接数量
        self.ENCODING = 'utf-8'
        self.BUFFERSIZE = 1024

    # 重写父类 threading.Thread 的 run 方法
    def run(self):
        print("TCP SERVER start...")
        print("host:{}, port:{}".format(self.ip, self.port))

        pool = ThreadPoolExecutor(10)  # 线程池最大线程数量

        # 接受客户端数据并响应
        while True:
            print("waiting for connection")
            client, client_ip_addr = self.sock.accept()  # 接受客户端请求之前保持阻塞
            reader = Reader(client, client_ip_addr)
            pool.submit(reader.run())


if __name__ == '__main__':
    server_addr = socket.gethostbyname(socket.gethostname())  # 将host作为服务器ip地址
    server_port = 12233
    Sentence.setSentenceByFile()  # 获取文件中的句子并初始化sentence类变量
    listener = Listener()  # listener 类继承了 threading 类
    listener.run()

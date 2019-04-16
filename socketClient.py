# coding=utf-8

# 客户端流程为：
# 1. 创建接口
# 2. 发起连接
#
# 注意：
# 创建接口参数同socket server相同
# 发起连接的函数为socket.connect(ip,port)
# ip与port为socket server端的ip和监听port。
import socket
import os
import fcntl
from socketServer import Sentence

BUFFERSIZE = 1024


def tcp_client_start(ipAddr='127.0.0.1', port=12345, data=''):
    if data == '':
        print('请输入要发送给服务器的信息，格式：sentence: 编号，编号')
        return

    # server port and ip
    server_ip = ipAddr
    server_port = port
    tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        tcp_client.connect((server_ip, server_port))
        print("connect server successfully")
        byteswritten = 0
        while byteswritten < len(data):
            startpos = byteswritten
            endpos = min(byteswritten + BUFFERSIZE, len(data))
            byteswritten += tcp_client.send(bytes(data[startpos:endpos], encoding="utf-8"))
            print("Wrote %d bytes\r" % byteswritten)
        tcp_client.shutdown(socket.SHUT_WR)  # 强制关闭客户端socket输出，解决短连接断开后发带空串socket的问题
        print("All data sent.")
        while True:
            buf = tcp_client.recv(BUFFERSIZE)
            buf = bytes.decode(buf, encoding='utf-8')
            if not len(buf):
                break
            print("服务器传回的数据为：{}".format(buf))  # 断开连接时服务器会传空串，如果写在if前则输出两次
            # 文件操作，多进程写入文件需要加锁
            fileName = 'client.txt'
            if not os.path.exists(fileName):
                with open(fileName, 'w') as f:
                    f.write(buf)
                    print('文件不存在，创建并写入文件成功')
            else:
                with open(fileName, 'a') as f:
                    Sentence.setSentenceByFile(file_name=fileName)
                    sentence = Sentence.getSentence()
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                    print('成功获取文件锁')
                    buf_to_list = buf.split(sep='\n')
                    for item in buf_to_list:
                        if (item + '\n') not in sentence:
                            f.write(item)
                        else:
                            print('句子' + item + ' 重复，写入失败')

    except Exception as e:
        print(e)


if __name__ == '__main__':
    server_ipAddr = '192.168.1.129'
    server_port = 12233
    send_data = "sentence:5,7,9"
    tcp_client_start(data=send_data)  # 需要知道server的ip和监听端口

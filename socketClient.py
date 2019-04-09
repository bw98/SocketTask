# coding:utf-8

# 客户端流程为：
# 1. 创建接口
# 2. 发起连接
#
# 注意：
# 创建接口参数同socket server相同
# 发起连接的函数为socket.connect(ip,port)
# ip与port为socket server端的ip和监听port。
import socket
import sys
import time

BUFFERSIZE = 1024


def tcp_client_start(ipAddr, port):
    # server port and ip
    server_ip = ipAddr
    server_port = port
    tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        tcp_client.connect((server_ip, server_port))
        print("connect server successfully")
        data = "sentence:1,2,3"
        byteswritten = 0
        while byteswritten < len(data):
            startpos = byteswritten
            endpos = min(byteswritten + BUFFERSIZE, len(data))
            byteswritten += tcp_client.send(bytes(data[startpos:endpos], encoding="utf-8"))
            sys.stdout.write("Wrote %d bytes\r" % byteswritten)
            sys.stdout.flush()
        tcp_client.shutdown(1)
        print("All data sent.")
        while 1:
            buf = tcp_client.recv(BUFFERSIZE)
            if not len(buf):
                break
            print("服务器传回的数据为：{}".format(buf))
            fileName = 'client(' + time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time())) + ').txt'
            f = open(fileName, 'a')
            f.write(bytes.decode(buf, encoding='utf-8'))
            f.close()

    except Exception as e:
        print(e)


if __name__ == '__main__':
    tcp_client_start(ipAddr='192.168.0.102', port=12233)  # 需要知道server的ip和监听端口

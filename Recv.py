import socket
import os
import time
import math
#发送方的ip
HOST = '172.22.43.202'   #发送方IP地址
PORT = 6070     #发送方端口号
BUFFER_SIZE = 1024 #缓冲区大小

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as c:
    c.connect((HOST,PORT))
    print('Connected with Server')
    while True:
        #接收文件名
        filename = c.recv(BUFFER_SIZE).decode('utf-8')
        #发送回执
        c.send("filename recved".encode('utf-8'))
        #接收文件大小
        try:
            filesize = c.recv(BUFFER_SIZE).decode('utf-8')
            filesize = int(filesize)
        except Exception as e:
            print("文件%s大小接收失败"%{filename},e)
        #发送回执
        c.send("filesize recved".encode('utf-8'))
        filename = os.path.basename(filename) #获取文件名（去除路径）
        while(os.path.exists(filename)):
            filename += '(1)'   #如果存在重名元素，后面加(1)
        with open(os.path.basename(filename),'wb') as f:     #保存文件
            while True:
                # print('begin waiting')
                data = c.recv(BUFFER_SIZE)
                # print('line:',data)
                if data[-1] == 4: #当接收到结束符号(ascii:04)结束接收
                    f.write(data[:-1])
                    break
                else:
                    f.write(data)
        try:
            if(os.path.getsize(filename) != filesize):
                print("文件%s未完全传输"%{filename})
            else:
                print("文件%s接收完毕"%{filename})
        except Exception as e:
            print(e)
        # 发送文件接收到回执
        c.send("file recved".encode('utf-8'))



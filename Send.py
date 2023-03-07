import socket
import time
import os
#函数定义
#传输文件函数
def transFile(filename):
    try:
        client_socket.send(filename.encode('utf-8'))
        #每次发送都接收对方的应答，防止对方接收缓存粘包
        print(client_socket.recv(BUFFER_SIZE).decode('utf-8')) #接收回执
        #得到文件大小
        file_size = os.path.getsize(filename)
        client_socket.send(str(file_size).encode('utf-8'))
        print(client_socket.recv(BUFFER_SIZE).decode('utf-8')) #接收回执
        with open(filename, 'rb') as f:
            data = f.read()
            client_socket.sendall(data + b'\x04')
            print('> 文件 '+ filename +'发送完成！')
    except Exception as e:
        print('文件传输失败：', e)
#倒计时函数
def timeLoop(t):
    print('倒计时开始')
    for i in range(t):
        print("                     ",end='\r')
        print('本次刷新剩余时间:',t - i,flush=True,end='\r')
        time.sleep(1)

#打印当前路径
print('当前路径为：',os.getcwd())
HOST = '0.0.0.0'  # 服务器IP地址
PORT = 6070  # 服务器端口号
BUFFER_SIZE = 1024  # 缓冲区大小

# 创建一个TCP套接字
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 绑定服务器地址和端口号
server_socket.bind((HOST, PORT))
# 监听客户端连接请求
server_socket.listen(1)

print('服务器正在运行...')

# 接受客户端连接
client_socket, client_address = server_socket.accept()
print('客户端连接成功:', client_address)


# 循环检查该目录下的文件
curList = set(os.listdir())
oldList = set()

# 打开文件并发送数据
while True:
    curList = set(os.listdir())
    #检查是否有新增文件
    if not curList == oldList:
        for file in curList:
            if not file in oldList and os.path.isfile(file):
                print('> 文件名：'+ file +'即将发送')
                transFile(file)
                #等待对方的回应
                response = client_socket.recv(BUFFER_SIZE).decode('utf-8')
                print(response)
    else:
        print('\n本轮无新增文件')
    oldList = curList
    timeLoop(15)
client_socket.close()
# 关闭连接
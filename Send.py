import socket
import time
import os

##该文件通过判断字节流末尾是否有结束符b'\x04'来判断文件是否传输结束
##接收文件时，发送方首先发送文件名，以供接收方保存文件。
## 然后发送方发送文件大小，以供接收方对比判断是否文件接受完整（也可以通过进行哈希码对比判断，但我没做hhh）
## 之前版本尝试过
#        1.无限死循环直到接收到空字节流，但是recv函数默认阻塞，只有在连接断开的时候，阻塞的recv会返回一个空字节流。
#           若想连续传多个文件而不打断socket连接，这种方法不能用简单的编程实现。
#        2.先传递文件大小，然后根据文件大小filesize与缓冲区大小BUFFER_SIZE计算出该文件需要传几次，确定好传递次数后，
#           使用for循环调用确定次数的传递。但该方法有个很严重的bug，即发送方使用sendall函数发送完全部的字节流后，接收方
#           使用recv函数接收时，每次接收到的字节流大小经常会达不到BUFFER_SIZE，而导致到达确定的次数后文件还有很多没有传递完。
#           猜测是因为接收方接收速度大于发送方发送的速度，导致缓冲区内还没填满就被调用的recv函数取走了。
#
##This file determines whether the file is finished transferring by determining whether
# there is an end character b'\x04' at the end of the byte stream
## When receiving a file, the sender first sends the file name for the receiver to save the file.
## Then the sender sends the size of the file for the receiver to compare and determine if the file is accepted in full
# (you can also compare and determine by hash code, but I didn't do it hhh)
## Previous versions have tried
#        1. infinite dead loop until receiving the empty byte stream,
#           but the recv function blocks by default, only when the connection is broken,
#           the blocking recv will return an empty byte stream.
#           If you want to pass multiple files in a row without breaking the socket connection,
#           this method cannot be implemented with simple programming.
#       2. First pass the file size, then calculate how many times the file needs to be passed
#           based on the file size filesize and buffer size BUFFER_SIZE, and after determining the number of passes
#           Use for loop call to determine the number of passes. But this method has a very serious bug,
#           that is, after the sender uses the sendall function to send the entire byte stream, the receiver
#           When using the recv function to receive, the size of the byte stream received each time often
#           does not reach BUFFER_SIZE, and the number of times the file has reached the determined number of passes is not finished.
#           Guess it is because the speed of receiving by the receiver is faster than the speed of sending by the sender,
#           resulting in the buffer being fetched by the recv function called before it is filled.
#

#传输文件函数/file transfering function
def transFile(filename):
    try:
        client_socket.send(filename.encode('utf-8'))
        #每次发送都接收对方的应答，防止对方接收缓存粘包
        # Receive an answer from the other side every time you send to prevent the other side from receiving cached sticky packets
        print(client_socket.recv(BUFFER_SIZE).decode('utf-8')) #接收回执/Receive a receipt
        #得到文件大小/Get the file size
        file_size = os.path.getsize(filename)
        client_socket.send(str(file_size).encode('utf-8'))
        print(client_socket.recv(BUFFER_SIZE).decode('utf-8')) #接收回执/Receive a receipt
        with open(filename, 'rb') as f:
            data = f.read()
            client_socket.sendall(data + b'\x04')
            print('> 文件 '+ filename +'发送完成！')
    except Exception as e:
        print('文件传输失败：', e)
#倒计时函数/Countdown function
def timeLoop(t):
    print('倒计时开始')
    for i in range(t):
        print("                     ",end='\r')
        print('本次刷新剩余时间:',t - i,flush=True,end='\r')
        time.sleep(1)

#打印当前路径/Print current path
print('当前路径为：',os.getcwd())
HOST = '0.0.0.0'  # 服务器IP地址/Server IP address
PORT = 6070  # 服务器端口号/Server port
BUFFER_SIZE = 1024  # 缓冲区大小/size of buffer

# 创建一个TCP套接字/create a tcp socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 绑定服务器地址和端口号/Bind server address and port number
server_socket.bind((HOST, PORT))
# 监听客户端连接请求/listen the connection request of client
server_socket.listen(1)

print('服务器正在运行...')

# 接受客户端连接/accpet the connetion request of client
client_socket, client_address = server_socket.accept()
print('客户端连接成功:', client_address)


# 循环检查该目录下的文件/Loop through the files in that directory
curList = set(os.listdir())
oldList = set()

# 打开文件并发送数据/open the file and send its content in type bytes
while True:
    curList = set(os.listdir())
    #检查是否有新增文件/Check for new files
    if not curList == oldList:
        for file in curList:
            if not file in oldList and os.path.isfile(file):
                print('> 文件名：'+ file +'即将发送')
                transFile(file)
                #等待对方的回应/Waiting for a response from the other side
                response = client_socket.recv(BUFFER_SIZE).decode('utf-8')
                print(response)
    else:
        print('\n本轮无新增文件')
    oldList = curList
    timeLoop(15)
# 关闭连接/close the connection
client_socket.close()

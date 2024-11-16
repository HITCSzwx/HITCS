import socket
import threading
import time

# 配置参数
SERVER_IP = "127.0.0.1"
SERVER_PORT = 12345
BUFFER_SIZE = 1024
WINDOW_SIZE = 4  # 窗口大小
SEQ_SIZE = 8  # 序列号范围

# 初始化 socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_IP, SERVER_PORT))

# 用于缓存已发送和已接收的数据
sent_data = {}  # 存储发送的数据包 {seq: data}
received_data = {}  # 存储接收的数据包 {seq: data}

# 用于记录 ACK 状态
acks = [False] * SEQ_SIZE

# 用于线程同步
lock = threading.Lock()

def send_data():
    """发送数据的线程函数"""
    seq = 0  # 当前发送的序列号
    while True:
        # 模拟数据发送
        data = f"Packet {seq}".encode()
        server_socket.sendto(data, (SERVER_IP, SERVER_PORT))
        with lock:
            sent_data[seq] = data
        print(f"[SEND] Packet {seq} sent")

        # 等待确认或者处理超时
        time.sleep(1)

        # 检查 ACK，如果未确认则重传
        with lock:
            if not acks[seq]:
                print(f"[RESEND] Packet {seq} not acknowledged, resending...")
            else:
                print(f"[ACKED] Packet {seq} acknowledged")

        seq = (seq + 1) % SEQ_SIZE  # 更新序列号

def receive_data():
    """接收数据的线程函数"""
    while True:
        data, addr = server_socket.recvfrom(BUFFER_SIZE)
        seq = int(data.decode().split()[-1])  # 从数据中提取序列号

        with lock:
            if not acks[seq]:  # 检查是否已经收到过该包
                received_data[seq] = data
                print(f"[RECEIVE] Packet {seq} received")
                acks[seq] = True  # 更新 ACK 状态

                # 发送 ACK
                ack = f"ACK {seq}".encode()
                server_socket.sendto(ack, addr)
                print(f"[SEND] ACK {seq}")

if __name__ == "__main__":
    print(f"Server started at {SERVER_IP}:{SERVER_PORT}")

    # 创建并启动发送和接收线程
    send_thread = threading.Thread(target=send_data)
    recv_thread = threading.Thread(target=receive_data)

    send_thread.start()
    recv_thread.start()

    send_thread.join()
    recv_thread.join()

import socket
from threading import Thread
import time

    

def connection_handler(conn, addr, conn_nbr):
    from_client = b''
    while True:
        data = conn.recv(4096)
        if not data: break
        from_client += data
        print(from_client)
        time.sleep(10)
        conn.send(b'I am SERVER\n')
    conn.close()
    print('Client ' + str(conn_nbr) + ' disconnected')

if __name__ == '__main__':
    conn_nbr = 0
    serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv.bind(('0.0.0.0', 8080))
    serv.listen(5)
    while True:
        conn, addr = serv.accept()
        conn_nbr += 1
        print("Client " + str(conn_nbr) + " connected.")
        handler = Thread(target=connection_handler, args=(conn, addr, conn_nbr))
        handler.start()
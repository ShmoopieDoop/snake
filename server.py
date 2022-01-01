import socket
import threading
import pickle

HEADER = 16
PORT = 5050
SERVER = "192.168.1.249"  # socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!disconnect"
GAME_MESSAGE = "!sending_game"
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(ADDR)


def handle_client(conn, addr, game):
    print(f"[NEW CONNECTION] {addr} connected")
    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                connected = False
            print(f"[{addr}] {msg}")
            conn.send("msg recieved".encode(FORMAT))
            conn.send(GAME_MESSAGE.encode(FORMAT))
            msg = pickle.dumps(game)
            conn.send(msg)
    conn.close()


def start(game):
    print("[STARTING] server is starting")
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr, game))
        thread.start()
        print(f"[ACTIVE CONNCTIONS] {threading.active_count() - 1}")

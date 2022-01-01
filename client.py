import socket
import pickle
import main

HEADER = 16
PORT = 5050
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!disconnect"
GAME_MESSAGE = "!sending_game"
GAME_REQUEST = "!requsting_game"
SERVER = "192.168.1.249"
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((ADDR))


def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b" " * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    msg = client.recv(2048).decode(FORMAT)
    if msg == GAME_MESSAGE:
        msg = client.recv(2048)
        game = pickle.loads(msg)
        grid, snake, score = game
        main.main(grid, snake, score)
    return msg

msg = send(GAME_REQUEST)
while msg != GAME_MESSAGE:
    msg = send(GAME_REQUEST)

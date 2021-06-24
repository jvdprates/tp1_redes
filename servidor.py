#!/usr/bin/env python3

import socket

HOST = 'localhost'
PORT = 3333

simpleSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
simpleSocket.bind((HOST,PORT))
simpleSocket.listen()

print("❗ Aguardando conexão de um cliente...")
connection, address = simpleSocket.accept()

print("✅ Conectado em", address)
while True:
    data = connection.recv(1024)
    if not data:
        print("Dados recebidos, fechando a conexão... 😴")
        connection.close()
        break
    print("📩 [Mensagem recebida]:", data.decode())
    connection.sendall(data)
    
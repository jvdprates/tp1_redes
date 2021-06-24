#!/usr/bin/env python3

import socket

HOST = '127.0.0.1'
PORT = 3333

print("❗ Programa iniciado!")
simpleSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
simpleSocket.connect((HOST,PORT))

print('✅ Conectado com sucesso ao servidor! enviando mensagem...')
simpleSocket.sendall(str.encode('Boa noite gente bonita!'))
data = simpleSocket.recv(1024)

print('💌 [Mensagem ecoada]:', data.decode())
print('Operação realizada com sucesso, fechando programa... 😴')
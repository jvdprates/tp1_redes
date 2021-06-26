import socket
import base64
import struct

HOST = 'localhost'
PORT = 50000

print("❗ Programa iniciado!")

skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
skt.bind((HOST, PORT))
skt.listen()
print("❗ Aguardando conexão de um cliente...")

connection, address = skt.accept()
print("✅ Conectado em", address)

while True:
    data = connection.recv(1024)
    print("📩 [Mensagem recebida]:", data)
    if not data:
        print("Dados recebidos, fechando a conexão... 😴")
        connection.close()
        break

    # Decodificando a mensagem em base16
    decodedData = base64.b16decode(data)
    print("⚙ [Mensagem decodificada]:", decodedData)

    # Unpack para regerar o tuple
    tupleMsg = struct.unpack("!2I2H2B10s", decodedData)
    print("⚙ [Mensagem desempacotada]:", tupleMsg)

    for i in tupleMsg:
        print(i, " - ", type(i))

    # Verificar os bytes de sincronização
    if not (hex(tupleMsg[0]) == 0xdcc023c2):
        print(hex(tupleMsg[0]))
        print("Primeiro campo inválido")
        connection.close()
        break

    # # Ecoando a mensagem decodificada para o cliente
    # print("📩 Ecoando para o cliente...")
    # connection.sendall(unpackedMsg)

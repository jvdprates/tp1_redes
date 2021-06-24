import socket
import base64

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
    if not data:
        print("Dados recebidos, fechando a conexão... 😴")
        connection.close()
        break
    print("📩 [Mensagem recebida]:", data.decode('UTF-8'))

    # Decodificando a mensagem em base16
    data = base64.b16decode(data)
    print("⚙ [Mensagem decodificada]:", data)

    # Ecoando a mensagem decodificada para o cliente
    print("📩 Ecoando para o cliente...")
    connection.sendall(data)

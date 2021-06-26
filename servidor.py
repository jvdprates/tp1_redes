import socket
import base64
import struct

HOST = 'localhost'
PORT = 50000

SYNC_CODE = 0xDCC023C2

print("❗ Programa iniciado!")

skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
skt.bind((HOST, PORT))
skt.listen()
print("❗ Aguardando conexão de um cliente...")

connection, address = skt.accept()
print("✅ Conectado em", address)

def validateSync(decodedTuple):
    sync1 = decodedTuple[0]
    sync2 = decodedTuple[1]
    print("Validação:", sync1, SYNC_CODE)

    if sync1 == sync2 and sync1 == SYNC_CODE:
        return True
    else:
        return False

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
    print("type(decodedData):", type(decodedData))

    # Unpack para regerar o tuple
    tupleMsg = struct.unpack("!2I2H2Bs", decodedData)
    print("⚙ [Mensagem desempacotada]:", tupleMsg)

    for i in tupleMsg:
        print(i, " - ", type(i))
    
    syncValidation = validateSync(tupleMsg)
    if syncValidation:
        packageId = tupleMsg[4]
        packageData = tupleMsg[6]
        
        packedMsg = struct.pack("!2I2H2Bs", SYNC_CODE, SYNC_CODE,
                       0, 0, packageId, 7, b'')        
        # Ecoando a mensagem decodificada para o cliente
        print("📩 Ecoando para o cliente...")
        connection.send(packedMsg)
    else:
        print("Erro de validação, fechando a conexão... 😴")
        connection.close()
        break
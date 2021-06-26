import socket
import base64
import struct
import sys
import utils

HOST = 'localhost'
PORT = 50000

SYNC_CODE = 0xDCC023C2
ACK_CODE = 7
PACK_SIZE = 15

print("❗ Programa iniciado!")
skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
skt.bind((HOST, PORT))
skt.listen()
print("❗ Aguardando conexão de um cliente...")

connection, address = skt.accept()
print("✅ Conectado em", address)

dataBuffer = bytearray()
while True:
    data = connection.recv(1024)
    print("📩 [Mensagem recebida]:", data)
    if not data:
        utils.messageClose(connection, 'Nenhum dado a mais foi recebido')
        print("Mensagem completa:", dataBuffer.decode("UTF-8"))
        break

    # Decodificando a mensagem em base16
    decodedData = base64.b16decode(data)
    print("⚙ [Mensagem decodificada]:", decodedData)
    print("type(decodedData):", type(decodedData))

    # Unpack para regerar o tuple
    tupleMsg = struct.unpack("!2I2H2Bs", decodedData)
    print("⚙ [Mensagem desempacotada]:", tupleMsg)
    
    syncValidation = utils.validateSync(tupleMsg)
    checkSumValidation = utils.validateSum(tupleMsg, data)
    if syncValidation and checkSumValidation:
        # Preparando echo de confirmação de recebimento para ser enviado ao cliente
        packageId = tupleMsg[4]
        packageData = tupleMsg[6]
        
        # Adiciona o dado recebido ao buffer
        print("type(packageData)", type(packageData))
        dataBuffer += packageData

        packedMsg = struct.pack("!2I2H2Bs", SYNC_CODE, SYNC_CODE,
                       PACK_SIZE, 0, packageId, ACK_CODE, b'')        

        # Codificando o retorno do cliente
        codedPack = base64.b16encode(packedMsg) 

        # Ecoando a mensagem decodificada para o cliente
        print("📩 Ecoando para o cliente...")
        connection.send(codedPack)
    else:
        if not checkSumValidation:
            utils.messageClose(connection, 'Erro de checksum')
        if not syncValidation:
            utils.messageClose(connection, 'Erro de validação de sincronização')
        break
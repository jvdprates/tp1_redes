import socket
import base64
import struct
import sys

import utils

HOST = '127.0.0.1'
PORT = 50000

SYNC_CODE = 0xDCC023C2
ACK_CODE = 7
PACK_SIZE = 15

print("❗ Programa iniciado!")
skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
skt.connect((HOST, PORT))
print('✅ Conectado com sucesso ao servidor!')


class Frame:
    def __init__(self, sync1, sync2, length, checksum, _id, flags, data):
        self.sync1 = sync1
        self.sync2 = sync2
        self.length = length
        self.checksum = checksum
        self._id = _id
        self.flags = flags
        self.data = data


inputMsg = input("❗ Digite uma mensagem: ")
print("inputMsg:", inputMsg)
print("type(inputMsg):", type(inputMsg))

# Criando uma classe do tipo Frame e instaciando suas variaveis
frame = Frame(SYNC_CODE, SYNC_CODE, PACK_SIZE,
              0, 0, 0, inputMsg.encode("UTF-8"))

print("frame.data:", frame.data)
print("type(frame.data):", type(frame.data))

message = bytearray(frame.data)

for byte in message:
    byte = byte.to_bytes(1, sys.byteorder)
    # Empacotando a mensagem de acordo com o tamanho de cada quadro
    print("byte:", byte)
    print("type(byte):", type(byte))
    packedMsg = struct.pack("!2I2H2Bs", frame.sync1, frame.sync2,
                            frame.length, frame.checksum, frame._id, frame.flags, byte)
    print("⚙ [Mensagem empacotada]:", packedMsg)

    checkedMsg = utils.createChecked(packedMsg)
    print("⚙ [Mensagem com checksum]:", checkedMsg)

    # Codificando o enquadramento para base16
    codedPack = base64.b16encode(checkedMsg)
    print("⚙ [Mensagem enquadrada]:", codedPack)

    # Enviando mensagem codificada para o servidor
    skt.send(codedPack)

    while True:
        skt.settimeout(5.0)
        try:
            serverEcho = skt.recv(1024)
            break
        except:
            print("❗ Não recebi eco a tempo, reenviando pacote...")
            skt.send(codedPack)

    # Recebendo um eco do servidor
    print('💌 [Mensagem ecoada]:', serverEcho)

    # Decodificando eco do servidor
    decodedServerEcho = base64.b16decode(serverEcho)
    print('💌 [Eco decodificado]:', decodedServerEcho)

    # Unpack do eco do servidor
    tupleEcho = struct.unpack("!2I2H2Bs", decodedServerEcho)
    print("⚙ [Eco desempacotado]:", tupleEcho)

    # Validação de sincronização do eco do servidor
    syncEchoValid = utils.validateSync(tupleEcho)
    # Validação de confirmação de recebimento de pacote correto
    echoIdValid = utils.validateEcho(frame._id, tupleEcho)
    # Validação de tamanho do pack do eco
    lengthValid = utils.validateLength(tupleEcho, decodedServerEcho)
    if syncEchoValid and echoIdValid and lengthValid:
        # Muda o ID para o do próximo pacote
        frame._id = utils.changeId(frame._id)
        # Segue o loop, preparando para enviar próximo pacote
    else:
        if not syncEchoValid:
            utils.messageClose(skt, "Erro de validação de sincronização")
        if not echoIdValid:
            utils.messageClose(skt, "Erro de confirmação do servidor")
        if not lengthValid:
            utils.messageClose(
                skt, "Erro de validação de tamanho do eco do servidor")
        break

utils.messageClose(skt, "Operação realizada com sucesso")

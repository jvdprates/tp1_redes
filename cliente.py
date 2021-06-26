import socket
import base64
import struct
import sys

HOST = '127.0.0.1'
PORT = 50000

SYNC_CODE = 0xDCC023C2

def changeId(id):
    if id == 0:
        return 1
    else:
        return 0

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
frame = Frame(SYNC_CODE, SYNC_CODE, len(inputMsg),
              0, 0, 0, inputMsg.encode("UTF-8"))

print("frame.data:", frame.data)
print("type(frame.data):", type(frame.data))

message = bytearray(frame.data)

for byte in message:
    byte = byte.to_bytes(1, sys.byteorder)
    # Empacotando a mensagem de acordo com o tamanho de cada quadro
    print("byte:", byte)
    print("type(byte):", type(byte))
    frame.length = sys.getsizeof(byte)
    print("frame.length", frame.length)
    packedMsg = struct.pack("!2I2H2Bs", frame.sync1, frame.sync2,
                       frame.length, frame.checksum, frame._id, frame.flags, byte)
    frame._id = changeId(frame._id)
    print("⚙ [Mensagem empacotada]:", packedMsg)

    # Codificando o enquadramento para base16
    codedPack = base64.b16encode(packedMsg)
    print("⚙ [Mensagem enquadrada]:", codedPack)

    # Enviando mensagem codificada para o servidor
    skt.send(codedPack)

    # Recebendo um eco do servidor
    data = skt.recv(1024)
    print('💌 [Mensagem ecoada]:', data)

print('Operação realizada com sucesso, fechando programa... 😴')

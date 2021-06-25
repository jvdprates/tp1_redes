import socket
import base64
import struct

HOST = '127.0.0.1'
PORT = 50000

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
frame = Frame(0xDCC023C2, 0xDCC023C2, len(inputMsg),
              0, 0, 0, inputMsg.encode("UTF-8"))
print("frame.data:", frame.data)
print("type(frame.data):", type(frame.data))

# longString = frame.sync1 + frame.sync2 + frame.length + frame.checksum + frame._id + frame.flags + frame.data
# print("longString:", longString)
# print("type(longString):", type(longString))

# Empacotando a mensagem de acordo com o tamanho de cada quadro
packedMsg = struct.pack("!IIHHBBI", frame.sync1, frame.sync2,
                        frame.length, frame.checksum, frame._id, frame.flags, int.from_bytes(frame.data, "big"))

for i in packedMsg:
    print(i, " - ", type(i))

print("⚙ [Mensagem empacotada]:", packedMsg)
print(packedMsg[6])
print(type(packedMsg[6]))

# Codificando o enquadramento para base16
codedPack = base64.b16encode(packedMsg)
print("⚙ [Mensagem enquadrada]:", codedPack)

# Enviando mensagem codificada para o servidor
skt.sendall(codedPack)

# Recebendo um eco do servidor
data = skt.recv(1024)
print('💌 [Mensagem ecoada]:', data)

print('Operação realizada com sucesso, fechando programa... 😴')

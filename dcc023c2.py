import socket
import base64
import struct
import sys

# Argumentos de chamada do programa
ARGS = sys.argv

# Tratativa para a inexistência de argumentos de chamada
if len(sys.argv) > 1:
    PROGRAM = sys.argv[1]
else:
    PROGRAM = 'null'

# Função que imprime o erro de chamada e explica a utilização correta
def printInputError(program):
    if program == 1:
        print("❗ Erro de chamada do servidor")
        print("[Uilização correta]:", "./dcc023c2 -s <port> <input_name> <output_name>")
    elif program == 2:
        print("❗ Erro de chamada do cliente")
        print("[Uilização correta]:", "./dcc023c2 -c 127.0.0.1 <port> <input_name> <output_name>")
    else:
        print("❗ Erro de chamada genérico")
        print("[Uilização correta]:", "./dcc023c2 <-c/-s> ...")

# Tratativa para os argumentos de chamada do programa
if (PROGRAM != '-c') and (PROGRAM != '-s'):
    printInputError(0)
    PROGRAM = 'null'
elif (PROGRAM == '-s'):
    if len(ARGS) != 5:
        printInputError(1)
        PROGRAM = 'null'
else:
    if len(ARGS) != 6:
        printInputError(2)
        PROGRAM = 'null'

# Codigo de sincronização
SYNC_CODE = 0xDCC023C2
# Tamanho de uma pack 
PACK_SIZE = 15
# Codigo de ACK de confirmação
ACK_CODE = 7

# Retorna o novo ID para o próximo pacote
def changeId(id):
    if id == 0:
        return 1
    else:
        return 0

# Mensagem de erro genérica, que fecha a conexão
def messageClose(socketConnection, message):
    print("{}, fechando a conexão... 😴".format(message))
    socketConnection.close()

# Validação de sincronização no pacote
def validateSync(decodedTuple):
    sync1 = decodedTuple[0]
    sync2 = decodedTuple[1]
    if sync1 == sync2 and sync1 == SYNC_CODE:
        return True
    else:
        return False

# Validação de tamanho do pacote
def validateLength(decodedTuple, receivedPack):
    tupleLength = decodedTuple[2]
    if tupleLength == len(receivedPack):
        return True
    else:
        return False

# Validação do ID do eco de confirmação
def validateEcho(currentId, decodedTuple):
    _id = decodedTuple[4]
    flag = decodedTuple[5]
    if currentId == _id and flag == ACK_CODE:
        return True
    else:
        return False

# Validação de checkSum
def validateSum(receivedPack):
    currentSum = calculateCheckSum(receivedPack)
    if currentSum == 0:
        return True
    else:
        return False

# Cálculo de checkSum para um pacote
def calculateCheckSum(packedMsg):
    hexPackedMsg = packedMsg.hex()
    currSum = 0
    for i in range(0, len(hexPackedMsg), 4):
        currSum += int(hexPackedMsg[i:i+4], 16)
        if len(hex(currSum)) > 6:
            currSum = (int(hex(currSum)[2], 16) + int(hex(currSum)[3:], 16))
    return currSum ^ 0xFFFF

# Criar um novo pacote com o checkSum
def createChecked(packedMsg):
    unpacked = struct.unpack("!2I2H2Bs", packedMsg)
    checkSum = calculateCheckSum(packedMsg)
    newPack = struct.pack("!2I2H2Bs", unpacked[0], unpacked[1], unpacked[2],
                          checkSum, unpacked[4], unpacked[5], unpacked[6])
    return newPack

# Inicializar Servidor
if(PROGRAM == '-s'):
    print("❗ Servidor iniciado")
    HOST = 'localhost'
    PORT = int(sys.argv[2])
    OUTPUT = sys.argv[4]

    skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    skt.bind((HOST, PORT))
    skt.listen()
    print("😴 Aguardando conexão de um cliente...")

    connection, address = skt.accept()
    print("✅ Conectado em", address)

    dataBuffer = bytearray()
    while True:
        data = connection.recv(1024)
        print("📩 [Mensagem recebida]:", data)
        if not data:
            messageClose(connection, '❗ Mensagem chegou ao fim')
            outputFile = open(f'{OUTPUT}.txt', "w")
            outputFile.write(dataBuffer.decode("UTF-8"))
            print("✅ Arquivo de output foi atualizado")
            outputFile.close()
            break

        # Decodificando a mensagem em base16
        decodedData = base64.b16decode(data)
        print("⚙ [Mensagem decodificada]:", decodedData)

        # Unpack para regerar o tuple
        tupleMsg = struct.unpack("!2I2H2Bs", decodedData)
        print("⚙ [Mensagem desempacotada]:", tupleMsg)

        # Validação de sincronização
        syncValid = validateSync(tupleMsg)
        # Validação de checksum
        checkSumValid = validateSum(decodedData)
        # Validação de tamanho do pack
        lengthValid = validateLength(tupleMsg, decodedData)
        if syncValid and checkSumValid and lengthValid:
            # Preparando echo de confirmação de recebimento para ser enviado ao cliente
            packageId = tupleMsg[4]
            packageData = tupleMsg[6]

            # Adiciona o dado recebido ao buffer
            dataBuffer += packageData

            packedMsg = struct.pack("!2I2H2Bs", SYNC_CODE, SYNC_CODE,
                                    PACK_SIZE, 0, packageId, ACK_CODE, b'')

            # Codificando o retorno do cliente
            codedPack = base64.b16encode(packedMsg)

            # Ecoando a mensagem decodificada para o cliente
            print("📩 Ecoando pack de confirmação para o cliente...")
            connection.send(codedPack)
        else:
            if not checkSumValid:
                messageClose(connection, 'Erro de checksum')
            if not syncValid:
                messageClose(
                    connection, 'Erro de validação de sincronização')
            if not lengthValid:
                messageClose(
                    connection, 'Erro de validação de tamanho de pacote')
            break

# Inicializar cliente
elif(PROGRAM == '-c'):
    print("❗ Cliente iniciado")
    HOST = sys.argv[2]
    PORT = int(sys.argv[3])
    INPUT = sys.argv[4]

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

    print("✅ Arquivo encontrado com sucesso")
    with open(f'{INPUT}.txt') as inputFile:
        inputMsg = inputFile.read()
    print("✅ Arquivo lido com sucesso")
    inputFile.close()

    # Criando uma classe do tipo Frame e instaciando suas variaveis
    frame = Frame(SYNC_CODE, SYNC_CODE, PACK_SIZE,
                  0, 0, 0, inputMsg.encode("UTF-8"))
    message = bytearray(frame.data)

    # Enviar um pacote para cada byte da mensagem
    for byte in message:
        byte = byte.to_bytes(1, sys.byteorder)
        
        # Empacotando a mensagem de acordo com o tamanho de cada quadro
        print("byte:", byte)
        print("type(byte):", type(byte))
        packedMsg = struct.pack("!2I2H2Bs", frame.sync1, frame.sync2,
                                frame.length, frame.checksum, frame._id, frame.flags, byte)
        print("⚙ [Mensagem empacotada]:", packedMsg)

        checkedMsg = createChecked(packedMsg)
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
        syncEchoValid = validateSync(tupleEcho)
        # Validação de confirmação de recebimento de pacote correto
        echoIdValid = validateEcho(frame._id, tupleEcho)
        # Validação de tamanho do pack do eco
        lengthValid = validateLength(tupleEcho, decodedServerEcho)
        if syncEchoValid and echoIdValid and lengthValid:
            # Muda o ID para o do próximo pacote
            frame._id = changeId(frame._id)
            # Segue o loop, preparando para enviar próximo pacote
        else:
            if not syncEchoValid:
                messageClose(skt, "Erro de validação de sincronização")
            if not echoIdValid:
                messageClose(skt, "Erro de confirmação do servidor")
            if not lengthValid:
                messageClose(
                    skt, "Erro de validação de tamanho do eco do servidor")
            break

    messageClose(skt, "Operação realizada com sucesso")

else:
    print("Finalizando programa... 😴")

import socket
import base64
import struct
import sys

SYNC_CODE = 0xDCC023C2
ACK_CODE = 7
PACK_SIZE = 15

def changeId(id):
    if id == 0:
        return 1
    else:
        return 0

def messageClose(socketConnection, message):
    print("{}, fechando a conexão... 😴".format(message))
    socketConnection.close()

def validateSync(decodedTuple):
    sync1 = decodedTuple[0]
    sync2 = decodedTuple[1]
    print("Validação:", sync1, SYNC_CODE)

    if sync1 == sync2 and sync1 == SYNC_CODE:
        print("✅ Sucesso!")
        return True
    else:
        print("❗ Falha!")
        return False

def validateSum(decodedTuple, receivedPack):
    checkSum = decodedTuple[3]
    print("Validação:", checkSum, len(receivedPack))

    if checkSum and len(receivedPack):
        print("✅ Sucesso!")
        return True
    else:
        print("❗ Falha!")
        return False

def validateEcho(currentId, decodedTuple):
    _id = decodedTuple[4]
    flag = decodedTuple[5]

    print("Validação:", _id, currentId, flag, ACK_CODE)
    if currentId == _id and flag == ACK_CODE:
        print("✅ Sucesso!")
        return True
    else:
        print("❗ Falha!")
        return False
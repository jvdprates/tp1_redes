import base64
import struct

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


def validateLength(decodedTuple, receivedPack):
    tupleLength = decodedTuple[2]
    print("receivedPack", receivedPack.hex())
    print("Validação:", tupleLength, len(receivedPack))
    if tupleLength == len(receivedPack):
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


def validateSum(receivedPack):
    currentSum = calculateCheckSum(receivedPack)

    print("Validação:", currentSum)
    if currentSum == 0:
        print("✅ Sucesso!")
        return True
    else:
        print("❗ Falha!")
        return False


def calculateCheckSum(packedMsg):
    print("packedMsg", packedMsg)
    hexPackedMsg = packedMsg.hex()
    print("hexPackedMsg", hexPackedMsg)

    currSum = 0
    for i in range(0, len(hexPackedMsg), 4):
        currSum += int(hexPackedMsg[i:i+4], 16)
        if len(hex(currSum)) > 6:
            currSum = (int(hex(currSum)[2], 16) + int(hex(currSum)[3:], 16))
    return currSum ^ 0xFFFF


def createChecked(packedMsg):
    unpacked = struct.unpack("!2I2H2Bs", packedMsg)
    checkSum = calculateCheckSum(packedMsg)
    newPack = struct.pack("!2I2H2Bs", unpacked[0], unpacked[1], unpacked[2],
                          checkSum, unpacked[4], unpacked[5], unpacked[6])
    print("newPack", newPack)
    newUnpacked = struct.unpack("!2I2H2Bs", newPack)
    print("newUnpacked", newUnpacked)
    return newPack

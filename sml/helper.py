# -*- encoding: utf-8 -*-


def cutByte(toCut):
    if type(toCut) == str:
        toCut = ord(toCut)

    try:
        leftpart = toCut >> 4 & 0x0F
    except Exception as e:
        print(e)
    try:
        rightpart = toCut & 0x0F
    except Exception as e:
        print(e)
    # test1 = 0x76
    # test2 = test1 >> 4
    # test3 = test2 << 4
    # test4 = test1 - test3
    # print(test1)
    # print(test2)
    # print(test4)
    return (leftpart, rightpart)


def DataTypeandLength(data):
    # type: (object) -> object
    if len(data) > 1:
        return ("Datenlaenge: {}".format(len(data)))
    if len(data) < 1:
        return
    more = False
    dTypeN = {0: "OctetString", "1": "was zum....", 4: "Bool", 5: "Integer", 6: "UInt", 7: "List of"}
    dTypeName = "none"
    dType, dLen = cutByte(data)
    if dType & 8:
        more = True
        dType = dType - 8
    try:
        dTypeName = dTypeN[dType]
    except:
        print(dType)
        dTypename = "unknown"
    return (dTypeName, dLen, more)


def getTLData(data):
    typus, len = cutByte(data[0])
    if typus == 0:
        if len > 1:
            OctetString = data[1:len - 1]
            return (OctetString, len - 1)
    if typus == 0x52:            #Int8
        return (data[1:2], 1)
    if typus == 0x53:            #Int16
        return (data[1:3], 2)
    if typus == 0x55:            #Int32
        return (data[1:4], 4)
    if typus == 0x59:            #Int64
        return (data[1:8], 8)
    if typus == 0x62:            #Uint8
        return (data[1:2], 1)
    if typus == 0x63:            #Uint16
        return (data[1:3], 2)
    if typus == 0x65:            #Uint32
        return (data[1:4], 4)
    if typus == 0x69:            #Uint64
        return (data[1:8], 8)
    if typus == 0x42:           #Bool
        return(data[1], 1)
    if typus == 0x7:            #List of
        return(len, 0)
    return ("", -1)


def ByteToHex(byteStr):
    """
    Convert a byte string to it's hex string representation e.g. for output.
    """
    if type(byteStr) == list:
        return  ''.join(str(x) for x in byteStr)
    if type(byteStr) == int:
        return '0x{:02x}'.format(byteStr)
    try:
        return ''.join(["%02X " % ord(x) for x in byteStr]).strip()
    except:
        return byteStr

def HexToByte(hexStr):
    """
    Convert a string hex byte values into a byte string. The Hex Byte values may
    or may not be space separated.
    """
    bytes = []
    hexStr = ''.join(hexStr.split(" "))
    for i in range(0, len(hexStr), 2):
        bytes.append(chr(int(hexStr[i:i + 2], 16)))
    return ''.join(bytes)

def crc16(data):
    """ CRC-16-CCITT Algorithm """
    data = bytearray(data)
    poly = 0x8408
    crc = 0xFFFF
    for b in data:
        cur_byte = 0xFF & b
        for _ in range(0, 8):
            if (crc & 0x0001) ^ (cur_byte & 0x0001):
                crc = (crc >> 1) ^ poly
            else:
                crc >>= 1

            cur_byte >>= 1
    crc = (~crc & 0xFFFF)
    crc = (crc << 8) | ((crc >> 8) & 0xFF)
    return int(crc)

def getByte(data,pos):
    return data << pos*8 & 0xff
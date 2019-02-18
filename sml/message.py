# -*- encoding: utf-8 -*-
import re
from sml.helper import *
from sml.types import smltree
from sml.types import SMLTree
from sml.datatypes import dataencode
import struct
import binascii


#EscSeq = 0x1b1b1b1b
#MsgBeg = 0x01010101 # leitet Uebertragung Version 1 als Datenstrom ein
#BegSmlMsg = re.compile(b"\x1b\x1b\x1b\x1b\x01\x01\x01\x01")
#EndSmlMsg = re.compile(b"\x1a[\x00\x01\x02\x03][0x00-0xff][0x00-0xff]")
#StartList = re.compile(b"[\x70-\x7F]")
dTypeN = {0: "s", 4: "?", 5: {2: "b", 3: "h", 5: "i", 9: "q"}, 6: {2: "B", 3: "H", 5: "I", 9: "Q"}}

def SMLStartSeq(data):
    BegSmlMsg = re.compile(b"\x1b\x1b\x1b\x1b\x01\x01\x01\x01")
    posi = BegSmlMsg.search(data)
    if posi:
        return (posi.start())
    return -1


def readVals(data, elements, telement):
    print("Enter readVals")
    for reads in range(0,elements):
        tLen = 1
        dType, dLen, more = DataTypeandLength(data[:1])

        while more == True:
            dLen = dLen << 4

            _,newlen, more = DataTypeandLength(data[tLen:tLen+1])
            dLen = newlen + dLen
            tLen = tLen +1

        #case dType in 0x7.....
        #dType, dLen = cutByte(data[1])

        if dType == "List of": # 0x07:
            telement.child = SMLTree()
            try:
                if telement.name == "root":
                    telement.child.name = "SML Message"
                if telement.name == "SML Message":
                    telement.child.name = "SML Gedoens"
            except Exception as e:
                print(e)
            telement.child.parent = telement
            data = data[1:]
            #data = readVals(data,dLen,telement.child)
            continue
        if dType in ["UInt", "Integer", "Bool"]:     #(dType == 0x04) or (dType == 0x05) or (dType == 0x06):
            telement.data = data[0:dLen]
            data = data[dLen+1:]
            telement.next = SMLTree()
            telement.next.prev = telement
            continue
        if dType == "OctetString": #0x00:
            telement.data = data[:dLen-1]
            data = data[dLen:]
            if dLen == 0:
                data = data[tLen:]
            telement.next = SMLTree()
            telement.next.prev = telement
            telement = telement.next
            continue
        data = data[1:]
        print("dtype {} dlen {}".format(dType,dLen))
        print(len(data))
    print("leave readVals")
    return data


def ProcessMessage(data):
    EndSML = re.compile(b"\x1b\x1b\x1b\x1b\x1a")
    StartList = re.compile(b"[\x70-\x7F]")
    posi = StartList.search(data) # suche 1. Vorkommen von 0x70 - 0x7F
    if not posi:
        return -1
    spos = posi.start()
    data = data[spos:]

    while (True):
        if (EndSML.search(data).start() == 0) or (len(data) < 5):
            break
        data = readVals(data,1,smltree)
    elems = smltree
    gotelement = False
    comefromchild = False
    tabbi = ""
    while True:
        try:
            print("{}{}".format(tabbi,elems.name))
        except:
            print("{}Noname".format(tabbi))
        try:
            print(elems.data)
        except:
            print("{}No data".format(tabbi))
        if comefromchild == False:
            try:
                elems = elems.child
                gotelement = True
                tabbi = tabbi + "-"
            except:
                pass
        if gotelement == False:
            try:
                elems = elems.next
                gotelement = True
                comefromchild = False
            except:
                pass
            if gotelement == False:
                try:
                    elems = elems.parent
                    comefromchild = True
                    tabbi = tabbi[:-1]
                    gotelement = True
                except:
                    pass
        if gotelement == False:
            break
        gotelement = False
        if len(data<5):
            break
    while (spos < len(data)):
            data = readvals(data, 1, smltree)

    if 1 > 0:
            dType, dLen, more = DataTypeandLength(data[spos:spos+1])
            #print("dType: {}, Len: {}, weiteres TL: {}".format(str(dType),str(dLen),more))
            if dType == "List of":
                messages = messages + 1
                spos = spos + 1
                anzahl = dLen
                if dLen == 6:
                    smltree.child = SMLTree()

            else:
                spos = spos + dLen
                if dLen == 0:
                    spos = spos + 1

    posi = StartList.search(data)

    if posi:
        print("ListStart found at {}".format(posi.start()))
    else:
        return -1
    if (data[8:10] == "\x76\x07"):
        print("SML Message")
        bla = data[28:32]

        print(':'.join(x.encode('hex') for x in bla))
        if (data[28:32] == "\x72\x62\x01\x65"):
            print("Sensor Time")
            print(":".join(":02x".format(ord(c)) for c in data[28:32]))
            SecIndex = data[32:36]
            print(":".join(":02x".format(ord(c)) for c in SecIndex))
            print("HerstellerID: {}".format(data[39:42]))
            print(":".join(":02x".format(ord(c)) for c in data[39:42]))
    print("test")


def getData(datatype, datalen, data):
    datatype = datatype & 0x07
    Daten = ""
    if datatype in dTypeN.keys():
        if datatype == 0:
            formstr = (datalen-1) * b"s"

        elif datatype == 4:
            formstr = dTypeN[datatype]
        elif datatype == 5 or datatype == 6:
            if datalen in dTypeN[datatype].keys():
                formstr = dTypeN[datatype][datalen]
            else:
                print("Fehler: Typ {} Laenge {}".format(datatype, datalen))
        try:
            #print("{}".format(binascii.hexlify(data[:datalen])))
            Daten = struct.unpack(formstr, data)[0]
            #print(Daten)
        except Exception as e:
            print(e)
    if Daten == "":
        Daten = data[:datalen]
    return Daten


def readStuff(data, elements, liste):
    while elements > 0:
        elements -= 1
        extlen = 0
        lenbytes = 1
        try:
            datatype, datalen = cutByte(data[0])
        except:
            if len(data) == 0:
                break
        if datatype not in (0x0, 0x4, 0x5,0x6,0x7):
            print("buh")
        if datatype == 0x4 and datalen != 2:
            print("boolbuh")
        if datatype in (0x5, 0x6) and datalen not in (2,3,5,9):
            print("intbuh")
        #print("TL: {}".format(binascii.hexlify(data[0])))
        #print(binascii.hexlify(data[:datalen]))
        while (datatype & 8):
            extlen = extlen << 4 + (datalen & 0x0F)
            datatype, datalen = cutByte(data[lenbytes])
            lenbytes += 1
        if extlen > 0:
            datalen = extlen
        data = data[lenbytes:]
        if datatype == 0x07 or datatype == 0x15:
            templist = []
            data,templist = readStuff(data,datalen,templist)
            liste.append(templist)
        else:
            if datalen < 2:
                liste.append("none")
            else:
                Daten = getData(datatype, datalen, data[:datalen-lenbytes])
                liste.append(Daten)
            #liste.append(data[1:datalen])
                #print(binascii.hexlify(data))
                #print(datalen-1+lenbytes)
                data = data[datalen-1+lenbytes:]
                #print(binascii.hexlify(data))
    #print(liste)
    return data,liste

def parseSML(data):
    dateilen = len(data)
    SMLFileStart = re.compile(b"\x1b\x1b\x1b\x1b\x01\x01\x01\x01")
    StartList = re.compile(b"[\x70-\x7F]")
    SMLFileEnd = re.compile(b"\x1b\x1b\x1b\x1b\x1a")
    DataTypes = dataencode()
    while 1:
        print(len(data))
        startpos = SMLFileStart.search(data)
        endpos = SMLFileEnd.search(data)

        if not startpos or not endpos:
            break
        print(startpos.start())
        print(endpos.start())

        daten = data[startpos.start():endpos.start() + 8]
        DataTypes.__init__(data[startpos.start():endpos.start()])
        data = data[endpos.start() + 8:]

    exit()

    spos2 = posi2.start()
    #print(binascii.hexlify(data[spos2:spos2+20]))
    print(crc16(data[:spos2+6]))
    print(struct.unpack("H",(data[spos2+6:spos2+8]))[0])
    #print(binascii.hexlify(data[spos:spos2]))
    #data = bytearray(data)
    #data.
    print("Start found at {}".format(spos))
    data1 = bytes(data[spos:spos2])

    DataTypes = dataencode(data1)
    print("Data left: {}".format(len(data)))
    print("Starts with {}".format(binascii.hexlify(data[0:4])))
    exit()

    liste = []
    _, liste = readStuff(data1,1,liste)
    for elem in liste:
        print(elem)

    liste2 = []
    data1 = data[spos2:]
    posi = StartList.search(data[spos2:])
    if posi:
        spos1 = posi.start()
        posi2 = StopList.search(data1[spos1:])
        if posi2:
            spos2 = posi2.start()
            _, liste2 = readStuff(data1[spos1:spos2],1,liste2)
            for elem in liste2:
                print(elem)
#* manual parsing of input data:
#	 * 1B1B1B1B
#	 * 01010101
#	 * 76 TL Field list of.., len = 6
#	 *  07 1. list element, TL Field : octet string, len 6 (why not 7?)
#	 *   003600001AFA  =transaction id
#	 *  62 00 2nd list element, TL field: u8, val=0 =group id
#	 *  62 00 3rd list element, TL field: u8, val=0 =abort on error
#	 *  72 4th list element, TL list of, len = 2 =message body
#	 *   630101 1st elem, TL u16, val=101 =tag ("public open req")
#	 *   76 2nd elem, TL list of, len = 6
#	 *    01 opt codepage
#	 *    01  opt clientid
#	 *    07 str, len 6= 0036044808FE reqFileId
#	 *    09 3032323830383136 serverId
#	 *    01 opt time
#	 *    01 opt version
#	 *  63 5th elem, u16, val = 31ED =crc16
#	 *  00 6th elem EndOfSMLMsg
#	 * 76 list of, len=6
#	 *  07 tl octet string, len 6 = 003600001AFB = transaction id
#	 *  62 u8, 00 =groupid
#	 *  62 u8, 00 =abort on error
#	 *  72 list, len=2 = message body
#	 *   63 0701 =tag (get list response)
#	 *   77 = message body data list with 7 elements
#	 *    01 opt clientid
#	 *    09 str, len 8 =3032323830383136 serverId
#	 *    01 opt listname
#	 *    72 actSensorTime
#	 *     62 u8, val=01
#	 *     65 u32, val=04487D89
#	 *    76 valList
#	 *     77
#	 *      07 str, l 6 =8181C78203FF objName 129-129:xC7... -> error code
#	 *      01 opt status
#	 *      01 opt valTime
#	 *      01 opt unit
#	 *      01 opt scaler
#	 *      04 str, l3 =454D48 value
#	 *      01 opt valueSignature
#	 *     77
#	 *      07 str, l 6 =0100000000FF objName 1-0:0.0.0*FF
#	 *      01
#	 *      01
#	 *      01
#	 *      01
#	 *      09 str, l 8 =3032323830383136 "02280816" Eigentumsnr?
#	 *      01
#	 *     77
#	 *      07 str, l 6 =0100010801FF objName 1-0:1.8.1*FF
#	 *      63 u16 =0180 status
#	 *      01
#	 *      62 u8, =1E unit -> Wh
#	 *      52 s8, =FF scaler (-> 10⁻1)
#	 *      56 signed int len 5 byte 0008D1CF1B
#	 *      01
#	 *     77
#	 *      07 str l 6 =0100010802FF objName 1-0:1.8.2*FF
#	 *      63 u16 =0180
#	 *      01
#	 *      62 u8 =1E
#	 *      52 s8 = FF
#	 *      56 s int, len 5 byte 0000004E9C
#	 *      01
#	 *     77
#	 *      07 str l 6 =00006001FFFF 0-0:96.1.FF*FF
#	 *      01
#	 *      01
#	 *      01
#	 *      01
#	 *      0B str l 10 = 30303032323830383136 "0002280816"
#	 *      01
#	 *     77
#	 *      07 str l 6 =0100010700FF objName 1-0:1.7.0*FF
#	 *      01
#	 *      01
#	 *      62 u8 = 1B unit
#	 *      52 s8 = FF scaler-> 10⁻1
#	 *      55 s int32 = 00000070 -> 112 -> 11.2
#	 *      01
#	 *    01 opt listSignature
#	 *    01 opt actGatewayTime
#	 *   63 u16 =D201 crc16
#	 *   00 EndOfSMLMsg
#	 *  76
#	 *   07 str l 6 = 003600001AFC
#	 *   62 u8 = 00
#	 *   62 u8 = 00
#	 *   72
#	 *    63 u16 = 0201
#	 *    71
#	 *     01
#	 *   63 u16 = 077A crc
#	 *   00 EndOfSMLMsg
#	 *  00
#	 *  1B1B1B1B
#	 *  1A019D37
#	 */
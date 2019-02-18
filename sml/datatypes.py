# -*- encoding: utf-8 -*-
from sml.helper import cutByte, getTLData, ByteToHex
import struct
from sml.types import dTypeN, dTypeNames, SML_Message
from collections import deque

class dataencode():
    smlMSG = SML_Message()
    encodedData = deque()

    def __init__(self, data = b''):
        if len(data) > 0:
            self.encodedData = self.encodeData(data, self.encodedData)
            self.smltranslate(self.encodedData)
        else:
            return

    def smltranslate(self, encodedData):
        while True:
            erg, encodedData = self.smlMSG.datafill(encodedData)
            if erg == False:
                break
            #print(self.smlMSG.__str__())

    def encodeData(self, data, datalist):
        if data[:8] == b"\x1b\x1b\x1b\x1b\x01\x01\x01\x01":
            print("SML Message Version 1")
        else:
            print("Wrong SML Header")
            return []
        tl = 8
        while tl < len(data):
            wert = ""
            if data[tl] == '\0' or data[tl] == 0:
                try:
                    datalist.append(dict(Wert = 0))
                except Exception as e:
                    print(e)
                tl += 1
                continue
            t, l = self.cutByte(data[tl])
            if t & 8:       # Length exceeds 14 Byte
                extlen = 0
                while True:
                    extlen = extlen << 4
                    extlen += (l & 0x0F)
                    if not t & 8:
                        l = extlen - 1 # minus second tl field, which is not part of the string then
                        break
                    tl += 1             # the lost length is added here to correct navigation inside data
                    t, l = cutByte(data[tl])


            if t == 4 and l == 2:
                try:
                    wert = dict(Bool = struct.unpack(dTypeN[t],data[tl +1: tl + l])[0])
                except:
                    pass
                tl += 1
            elif t in (5,6) and l in (2,3,5,9):
                try:
                    wert = dict(Wert = struct.unpack(dTypeN[t][l], data[tl+1:tl + l])[0])
                except:
                    pass
                tl += l
            elif t in (5,6): # Lengthfields 4 seen...
                try:
                    wert = dict(Wert = data[tl + 1: tl + l ])
                except:
                    print("decoder error")
                tl += l
            elif t == 0:
                if l == 1:
                    try:
                        wert = dict(optional = struct.unpack((dTypeN[t]*(l-1)), data[tl+1:tl+l]))
                    except Exception as e:
                        print(e)
                else:
                    try:
                        wert = dict(octetstring = struct.unpack((dTypeN[t]*(l-1)), data[tl+1:tl+l]))
                    except Exception as e:
                        print(e)
                tl += l
            elif t == 7:
                wert = dict(Listelem = l)
                tl += 1
            else:
                tl += 1
                continue
            try:
                try:
                    datalist.append(wert)
                except:
                    datalist = list(wert)
            except:
                pass
        return datalist

    def cutByte(self, toCut):
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
        return (leftpart, rightpart)

    def printall(self):
        Maske = """SML Nachricht:\nTransaction ID: {}\nGroup No: {}\nMessages:\n"""
        print(Maske.format(self.smlMSG.transID, self.smlMSG.groupNo))
        for msg in self.smlMSG.Messages:
            print("MessageTyp: {}".format(msg))
            for elem in self.smlMSG.Messages[msg]:
                if elem == 'valList':
                    #for listelem in self.smlMSG.Messages[msg][elem]:
                    #    print("\t\t{} {}".format(listelem, self.smlMSG.Messages[msg][elem][listelem]))
                    for listelem in self.smlMSG.Messages[msg][elem]:
                        print("\t\t{} {}".format(listelem, ByteToHex(self.smlMSG.Messages[msg][elem][listelem]['objName'])))
                else:
                    print("\t{} {}".format(elem,ByteToHex(self.smlMSG.Messages[msg][elem])))
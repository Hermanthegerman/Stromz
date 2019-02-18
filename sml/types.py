# -*- encoding: utf-8 -*-
from sml.helper import cutByte, getTLData, ByteToHex
from collections import deque

dTypeNames = {0: "OctetString", 1: "was zum....", 4: "Bool", 5: "Integer", 6: "UInt", 7: "List of"}
dTypeN = {0: "c", 4: "!?", 5: {2: "!b", 3: "!h", 5: "!i", 9: "!q"}, 6: {2: "!B", 3: "!H", 5: "!I", 9: "!Q"}, 7: None}

class SML_Message():
    transID = 0
    groupNo = 0
    abortOnError = 0
    messageBody = 0
    crc16 = 0
    eom = 0
    MessageType = ""
    Messages = dict()

    def datafill(self,data = []):
        if data == [] or len(data) == 0:
            return False, data
        try:
            if 'Listelem' not in data[0]:
                pass
        except:
            pass
        if data.popleft()['Listelem'] == 6:
            try:
                self.transID = data.popleft().values()[0]
                self.groupNo = data.popleft().values()[0]
                self.abortOnError = data.popleft().values()[0]
                mess = data.popleft()
                if 'Listelem' in mess:
                    self.messageBody = data.popleft().values()[0]
                else:
                    self.messageBody = mess['Wert']
                self.MessageType = SML_MessageBody[self.messageBody]
                if self.MessageType != "":
                    erg, data = self.parseMsg(data, self.MessageType)
                    if erg == True:
                        self.crc16 = data.popleft().values()[0]
                        try:
                            if data.popleft().values()[0] == 0:
                                self.eom = 1
                        except Exception as e:
                            print(e)

                    return erg, data
            except Exception as e:
                print(e)
                return False, data
        else:
            pass

    def parseMsg(self, data = [], mt = ""):
        if mt in SML_MessageBody.values():
            print("Messagetyp: {}".format(mt))
            self.Messages[mt], data = MessageTypes().filldata(data,mt)
            return True, data
        else:
            print(type)
            return False, data

    def __str__(self):
        tostr = ("Transaction ID: {}\n".format(ByteToHex(self.transID)))
        tostr += ("Group No : {}\n".format(ByteToHex(self.groupNo)))
        tostr += ("abort on Error: {}\n".format(ByteToHex(self.abortOnError)))
        tostr += ("MessageBody: {}\n".format(self.MessageType))
        return tostr


SML_MessageBody = {0x00000100: "OpenRequest",
                   0x00000101: "OpenResponse",
                   0x00000200: "CloseRequest",
                   0x00000201: "CloseResponse",
                   0x00000300: "GetProfilePackRequest",
                   0x00000301: "GetProfilePackResponse",
                   0x00000400: "GetProfileListRequest",
                   0x00000401: "GetProfileListsResponse",
                   0x00000500: "GetProcParameterRequest",
                   0x00000501: "GetProcParameterResponse",
                   0x00000600: "SetProcParameterRequest",
                   0x00000601: "SetProcParameterResponse",
                   0x00000700: "GetListRequest",
                   0x00000701: "GetListResponse",
                   0x00000800: "GetCosemRequest",
                   0x00000801: "GetCosemResponse",
                   0x00000900: "SetCosemRequest",
                   0x00000901: "SetCosemResponse",
                   0x00000A00: "ActionCosemRequest",
                   0x00000A01: "ActionCosemResponse",
                   0x0000FF01: "AttentionResponse"}

'''SML_ErrorMessages = {
0x8181C7C7E000
}
'''
SML_Parameter = {'\x01\x00\x00\x02\x02\xFF': "Schaltprogramm-Nr",
                 '\x81\x81\xC7\x8C\x01\xFF': "Aktivierung_INFO_Schnittstelle",
                 '\x81\x81\xC7\x8C\x02\xFF': "Aktivierung_Betriebsart_EDL40",
                 '\x81\x81\xC7\x8C\x03\xFF': "Löschen_der_historischen_Werte",
                 '\x81\x81\xC7\x8C\x04\xFF': "Aktivierung_der_Ausgabe_historischer_Werte_auf_der_Anzeige",
                 '\x81\x81\xC7\x8C\x06\xFF': "Ausgabe_fuer_30_Sek_eines_INFO-Textes_auf_der_Anzeige",
                 '\x81\x81\xC7\x8C\x07\xFF': "Bitmaske_der_auf_dem_Display_sichtbaren_Tarifregister",
                 '\x81\x81\xC7\x8C\x08\xFF': "Ausgabe_erweiterter_herstellerspezifischer_Datensatz",
                 '\x81\x81\xC7\x8C\x09\xFF': "Loeschen_per_Aufruftaste_zu_historischen_Werten_freigeben",
                 '\x81\x81\xC7\x8C\x0A\xFF': "Aktivierung_Schutz_per_Pincode_auf_das_Display",
                 '\x81\x81\xC7\x8C\x0B\xFF': "Pin-Code_zum_Zugriff_auf_das_Display",
                 '\x81\x81\xC7\x8C\x0C\xFF': "Ereigniszaehler_fuer_Manipulationsversuche",
                 '\x81\x81\xC7\x8C\x0D\xFF': "Aktivierung_des_Schutzes_per_PINcode_einschalten",
                 '\x01\x00\x01\x08\x00\x63': "Historischer Verbrauch letzte 365 Tage",
                 '\x01\x00\x01\x08\x00\x62': "Historischer Verbrauch letzte 30 Tage",
                 '\x01\x00\x01\x08\x00\x61': "Historischer Verbrauch letzte 7 Tage",
                 '\x01\x00\x01\x08\x00\x60': "Historischer Verbrauch letzter Tag",
                 '\x01\x00\x01\x09\x0B\x00': "Kalendarischer Zeitstempel",
                 '\x01\x00\x0F\x07\x00\xFF': "Akltuelle Wirkleistung Betrag",
                 '\x01\x00\x23\x07\x00\xFF': "Aktuelle Wirkleistung Betrag L1",
                 '\x01\x00\x37\x07\x00\xFF': "Aktuelle Wirkleistung Betrag L2",
                 '\x01\x00\x4b\x07\x00\xFF': "Aktuelle Wirkleistung Betrag L3"}

class MessageTypes():
    mesDef = dict( OpenResponse = ['CodePage', 'clientID', 'reqFileID', 'serverID', 'refTime', 'smlVersion'],
                   CloseResponse = ['globalSignature'],
                   GetListResponse = ['clientID', 'serverID', 'listName', 'actSensorTime', 'valList', 'listSignature', 'actGatewayTime'],
                   valList = ['objName', 'status', 'valTime', 'unit', 'scaler', 'value', 'valueSignature'])

    #Message = dict()

    def smlTime(self, data):
        ts = 0
        elem = data.popleft()
        if 'optional' in elem:
            return 'optional', data
        elems = elem.values()[0]
        tityp = data.popleft().values()[0]
        for count in range(elems - 1):
            ts += data.popleft().values()[0]
        if tityp == 3:
            return dict(localTimeStamp = ts), data
        elif tityp in [1,2]:
            return dict(TimeStamp = ts), data
        else:
            return False, data

    def filldata(self, data = [], mt = {}):
        Message = dict()
        if data == [] or mt not in self.mesDef:
            return False, data
        if 'Listelem' not in data.popleft():
            return False, data
        try:
            for elem in self.mesDef[mt]:
                if elem == 'valList':
                    Message[elem] = dict()
                    if 'Listelem' in data[0] and 'Listelem' in data[1]:
                        elemcount = data.popleft().values()[0]
                        for counti in range(1,elemcount + 1):
                            Message[elem][counti], data = self.filldata(data, elem)

                    else:
                        Message[elem][1], data = self.filldata(data, elem)
                elif elem in ['actSensorTime', 'valTime']:
                    Message[elem], data = self.smlTime(data)
                elif elem in ['objName']:
                    objName = b''.join(data.popleft().values()[0])
                    print(SML_Parameter)
                    print(ByteToHex(objName))
                    if objName in SML_Parameter:
                        Message[elem] = SML_Parameter[objName]
                    else:
                        Message[elem] = objName
                else:
                    Message[elem] = data.popleft().values()[0]

        except Exception as e:
            print(self.__class__.__name__, + e)
        return Message, data


def smltree():
    pass

def SMLTree():
    pass

SMLStartSeq = ""
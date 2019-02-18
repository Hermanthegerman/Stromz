# -*- encoding: utf-8 -*-
from sml.helper import cutByte
import binascii, struct
from pprint import pprint


with open('vzdump','rb') as f:
    output = f.read()
content = binascii.hexlify(output)

ESCAPE = binascii.unhexlify("1b1b1b1b")
MESSAGE_BEGIN = binascii.unhexlify("01010101")
MESSAGE_END = 0x1a
TYPE_STRING = 0x0
TYPE_BOOL = 0x4
TYPE_UINT = 0x5
TYPE_INT = 0x6
TYPE_LIST = 0x7
SML_MESSAGE_END = 0x00

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
wet = binascii.unhexlify("0100010800ff")
wet2 = binascii.unhexlify("0100010801ff")
wet3= binascii.unhexlify("0100010802ff")
wet4 = binascii.unhexlify("0100020800ff")
wet5 = binascii.unhexlify("0100020801ff")
wet6 = binascii.unhexlify("0100020802ff")
obis= {wet: "Wirkbezug ET",
        wet2: "Wirkbezug HT",
        wet3: "Wirkbezug NT",
       wet4: "Wirkarbeit Lieferung ET",
       wet5: "Wirkarbeit Lieferung HT",
       wet6: "Wirkarbeit Lieferung NT"}

def parse(hexstring, index = 0, max_tokens = 0):
    hexlength = len(hexstring)
    parsetree = []
    parsed_tokens = 0
    while index < hexlength:
        if is_escape(hexstring, index):
            if read(hexstring, index+4, 4) == MESSAGE_BEGIN:
                parsed, index = parse(hexstring, index + 8)
                parsetree.append(("MessageBegin", parsed))
                continue
            elif ord(hexstring[index+4]) == MESSAGE_END:
                return parsetree, index + 8
        type, length, index = read_type_and_length(hexstring, index)
        if type == 0 and length == -1: # End of SMLMessage
            return parsetree, index
        parsed, index = read_data(hexstring, index, type, length)
        if parsed in obis.keys():       #hermi
            parsed = obis[parsed]       #hermi
        data = format_data(parsed, type, length)
        if max_tokens == 2 and parsed_tokens == 0:  #hermi
            if data in SML_MessageBody.keys():      #hermi
                data = SML_MessageBody[data]        #hermi
        parsetree.append(data)
        parsed_tokens += 1
        if max_tokens > 0 and parsed_tokens == max_tokens:
            return parsetree, index
    return parsetree, index

def read_type_and_length(hexstring, index):
    byte = ord(hexstring[index])
    length = byte & 0x0F
    type = (byte >> 4) & 0x07
    index += 1
    length_bytes = 1
    if type == 0x15 or type == 0x08:
        while byte & 0x80 == 0x80 and index < len(hexstring):
            byte = ord(hexstring[index])
            length = length << 4 + (byte & 0x0F)
            index += 1
            length_bytes += 1
            if byte & 0x70 != 0x00:
                break
    if type != 7:
        length -= length_bytes
    return type, length, index


def read_data(hexstring, index, type, length):
    if type == TYPE_LIST:
        return parse(hexstring, index, length)
    elif length < 0:
        return '', index
    else:
        parsed = read(hexstring, index, length)
        index += length
        return parsed, index


def format_data(data, type, length):
    if type == TYPE_STRING:
        formstr =  "!" + length * 'c' # byte-order big-endian or network order
    if type == TYPE_BOOL:
        formstr = '?'
    if type == TYPE_INT:
        if length == 1:
            formstr = 'b'
        if length == 2:
            formstr = '!h'
        if length == 4:
            formstr = '!i'
        if length == 8:
            formstr = '!q'
    if type == TYPE_UINT:
        if length == 1:
            formstr = 'B'
        if length == 2:
            formstr = '!H'
        if length == 4:
            formstr = '!I'
        if length == 8:
            formstr = '!Q'
    try:
        if type == TYPE_STRING:
            return ''.join(struct.unpack(formstr, data))
        else:
            return struct.unpack(formstr, data)[0]
    except:
        return data


def is_escape(hexstring, index):
    return read(hexstring, index, 4) == ESCAPE


def read(hexstring, index, length):
    return hexstring[index:index+length]

print(content)
msg, _ = parse(output)
pprint(msg)


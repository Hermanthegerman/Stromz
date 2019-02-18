# -*- encoding: utf-8 -*-
from sml.helper import cutByte
import binascii


with open('vzdump','rb') as f:
    output = f.read()
content = binascii.hexlify(output)

#print(binascii.unhexlify("03"), "test")
#ESCAPE = binascii.unhexlify("1b1b1b1b")
#MESSAGE_BEGIN = binascii.unhexlify("01010101")
#MESSAGE_END = binascii.unhexlify("1a")
#print ESCAPE
Types = {"0": "String", "4": "Bool", "5": "UInt", "6": "Int", "7": "List"}



def parse(hexstring, max_tokens=0):
    parsed_tokens = 0
    index = 0
    token_pos = 0
    token = ''
    parsetree = []
    datalength = len(hexstring);
    while index < datalength:
        token = token + hexstring[token_pos]
        lookahead = hexstring[index:index+8]
        if lookahead == "00760700":
            print "HAHA"
        parsed = ''
        try:
            if lookahead == "1b1b1b1b":  # Escape
                parsed, index = in_escape(hexstring, index + 8) #len(token))
                token_pos = index
                token = ''
                parsed_tokens += 1
                parsetree.append(parsed)
            #if lookahead == "00":
            #    parsed = lookahead
            #    index += 2
            #    token = ''
            #    token_pos = index
            #    parsed_tokens += 1
            #    parsetree.append(parsed)
            elif token in Types:
               # print token
                type, next = get_type(hexstring,index)
                parsed, next = parse_type(hexstring, next, type)
                parsetree.append(parsed)
                parsed_tokens += 1
                token = ''
                token_pos = index = next + 1
            elif len(token) == 1 and int(token, 16) >= 8:
                n_token = str(int(token,16) - 8)
                #print ("bla", token, n_token)
                if n_token in Types:
                    parsed, next = parse_type(hexstring, index + 1, Types[n_token], True)
            elif len(token) > 8:
                parsetree.append(token)
                parsed_tokens += 1
                token = ''
                token_pos = index = index + 9
                #print("parse error at index ", index, token, " at: ", hexstring[index-8:index+8])
            else:
                token_pos = token_pos + 1
            if max_tokens > 0 and parsed_tokens == max_tokens:
                return parsetree, index
        except:
            print(parsetree)
            raise
    return parsetree, index


def in_escape(hexstring, index):
    if hexstring[index:index + 8] == "01010101":
        #tree, index = parse(hexstring[index+8:])
        return "MessageBegin", index + 8#["MessageBegin", tree], index + 8
    if hexstring[index:index + 2] == "1a":
        return "EndMessage", index + 8
    else:
        return hexstring[index:index + 8], index + 8

def get_type(hexstring, index):
    type = hexstring[index]
    return Types[type], index + 1

def parse_type(hexstring, index, type, added_length = False):
    if type == "List":
        return parse_list(hexstring, index, added_length)
    if type == "String":
        length = int(hexstring[index], 16) * 2 - 2
        if added_length:
            length += int(hexstring[index + 1], 16) * 2 - 2
        if length < 0:
            return "", index
    else:
        length = int(hexstring[index], 16) * 2 - 2
    parsed = hexstring[index+1:index+1+length]
    return parsed, index + length




def parse_list(hexstring, index, added_length = False):
    listlen = int(hexstring[index], 16)
    if added_length:
        index += 1
        listlen += int(hexstring[index], 16)
    parsed, newindex = parse(hexstring[index + 1:], listlen)
    return parsed, index + newindex


print(content)

parsed, index = parse(content[:2000])
for x in parsed:
    print x
#print parsed
#print(parse(
#    "1b1b1b1b010101017607000602a7e180620062007263010176010107000600cea0800b0901454d48000069c032010163c1db007607000602a7e180620062007263010176010107000600cea0800b0901454d48000069c032010163c1db00"))
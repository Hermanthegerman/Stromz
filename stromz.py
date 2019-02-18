# -*- encoding: utf-8 -*-

import re
from sml.datatypes import dataencode


with open('vzdump','rb') as f:
    data = f.read()

print("Bytes read: {}".format(len(data)))


SMLFileStart = re.compile(b"\x1b\x1b\x1b\x1b\x01\x01\x01\x01")
StartList = re.compile(b"[\x70-\x7F]")
SMLFileEnd = re.compile(b"\x1b\x1b\x1b\x1b\x1a")

while 1:
    DataTypes = dataencode()
    startpos = SMLFileStart.search(data)
    endpos = SMLFileEnd.search(data)

    if not startpos or not endpos:
        break

    daten = data[startpos.start():endpos.start() + 8]
    DataTypes.__init__(data[startpos.start():endpos.start()])
    DataTypes.printall()
    del DataTypes
    data = data[endpos.start() + 8:]

exit()

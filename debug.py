#!/usr/bin/python3

from sugarsync import XMLElement
from sugarsync import Printer
from sugarsync import XMLTextNode

f = open('curltest/publiclinkresp.xml', 'r')
data = f.read()

data = XMLElement.parse(data)
print(vars(data))
Printer(data)

#!/usr/bin/python3

from SugarSync import XMLElement, XMLTextNode
f = open('collection.xml', 'r')
xml = f.read()

elm = XMLElement.parse(xml)
print(elm.toString())

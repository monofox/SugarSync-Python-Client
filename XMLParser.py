#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# author: Alexander Straube
# author: Lukas Schreiner
# 
# For editors/contributors: please add an author tag above - 
# for a full list ;-)
#

import xml.dom.minidom as dom
import re
from Printer import Printer
from XMLTextNode import XMLTextNode
from XMLElement import XMLElement

class XMLParser:
    @staticmethod
    def parse(xml, parse = True, first = True):
        xmlpar = []
        if parse:
            # we remove all \n and others!
            xml = re.sub('\n', '', xml)
            xml = re.sub('\r', '', xml)
            xml = re.sub('>( *)<', '><', xml)

            tree = dom.parseString(xml)
            # we have always to use the first child!
            return XMLParser.parse(tree, False)
        else:
            tree = xml

        for branch in tree.childNodes:
            if branch.nodeType == branch.ELEMENT_NODE:
                xmltmp = XMLElement(branch.nodeName)
                # Attribute ?
                if branch._get_attributes() is not None:
                    for attr,value in branch._get_attributes().items():
                        xmltmp.setAttribute(attr,value)

                if branch.childNodes is not None:
                    ch = XMLParser.parse(branch, False, False)
                    if ch is not None:
                        for child in ch:
                            xmltmp.addChild(child)

                xmlpar.append(xmltmp)
            elif branch.nodeType == branch.TEXT_NODE:
                xmlpar.append(XMLTextNode(branch.nodeValue))
            else:
                xmlpar = None

        if first and xmlpar is not None and len(xmlpar) == 1:
            xmlpar = xmlpar[0]

        return xmlpar

def standAloneTest():
    f = open('collection.xml')
    d = XMLParser.parse(f.read())
    print(d)
    print(d.toString())

if __name__ == "__main__":
    standAloneTest()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# author: Alexander Straube
# author: Lukas Schreiner
# 
# For editors/contributors: please add an author tag above - 
# for a full list ;-)
#
import re
from XMLTextNode import XMLTextNode

class XMLElement:
    
    def __init__(self, name=''):
        self.name = str(name)
        self.attributes = {}
        self.childs = []
        self.childIsText = False
        self.head = None
        self.value = None
        
    def getName(self):
        return self.name
    
    def setHead(self, value):
        self.head = value
        
    def removeHead(self):
        self.head = None

    def getValue(self):
        return self.value
    
    def setAttribute(self, name, value):
        self.attributes[name] = value
    
    def removeAttribute(self, name):
        try:
            del self.attributes[name]
        except:
            print("Element doesn't exist!")
    
    def addChild(self, elm):
        # there can't be more than 1 child if elm == XMLTextNode
        
        self.childs.append(elm)
        
        # we want an dynamic element!
        if elm.getName() is None:
            # this is an XMLTextNode
            self.value = elm.getValue()
        else:
            setattr(self, elm.getName(), elm)
        
        return self # for compact usage

    def getAttribute(self, attr):
        if self.hasAttribute(attr):
            return self.attributes[attr]
        else:
            # it does not exist
            return None

    def hasAttribute(self, attr):
        if attr in self.attributes:
            return True
        else:
            return False
    
    def getAttributes(self):
        attr = ''
        for k,f in self.attributes.items():
            attr = attr+' %s="%s"' % (k, f)
    
        return attr
    
    def getChildren(self):
        return self.childs
    
    def getChilds(self):
        xml = ''
        for f in self.childs:
            xml = xml+f.toString()
            
        return xml
    
    def toString(self):
        xml = ''
        if self.head is not None:
            xml = self.head
        xml = xml + '<%s%s>%s</%s>' % (self.name, self.getAttributes(), self.getChilds(), self.name)
        
        return xml
    
    @staticmethod
    def parse(data, first = True):
        xmlpar = []
        
        # remove first line thing
        if first:
            pattern = '(<\?xml version.*\?>)'
            data = re.sub(pattern, '', data)

        pattern =  '<([^<>]+)?(( ([^<>]*)="([^<>]*)")*)>(.+)</\\1>'
        # following pattern is not useable because we will not get an hierachie.
        # pattern =  '<([^<>]+)?(( ([^<>]*)="([^<>]*)")*)>([^<>]+)</\\1>'
        m = re.compile(pattern, re.I | re.S)
        
        if m.search(data) is not None:
            xml = m.findall(data)
                           
            for f in xml:
                # 0: key, 1: value
                xmltmp = XMLElement(f[0])
                
                # we need childs!
                ch = XMLElement.parse(f[5], False)
                if ch is not None:
                    for k in ch:
                        xmltmp.addChild(k)
                
                xmlpar.append(xmltmp)
        elif data is not None:
            xmlpar.append(XMLTextNode(data))
        else:
            xmlpar = None
        
        if first and xmlpar is not None and len(xmlpar) == 1:
            xmlpar = xmlpar[0]
        
        return xmlpar
    
    def repr(self):
        self.__repr__(True)
    
    def __repr__(self, ram = False):
        if self.value == None or ram:
            # normal resp
            return "<%s instance at %s>" % (self.__class__,id(self))
        else:
            return self.value

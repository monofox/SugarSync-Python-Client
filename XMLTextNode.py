#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# author: Alexander Straube
# author: Lukas Schreiner
# 
# For editors/contributors: please add an author tag above - 
# for a full list ;-)
#

class XMLTextNode:
    
    def __init__(self, value=''):
        self.value = value
        
    def getName(self):
        return None
        
    def setValue(self, value):
        self.value = value
        
    def getValue(self):
        return self.value
        
    def toString(self):
        return self.value


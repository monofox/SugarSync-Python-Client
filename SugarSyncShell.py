#!/usr/bin/env python3.2
# -*- coding: utf-8 -*-
#
# author: Alexander Straube
# author: Lukas Schreiner
# 
# For editors/contributors: please add an author tag above - 
# for a full list ;-)
# 
# Be careful! This communicates directly with sugarsync! (only names are cached!)

#from sugarsync import Printer, XMLElement, XMLTextNode
from SugarSyncCollection import SugarSyncCollection
from Colors import Colors
from console import Console

class SugarSyncShell:

    def __init__(self, sugarsync, startdir=None, collection=True):
        self.sugarsync = sugarsync
        self.virtualfs = startdir # starts with startdir

        self.path = [startdir]
        self.run = True

        self.cmds = {
                'clear': self.clear,
                'cd': self.cd,
                'ls': self.ls,
                'pwd': self.pwd,
                'exit': self.exit
                }
        self.names = []

        self.cmd()

    def getPath(self, withHeader=True, colorize=True):
        # the beginning:
        h = self.sugarsync.username[:self.sugarsync.username.find('@')] + ' '
        if colorize:
            h = Colors.c(h, Colors.YELLOWL)

        p = ''

        for f in self.path:
            p = p + f.getName() + '/'
        
        if colorize:
            p = Colors.c(p, Colors.BLUE)

        if withHeader:
            return h + p
        else:
            return p

    def cmd(self):
        while self.run:
            want = input('%s %s ' % (self.getPath(), Colors.c('$', Colors.BLUE)))
            cmd = ''
            param = ''
            # its always the same: command parameters - there is no &&, ||, |, &, etc. pp.

            index = want.find(' ')
            if index > 0:
                cmd = want[:index]
                param = want[index:]
            else:
                cmd = want
                param = ''

            try:
                self.cmds[cmd](param)
            except KeyError as ke:
                print('Wrong input.')

    
    def clear(self, param):
        (width, height) = Console.getTerminalSize()
        for f in range(0,height):
            print('');

    def cd(self, param):
        pass

    def ls(self, param):
        # get actual element:
        elm = self.path[len(self.path)-1]

        print(Colors.c('./', Colors.BLUE))
        if len(self.path) > 1:
            print(Colors.c('../', Colors.BLUE))

        for k,v in elm.getChildren().items():
            print(k)

    def pwd(self, param):
        print(self.getPath(False, False)) # withour header and without color

    def exit(self, param):
        print('Goodbye ;-)')
        self.run = False
            


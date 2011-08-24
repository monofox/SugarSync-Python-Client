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

class SugarSyncShell:

    def __init__(self, sugarsync, startdir=None):
        self.sugarsync = sugarsync
        self.names = {}

        self.path = [startdir]
        self.run = True

        self.cmds = {
                'cd': self.cd,
                'ls': self.ls,
                'pwd': self.pwd,
                'exit': self.exit
                }

        self.cmd()

    def getPath(self):
        p = ''
        for f in self.path:
            if p != '':
                p = p + '/'

            if f in self.names:
                p = p + self.names[f]
            else:
                # request it
                fi = self.sugarsync.getFileInfo(f, True)
                print(vars(fi))
                self.names[f] = fi.displayName.value
                p = p + self.names[f]

        return p

    def cmd(self):
        while self.run:
            want = input('%s> ' % self.getPath())
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

    
    def cd(self, param):
        pass

    def ls(self, param):
        pass

    def pwd(self, param):
        pass

    def exit(self, param):
        print('Goodbye ;-)')
        self.run = False
            


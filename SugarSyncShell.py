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

from SugarSyncCollection import SugarSyncCollection
from SugarSyncDirectory import SugarSyncDirectory
from SugarSyncFile import SugarSyncFile
from Colors import Colors
from console import Console
from Printer import Printer
from XMLElement import XMLElement
from XMLTextNode import XMLTextNode
import os, os.path

class SugarSyncShell:
    TYPE_FILE = 1
    TYPE_FOLDER = 2
    TYPE_ALL = 4

    def __init__(self, sugarsync, startdir=None, collection=True):
        self.sugarsync = sugarsync
        self.virtualfs = startdir # starts with startdir
        self.localPath = os.getcwd()
        self.path = [startdir]
        self.run = True

        self.cmds = {
                'clear': self.clear,
                'cd': self.cd,
                'get': self.get,
                'ls': self.ls,
                'lpwd': self.lpwd,
                'lcd' : self.lcd,
                'pwd': self.pwd,
                'exit': self.exit
                }
        self.names = []

        self.cmd()

    def getPath(self, withHeader=True, colorize=True):
        # the beginning:
        if len(self.sugarsync.nickname) > 0:
            h = self.sugarsync.nickname + ' '
        else:
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

    def searchPath(self, path, typ):
        # TODO: make it performanenter with while instead of for ?
        data = None
        elm = self.path[len(self.path)-1]
        elm = elm.getChildren()

        if elm is not None:
            for k,v in elm.items():
                if str(v.getName()).strip() == path.strip() and ( 
                        (isinstance(v, SugarSyncDirectory) and typ == SugarSyncShell.TYPE_FOLDER)
                        or   (isinstance(v, SugarSyncFile) and typ == SugarSyncShell.TYPE_FILE)
                        ):
                    data = v
        
        return data

    def clear(self, param):
        (width, height) = Console.getTerminalSize()
        for f in range(0,height):
            print('');

    def cd(self, param):
        # TODO: at this point its very pre-release...
        # we have to trim the param
        param = param.strip()
        if param[len(param)-1:] == '/':
            param = param[:-1]

        # and split on / ?

        if param == '.':
            return True
        elif param == '..':
            self.path.pop()
        else:
            # search
            path = self.searchPath(param, SugarSyncShell.TYPE_FOLDER)
            if path is not None:
                self.path.append(path)
                return True
            else:
                print('Could not change the directory.')
                return False
    

    def ls(self, param):
        # get actual element:
        elm = self.path[len(self.path)-1]

        print(Colors.c('./', Colors.BLUE))
        if len(self.path) > 1:
            print(Colors.c('../', Colors.BLUE))

        for k,v in elm.getChildren().items():
            if isinstance(v, SugarSyncDirectory):
                print(Colors.c(str(k) + '/', Colors.BLUE))
            else:
                print(k)

    def pwd(self, param):
        print(self.getPath(False, False)) # withour header and without color

    def get(self, param):
        # at this point it can only be a file
        param = param.strip()

        if param in ['.', '..'] or param[len(param)-1:] == '/':
            print('It can be only a file at this development point.')
            return False
        
        elm = self.searchPath(param, SugarSyncShell.TYPE_FILE)
        if elm is not None:
            # filename ? and check if its exist...
            fname = elm.getName()
            if os.path.lexists(self.localPath+'/'+fname):
                # overwrite?
                overwrite = None
                while overwrite is None:
                    ow = input('Overwrite "%s/%s"? (N/y)' % (self.localPath,fname))
                    ow = ow.strip()
                    if ow in ['y', 'Y']:
                        overwrite = True
                    elif ow in ['n', 'N', '']:
                        overwrite = False
                    else:
                        print('I have not understand your answer "%s".' % (ow))

                if overwrite and not os.path.isfile(self.localPath+'/'+fname):
                        print('Can not overwrite something which is not a file.')
                        overwrite = None
            else:
                overwrite = True

            if overwrite and os.path.lexists(self.localPath+'/'+fname):
                os.remove(self.localPath+'/'+fname)
            
            if overwrite:
                self.sync.getFile(elm.getLink(), self.localPath+'/'+fname)

        else:
            print('Could not find the file.')
            return False

    def put(self, param):
        pass

    def lcd(self, param):
        param = param.strip()
        # change local path
        os.chdir(param)
        self.localPath = os.getcwd()

    def lpwd(self, param):
        # we do not accept any param
        print('Local Path: ' + os.getcwd())

    def exit(self, param):
        print('Goodbye ;-)')
        self.run = False
            


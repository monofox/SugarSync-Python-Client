#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author: unknown
# as found on http://stackoverflow.com/questions/287871/print-in-terminal-with-colors-using-python

class Colors:
    YELLOWL = '226'
    BLUE = '33'
    NORMAL = '231'

    @staticmethod
    def c(txt,col):
        return "\033[38;5;%sm%s\033[m" % (str(col), str(txt))

#for color in range(0, 256) :
#        print("\033[38;5;%sm%03s TEST\033[m" % (str(color), str(color)))
#        if color % 3:
#            print("\n")
#        else:
#            print("\t")


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author: unknown

class Printer:
    def __init__ (self, PrintableClass):
        for name in dir(PrintableClass):
            if name is not "__abstractmethods__":
                value = getattr(PrintableClass,name)
                if  '_' not in str(name).join(str(value)):
                    print('  .%s: %r' % (name, value))


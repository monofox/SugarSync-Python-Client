import fcntl, termios, struct, os

class Console:
    @staticmethod
    def ioctl_GWINSZ(fd):
        try:
            cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
        except:
            return None

        return cr 

    @staticmethod
    def getTerminalSize():

        cr = Console.ioctl_GWINSZ(0) or Console.ioctl_GWINSZ(1) or Console.ioctl_GWINSZ(2)
        if not cr:
            try:
                fd = os.open(os.ctermid(), os.O_RDONLY)
                cr = Console.ioctl_GWINSZ(fd)
                os.close(fd)
            except:
                pass
            if not cr:
                try:
                    cr = (env['LINES'], env['COLUMNS'])
                except:
                    cr = (25, 80)

        if len(cr) > 0:
            return (int(cr[1]), int(cr[0]))
        else:
            return (0,0)


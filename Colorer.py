import logging
import textwrap
import itertools
'''
Functions below: add_Coloring
Author: http://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output
Author: Dave Sorin
Downloaded 2/21/14
Edited by D. Folkner to change some of the colors and how it is output.
'''
# now we patch Python code to add color support to logging.StreamHandler
def add_coloring_to_emit_windows(fn):
        # add methods we need to the class
    def _out_handle(self):
        import ctypes
        return ctypes.windll.kernel32.GetStdHandle(self.STD_OUTPUT_HANDLE)
    out_handle = property(_out_handle)

    def _set_color(self, code):
        import ctypes
        # Constants from the Windows API
        self.STD_OUTPUT_HANDLE = -11
        hdl = ctypes.windll.kernel32.GetStdHandle(self.STD_OUTPUT_HANDLE)
        ctypes.windll.kernel32.SetConsoleTextAttribute(hdl, code)

    setattr(logging.StreamHandler, '_set_color', _set_color)

    def new(*args):
        FOREGROUND_BLUE      = 0x0001 # text color contains blue.
        FOREGROUND_GREEN     = 0x0002 # text color contains green.
        FOREGROUND_RED       = 0x0004 # text color contains red.
        FOREGROUND_INTENSITY = 0x0008 # text color is intensified.
        FOREGROUND_WHITE     = FOREGROUND_BLUE|FOREGROUND_GREEN |FOREGROUND_RED
       # winbase.h
        STD_INPUT_HANDLE = -10
        STD_OUTPUT_HANDLE = -11
        STD_ERROR_HANDLE = -12

        # wincon.h
        FOREGROUND_BLACK     = 0x0000
        FOREGROUND_BLUE      = 0x0001
        FOREGROUND_GREEN     = 0x0002
        FOREGROUND_CYAN      = 0x0003
        FOREGROUND_RED       = 0x0004
        FOREGROUND_MAGENTA   = 0x0005
        FOREGROUND_YELLOW    = 0x0006
        FOREGROUND_GREY      = 0x0007
        FOREGROUND_INTENSITY = 0x0008 # foreground color is intensified.

        BACKGROUND_BLACK     = 0x0000
        BACKGROUND_BLUE      = 0x0010
        BACKGROUND_GREEN     = 0x0020
        BACKGROUND_CYAN      = 0x0030
        BACKGROUND_RED       = 0x0040
        BACKGROUND_MAGENTA   = 0x0050
        BACKGROUND_YELLOW    = 0x0060
        BACKGROUND_GREY      = 0x0070
        BACKGROUND_INTENSITY = 0x0080 # background color is intensified.

        levelno = args[1].levelno
        if(levelno>=50):
            # color = BACKGROUND_YELLOW | FOREGROUND_RED | FOREGROUND_INTENSITY | BACKGROUND_INTENSITY
            color = FOREGROUND_MAGENTA | FOREGROUND_INTENSITY
        elif(levelno>=40):
            color = FOREGROUND_RED | FOREGROUND_INTENSITY
        elif(levelno>=30):
            color = FOREGROUND_YELLOW | FOREGROUND_INTENSITY
        elif(levelno>=20):
            color = FOREGROUND_GREEN
        elif(levelno>=10):
            color = FOREGROUND_CYAN
        else:
            color =  FOREGROUND_WHITE

        args[0]._set_color(color)

        ret = fn(*args)
        args[0]._set_color( FOREGROUND_WHITE )
        return ret
    return new

def add_coloring_to_emit_ansi(fn):
    # add methods we need to the class
    def new(*args):
        levelno = args[1].levelno
        if(levelno>=50):
            color = '\x1b[31m' # red
        elif(levelno>=40):
            color = '\x1b[31m' # red
        elif(levelno>=30):
            color = '\x1b[33m' # yellow
        elif(levelno>=20):
            color = '\x1b[32m' # green
        elif(levelno>=10):
            color = '\x1b[35m' # pink
        else:
            color = '\x1b[0m' # normal
        args[1].msg = color + args[1].msg +  '\x1b[0m'  # normal
        # args[1].levelname = color + args[1].levelname +  '\x1b[0m'  # normal

        #print "after"
        return fn(*args)
    return new

def customLogger(name):
    logger = logging.getLogger(name)
    logger_handler = logging.StreamHandler()
    logger.addHandler(logger_handler)
    logger_handler.setFormatter(MyFormatter("%(message)s"))
    logger.setLevel("DEBUG")

    return logger

import platform
if platform.system()=='Windows':
    # Windows does not support ANSI escapes and we are using API calls to set the console color
    logging.StreamHandler.emit = add_coloring_to_emit_windows(logging.StreamHandler.emit)
else:
    # all non-Windows platforms are supporting ANSI escapes so we use them
    logging.StreamHandler.emit = add_coloring_to_emit_ansi(logging.StreamHandler.emit)
    #log = logging.getLogger()
    #log.addFilter(log_filter())
    #//hdlr = logging.StreamHandler()
    #//hdlr.setFormatter(formatter())


'''
MyFormatter class
Adapted from: http://stackoverflow.com/questions/6847862/how-to-change-the-format-of-logged-messages-temporarily-in-python
              http://stackoverflow.com/questions/3096402/python-string-formatter-for-paragraphs
Authors: Vinay Sajip, unutbu
'''
class MyFormatter(logging.Formatter):

    #This function overwrites logging.Formatter.format
    #We conver the msg into the overall format we want to see
    def format(self,record):


        widths=[getTerminalSize()[0] - 12 ,10]
        form='{row[0]:<{width[0]}} {row[1]:<{width[1]}}'

        #Instead of formatting...rewrite message as desired here
        record.msg = self.Create_Columns(form,widths,[record.msg],["[%8s]"%record.levelname])

        #Return basic formatter
        return super(MyFormatter,self).format(record)

    def Create_Columns(self,format_str,widths,*columns):
        '''
        format_str describes the format of the report.
        {row[i]} is replaced by data from the ith element of columns.
        widths is expected to be a list of integers.
        {width[i]} is replaced by the ith element of the list widths.
        All the power of Python's string format spec is available for you to use
        in format_str. You can use it to define fill characters, alignment, width, type, etc.
        formatter takes an arbitrary number of arguments.
        Every argument after format_str and widths should be a list of strings.
        Each list contains the data for one column of the report.
        formatter returns the report as one big string.
        '''
        result=[]
        for row in zip(*columns):

            #Create a indents for each row...
            sub = []

            #Loop through
            for r in row:
                #Expand tabs to spaces to make our lives easier
                r = r.expandtabs()

                #Find the leading spaces and create indend character
                if r.find(" ") == 0:
                    i = 0
                    for letters in r:
                        if not letters == " ":
                            break
                        i += 1
                    sub.append(" "*i)
                else:
                    sub.append("")

            #Actually wrap and creat the string to return...stolen from internet
            lines=[textwrap.wrap(elt, width=num, subsequent_indent=ind) for elt,num,ind in zip(row,widths,sub)]
            for line in itertools.izip_longest(*lines,fillvalue=''):
                result.append(format_str.format(width=widths,row=line))
        return '\n'.join(result)





'''
Functions below: getTerminalSize
Author: http://stackoverflow.com/questions/566746/how-to-get-console-window-width-in-python
Author: Harco Kuppens
Downloaded 2/21/14
'''

def getTerminalSize():
   import platform
   current_os = platform.system()
   tuple_xy=None
   if current_os == 'Windows':
       tuple_xy = _getTerminalSize_windows()
       if tuple_xy is None:
          tuple_xy = _getTerminalSize_tput()
          # needed for window's python in cygwin's xterm!
   if current_os == 'Linux' or current_os == 'Darwin' or  current_os.startswith('CYGWIN'):
       tuple_xy = _getTerminalSize_linux()
   if tuple_xy is None:
       print "default"
       tuple_xy = (80, 25)      # default value
   return tuple_xy

def _getTerminalSize_windows():
    res=None
    try:
        from ctypes import windll, create_string_buffer

        # stdin handle is -10
        # stdout handle is -11
        # stderr handle is -12

        h = windll.kernel32.GetStdHandle(-12)
        csbi = create_string_buffer(22)
        res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
    except:
        return None
    if res:
        import struct
        (bufx, bufy, curx, cury, wattr,
         left, top, right, bottom, maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
        sizex = right - left + 1
        sizey = bottom - top + 1
        return sizex, sizey
    else:
        return None

def _getTerminalSize_tput():
    # get terminal width
    # src: http://stackoverflow.com/questions/263890/how-do-i-find-the-width-height-of-a-terminal-window
    try:
       import subprocess
       proc=subprocess.Popen(["tput", "cols"],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
       output=proc.communicate(input=None)
       cols=int(output[0])
       proc=subprocess.Popen(["tput", "lines"],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
       output=proc.communicate(input=None)
       rows=int(output[0])
       return (cols,rows)
    except:
       return None


def _getTerminalSize_linux():
    def ioctl_GWINSZ(fd):
        try:
            import fcntl, termios, struct, os
            cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ,'1234'))
        except:
            return None
        return cr
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        try:
            cr = (env['LINES'], env['COLUMNS'])
        except:
            return None
    return int(cr[1]), int(cr[0])

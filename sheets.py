
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter,LEDGER,ELEVENSEVENTEEN
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Image, Table, TableStyle, Frame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
# from PDFImage import PDFImage
from modparagraph import ModParagraph
import os
import Colorer

logger = Colorer.customLogger('root')

def main():
    logger.info("You are using default sheets.py")
    logger.info("You should check 'default.pdf' to see the output")

    s = Sheets(pagesize=letter)
    s.registerFont('cour')
    s.createBorder(.75*inch)
    s.createParagraph(u"Sample Centered Text<br />with Multiple Lines",space = 0, justify = 'center')
    s.createParagraph("Sample right justify...Notice the space", space=50, justify='right')
    s.createParagraph("Here is a <b>paragraph</b> with an indentation and a different font...notice it wraps around."+
        "Font is 18).",
        fontName='cour',indent = 0.5*inch, fontSize=18)
    s.createParagraph("Here is a <b>paragraph</b> with an indentation and a different font...notice it wraps around."+
        "Font is 18). It also has extra space after the first line",
        fontName='times',indent = 0.5*inch, fontSize=18, first_line_space=10)

    s.createLinedWrap("Text with no Line:","FILL TEXT 1...can wrap around to multiple lines...............",
        "Description 1", "Description 2", lines = 1)

    s.createParagraph("Left side of sheet")
    s.createParagraph("Use shift=False to not shift",shift=False,justify='right')

    data = ["12K017M3",
            "12K017M4",
            "12K017M5",
            "12K017M6",
            "12K017M7"]

    s.createTableFromList(data, fontSize = 14, fontName = 'times')

    s.createFrame("This is a frame! <br /> Look at me", drawBorder=True, frameJustify='center')

    s.save()

'''THIS was made for a very different project and does lots and lots of stuff...
but has some functionality I wanted...Adapting for your cards, but leaving in
random stuff'''


class Sheets():

    #Define default parameters parameters
    margin = inch
    fonts = ['arial', 'times']
    fn = 'default.pdf'
    pagesize = letter
    width, height = pagesize
    # mwidth = width - 2*margin
    # mheight = height - 2*margin
    pos = (0,0)

    #Get Styles
    styles = getSampleStyleSheet()

    def __init__(self,**kwargs):
        #Get the logger
        # self.logger = Colorer.customLogger('root')

        #Table of possible key values
        for key, value in kwargs.iteritems():
            if key == 'margin':
                self.margin = value
                self.compute_mdims()
            elif key == 'fonts':
                self.fonts = value
            elif key == 'fn':
                self.fn = value
            elif key == 'pagesize':
                self.set_pagesize(value)
            else:
                logger.critical("kwargs does not have a key %s in Sheets class"%key)
                raise Exception()

        self.compute_mdims()
        #Get the canvas
        self.c = canvas.Canvas(self.fn, pagesize = self.pagesize)

        #Get Fonts
        for font in self.fonts:
            self.registerFont(font)

        #Manage Styles
        for font in self.fonts:
            self.addStyles(font)

        #Set the position to the top of the page
        self.init_pos()

    def init_pos(self):
        self.pos = (self.margin, self.margin + self.mheight)

    def set_pagesize(self,pagesize):
        self.pagesize = pagesize
        self.width, self.height = pagesize
        self.compute_mdims()

    def compute_mdims(self):
        self.mwidth = self.width - 2*self.margin
        self.mheight = self.height - 2*self.margin

    def save(self):
        self.c.showPage()
        self.c.save()

    def registerFont(self, font):
        pdfmetrics.registerFont(TTFont(font, font + '.ttf'))
        pdfmetrics.registerFont(TTFont(font + 'bold',font +'bd.ttf'))
        pdfmetrics.registerFont(TTFont(font + 'italic',font +'i.ttf'))
        pdfmetrics.registerFont(TTFont(font + 'bolditalic',font +'bi.ttf'))
        pdfmetrics.registerFontFamily(font, normal=font,
            bold=font + 'bold',
            italic = font + "italic",
            boldItalic=font + 'bolditalic')

        if not font in self.fonts:
            self.fonts.append(font)
            self.addStyles(font)

    def createBorder(self, from_edge, thickness = 2, layers = 1, padding = 5):

        #Check the inputs
        if from_edge < 0:
            logger.critical("Sheets.createBorder...from_edge must be positive")
            raise Exception()
        elif thickness < 1:
            logger.critical("Sheets.createBorder...thickness must be at least 1")
            raise Exception()
        elif layers <1:
            logger.critical("Sheets.createBorder...layers must be at least 1")
            raise Exception()
        elif padding <1:
            logger.critical("Sheets.createBorder...padding must be at least 1")
            raise Exception()
        elif (layers-1)*padding > from_edge:
            logger.warning("sheets.create_border...too many layers and padding...outside of paper")

        #Save State
        self.c.saveState()

        #Set the thickness
        self.c.setLineWidth(thickness)

        #Loop through layers and add borders going outward
        for i in range(layers):
            self.c.rect(from_edge - padding*i,
                        from_edge - padding*i,
                        self.width - 2*from_edge + 2*padding*i,
                        self.height - 2*from_edge + 2*padding*i)

        #Restore the state
        self.c.restoreState()

    def addStyles(self, font, firstLineIndent=0, size = None):

        #Loop through the different Justification
        for justify in [TA_RIGHT,TA_LEFT,TA_CENTER,TA_JUSTIFY]:
            if justify == TA_RIGHT:
                just_n = 'right'
            elif justify == TA_LEFT:
                just_n = 'left'
            elif justify == TA_CENTER:
                just_n = 'center'
            elif justify == TA_JUSTIFY:
                just_n = 'justify'

            #Get the name of the style
            if firstLineIndent == 0:
                leader = font + just_n
            else:
                leader = str(firstLineIndent) + font + just_n

            #If they didnt specify the size...loop from 10 to 36 in specific steps
            if size is None:
                for ts in range(10,36,2):
                    try:
                        self.styles.add(ParagraphStyle(name=leader + str(ts),
                            fontName = font, fontSize = ts, leading = ts,
                            alignment = justify, firstLineIndent = firstLineIndent))
                    except:
                        pass
            #otherwise just add the 1 size
            else:
                try:
                    self.styles.add(ParagraphStyle(name=leader + str(size),
                            fontName = font, fontSize = size, leading = size,
                            alignment = justify, firstLineIndent = firstLineIndent))
                except:
                    pass


    def createParagraph(self, text, space = None, shift = True,
                        fontName = None, fontSize = 14, justify = 'left',
                        width = None, height = None, indent = None, first_line_space = None,
                        return_para=False):

        #Set defaults using class characteristics
        if space is None:
            space = fontSize

        if fontName is None:
            fontName = self.fonts[0]

        if width is None:
            width = self.mwidth

        if height is None:
            height = self.mheight

        try:
            self.addStyles(fontName, size=fontSize, firstLineIndent=indent)
            self.addStyles(fontName, size=fontSize)
        except:
            pass

        #Create paragraph
        if indent is None:
            p = ModParagraph(text, self.styles[fontName + justify + str(fontSize)])
        else:
            p = ModParagraph(text, self.styles[str(indent) + fontName + justify + str(fontSize)])


        if return_para:
            return p

        #Wrap paragraph and determine hieght
        if first_line_space is None:
            w, h = p.wrap(width, height)
        else:
            w, h = p.wrapWithUnderline(width, height, first_line_space)

        #If shift...we shift down to insert new text.
        if shift:
            self.shiftPos(h + space)

        #Draw it at the current position
        p.drawOn(self.c,self.pos[0],self.pos[1])

        return h

    def createTableFromList(self, data, numRow= 3, fontSize=14, fontName=None, shift=True, space=None):

        #Set defaults
        if fontName is None:
            fontName = self.fonts[0]
        if space is None:
            space = fontSize

        #Conver list to the list that table wants you to have
        tableData = []

        for i in range(numRow):
            tableData.append(data[i::numRow])

        #Create the table
        t = Table(tableData)

        #Set the font and size like you want to!
        t.setStyle(TableStyle([('FONT', (0, 0), (-1, -1), fontName),
                               ('FONTSIZE', (0, 0), (-1, -1), fontSize)]))

        #Get the height
        w ,h = t.wrapOn(self.c, 0, 0)

        if w > self.mwidth:
            logger.error("Table in Sheets.createTable has extened past margin...code is not smart enough to adjust...change your table.")

        #Shift if necessary
        if shift:
            self.shiftPos(h + space)

        #Draw it!
        t.drawOn(self.c,self.pos[0],self.pos[1])

    def createTable(self,data,fontSize=14, fontName=None, shift = True, space = None, style=None,
        colWidths=None):
        #Set defaults
        if fontName is None:
            fontName = self.fonts[0]
        if space is None:
            space = fontSize

        #Create the table
        t = Table(data,colWidths = colWidths)

        #Set the font and size like you want to!
        if style is None:
            t.setStyle(TableStyle([('FONT', (0, 0), (-1, -1), fontName),
                                   ('FONTSIZE', (0, 0), (-1, -1), fontSize)]))
        else:
            t.setStyle(style)

        #Get the height
        w ,h = t.wrapOn(self.c, 0, 0)

        if w > self.mwidth:
            logger.error("Table in Sheets.createTable has extened past margin...code is not smart enough to adjust...change your table.")

        #Shift if necessary
        if shift:
            self.shiftPos(h + space)

        #Draw it!
        t.drawOn(self.c,self.pos[0],self.pos[1])



    def createImage(self, fn, aspect = None, width=None, height=None, indent=None, padding=10, shift=True,
        return_image=False):
        _,file_extension = os.path.splitext(fn)
        if file_extension.lower().strip() == '.pdf':
            logger.critical('Doesnt WORK ON PDFS yet')
            raise

        #Get image dimensions
        img = ImageReader(fn)
        iw, ih = img.getSize()

        #Set parameters
        if aspect is None:
            if width is None and height is None:
                width = iw
                height = ih
            elif height is None:
                aspect = float(ih)/float(iw)
                height = aspect*width
            elif width is None:
                aspect = float(iw)/float(ih)
                width = aspect*height
        else:
            width = iw*aspect
            height = ih*aspect

        if height > self.mheight:
            logger.warning('Image is taller than the entire page')
        if width + (indent or 0.0) > self.mwidth:
            logger.warning('Entering side margin...check')


        i = Image(fn,width = width, height = height)

        if return_image:
            return i

        #Shif down before adding to make room
        if shift:
            self.shiftPos(height + padding)

        #Indent if necessary
        if not indent is None:
            self.c.saveState()
            self.c.translate(indent,0)

        #Draw the image
        i.drawOn(self.c,self.pos[0],self.pos[1])

        #Restore if needed
        if not indent is None:
            self.c.restoreState()

        return width, height

    def shiftPos(self, distance):
        self.pos = (self.pos[0], self.pos[1] - distance)

    def createHLine(self, space = 24, thickness = 1, shift = True, width = None, start = None):
        #Save State
        self.c.saveState()

        #Set the thickness
        self.c.setLineWidth(thickness)

        #Shift if necessary
        if shift:
            self.shiftPos(space)

        #Default inputs
        if width is None:
            width = self.mwidth

        if start is None:
            start = self.pos
        else:
            start = (start[0] + self.pos[0], -start[1] + self.pos[1])

        #Create Line
        self.c.line(start[0],start[1],start[0] + width,start[1])

        #Restore the state
        self.c.restoreState()

    def createFrame(self,text,width=2*inch,height=2*inch,drawBorder=False,
        textJustify='left',frameJustify='left',fontSize=14, fontName=None, space=None, shift=True):
        #Set the defaults
        if fontName is None:
            fontName = self.fonts[0]
        if space is None:
            space = fontSize

        #Create paragraph but put in list of story
        story = []
        story.append(self.createParagraph(text,return_para=True,fontSize=fontSize, fontName=fontName,
            justify=textJustify))

        #Shift vertically if we need to
        if shift:
            self.shiftPos(height + space)

        #Worry about box justification
        if frameJustify == 'left':
            start = self.pos[0]
        elif frameJustify == 'right':
            start = self.pos[0] + self.mwidth - width
        elif frameJustify == 'center':
            start = self.pos[0] + self.mwidth/2 - width/2
        else:
            logger.error("Error in sheets.createFrame...frameJustify has invalid input")

        if drawBorder:
            f = Frame(start,self.pos[1], width,height,showBoundary=1)
        else:
            f = Frame(start,self.pos[1], width,height,showBoundary=0)

        #Create frame on page
        f.addFromList(story,self.c)

    def getStringLength(self,string, fontName=None, fontSize=14):

        #Set defaults
        if fontName is None:
            fontName = self.fonts[0]

        return pdfmetrics.stringWidth(string, fontName, fontSize)




    def createLinedWrap(self, text1 = "", text2="", text3="", text4 = "", lines=1,
                        fontName=None, fontSize=14, smallSize=10, buff=5, underline=1.5):
        #Set Defaults
        if fontName is None:
            fontName = self.fonts[0]

        #Find width of leader string
        # width = pdfmetrics.stringWidth(text1 + " ", fontName, fontSize)
        width = self.getStringLength(text1 + " ", fontName=fontName, fontSize=fontSize)

        #Create the leader text
        self.createParagraph(text1, fontName = fontName, fontSize = fontSize)

        #Create the subtext
        self.c.saveState()
        self.c.translate(0, -smallSize)
        self.createParagraph(text3, fontName=fontName, fontSize=smallSize, shift=False)
        self.createParagraph(text4, fontName=fontName, fontSize=smallSize, shift=False,indent=width)
        self.c.restoreState()

        #We always have to make a shortened first line
        self.c.saveState()
        self.c.translate(0,-underline)
        self.createHLine(shift = False,
                         start=(width,0),
                         width=self.mwidth - width)
        self.c.restoreState()


        #Create the wrap text
        h = self.createParagraph(text2, space=-fontSize,
            fontName=fontName, fontSize=fontSize, indent=width,
            first_line_space = smallSize + buff)

        #Find number of paragraph lines:
        numLines = int((h - smallSize - buff)/fontSize)

        #Create necessary Lines:
        self.c.saveState()
        self.c.translate(0,-underline)
        j = -1
        for i in range(numLines-1):
            self.createHLine(shift=False)
            self.c.translate(0,fontSize)
            j = i
        self.c.restoreState()

        #Check to see if we made enough
        if lines < numLines:
            logger.warning("Sheets.createLinedWrap...You specified less thans then necessary...creating lines")
        elif lines > numLines:
            #If we didnt...make some more!
            self.c.saveState()
            self.c.translate(0,-underline)
            for i in range(lines - numLines):
                self.createHLine(space = fontSize)
            self.c.restoreState()

if __name__ == '__main__':
    main()

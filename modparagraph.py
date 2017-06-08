__version__=''' $Id$ '''
__doc__='''The standard paragraph implementation'''
from string import join, whitespace
from operator import truth
from types import StringType, ListType
from unicodedata import category
from reportlab.pdfbase.pdfmetrics import stringWidth, getFont, getAscentDescent
from reportlab.platypus.paraparser import ParaParser
from reportlab.platypus.flowables import Flowable
from reportlab.lib.colors import Color
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.utils import _className
from reportlab.lib.geomutils import normalizeTRBL
from reportlab.lib.textsplit import wordSplit, ALL_CANNOT_START
from copy import deepcopy
from reportlab.lib.abag import ABag
from reportlab.rl_config import platypus_link_underline
from reportlab import rl_config
import re
from reportlab.platypus import Paragraph
from reportlab.platypus.paragraph import *
from reportlab.platypus.paragraph import _leftDrawParaLine
from reportlab.platypus.paragraph import _leftDrawParaLineX
from reportlab.platypus.paragraph import _rightDrawParaLine
from reportlab.platypus.paragraph import _rightDrawParaLineX
from reportlab.platypus.paragraph import _centerDrawParaLineX
from reportlab.platypus.paragraph import _centerDrawParaLine
from reportlab.platypus.paragraph import _do_post_text
from reportlab.platypus.paragraph import _justifyDrawParaLine
from reportlab.platypus.paragraph import _justifyDrawParaLineX
from reportlab.platypus.paragraph import _do_under_line
from reportlab.platypus.paragraph import _do_link_line
from reportlab.platypus.paragraph import _drawBullet


'''
This file is used to create a new class based on the platypus Paragraph function.
It's primary purpose is to allow for an additional space between the first and second
lines of a paragraph.  This is handy when using descriptions for the fields.
It adds a new property: firstLineSpace - this is added to leading on the first line when
wrapWithUnderline is called.
It adds new function: wrapWithUnderline.  This is used to set the firstLineSpace to get the
proper height of the paragraph.  Almost direct copy from wrap method.
It overwhrites drawPara.  Again, all I changed was the adding of the leading in 2 places
'''




class ModParagraph(Paragraph):
    firstLineSpace = None
    def wrapWithUnderline(self,availWidth,availHeight, firstLineSpace):
        #Call self.wrap()
        self.wrap(availWidth, availHeight)

        #Add firstLineSpace to Height
        self.height += firstLineSpace

        #Set Parameters
        self.firstLineSpace = firstLineSpace

        #Return same thing sa self.wrap
        return self.width, self.height

    def drawPara(self,debug=0):
        """Draws a paragraph according to the given style.
        Returns the final y position at the bottom. Not safe for
        paragraphs without spaces e.g. Japanese; wrapping
        algorithm will go infinite."""

        #stash the key facts locally for speed
        canvas = self.canv
        style = self.style
        blPara = self.blPara
        lines = blPara.lines
        leading = style.leading
        autoLeading = getattr(self,'autoLeading',getattr(style,'autoLeading',''))

        #work out the origin for line 1
        leftIndent = style.leftIndent
        cur_x = leftIndent

        if debug:
            bw = 0.5
            bc = Color(1,1,0)
            bg = Color(0.9,0.9,0.9)
        else:
            bw = getattr(style,'borderWidth',None)
            bc = getattr(style,'borderColor',None)
            bg = style.backColor

        #if has a background or border, draw it
        if bg or (bc and bw):
            canvas.saveState()
            op = canvas.rect
            kwds = dict(fill=0,stroke=0)
            if bc and bw:
                canvas.setStrokeColor(bc)
                canvas.setLineWidth(bw)
                kwds['stroke'] = 1
                br = getattr(style,'borderRadius',0)
                if br and not debug:
                    op = canvas.roundRect
                    kwds['radius'] = br
            if bg:
                canvas.setFillColor(bg)
                kwds['fill'] = 1
            bp = getattr(style,'borderPadding',0)
            tbp, rbp, bbp, lbp = normalizeTRBL(bp)
            op(leftIndent - lbp,
                        -bbp,
                        self.width - (leftIndent+style.rightIndent) + lbp+rbp,
                        self.height + tbp+bbp,
                        **kwds)
            canvas.restoreState()

        nLines = len(lines)
        bulletText = self.bulletText
        if nLines > 0:
            _offsets = getattr(self,'_offsets',[0])
            _offsets += (nLines-len(_offsets))*[_offsets[-1]]
            canvas.saveState()
            #canvas.addLiteral('%% %s.drawPara' % _className(self))
            alignment = style.alignment
            offset = style.firstLineIndent+_offsets[0]
            lim = nLines-1
            noJustifyLast = not (hasattr(self,'_JustifyLast') and self._JustifyLast)

            if blPara.kind==0:
                if alignment == TA_LEFT:
                    dpl = _leftDrawParaLine
                elif alignment == TA_CENTER:
                    dpl = _centerDrawParaLine
                elif self.style.alignment == TA_RIGHT:
                    dpl = _rightDrawParaLine
                elif self.style.alignment == TA_JUSTIFY:
                    dpl = _justifyDrawParaLine
                f = blPara
                if rl_config.paraFontSizeHeightOffset:
                    cur_y = self.height - f.fontSize
                else:
                    cur_y = self.height - getattr(f,'ascent',f.fontSize)
                if bulletText:
                    offset = _drawBullet(canvas,offset,cur_y,bulletText,style)

                #set up the font etc.
                canvas.setFillColor(f.textColor)

                tx = self.beginText(cur_x, cur_y)
                if autoLeading=='max':
                    leading = max(leading,blPara.ascent-blPara.descent)
                elif autoLeading=='min':
                    leading = blPara.ascent-blPara.descent

                #now the font for the rest of the paragraph

                #----------------------DAVID ADDDED THESE LINES------------------------
                if not self.firstLineSpace is None:
                    tx.setFont(f.fontName, f.fontSize, leading + self.firstLineSpace)
                else:
                    tx.setFont(f.fontName, f.fontSize, leading)
                #----------------------------------------------------------------------


                ws = lines[0][0]
                t_off = dpl( tx, offset, ws, lines[0][1], noJustifyLast and nLines==1)

                #----------------------DAVID ADDDED THESE LINES------------------------
                tx.setFont(f.fontName, f.fontSize, leading)
                #----------------------------------------------------------------------

                if f.underline or f.link or f.strike or style.endDots:
                    xs = tx.XtraState = ABag()
                    xs.cur_y = cur_y
                    xs.f = f
                    xs.style = style
                    xs.lines = lines
                    xs.underlines=[]
                    xs.underlineColor=None
                    xs.strikes=[]
                    xs.strikeColor=None
                    xs.links=[]
                    xs.link=f.link
                    xs.textColor = f.textColor
                    xs.backColors = []
                    canvas.setStrokeColor(f.textColor)
                    dx = t_off+leftIndent
                    if dpl!=_justifyDrawParaLine: ws = 0
                    underline = f.underline or (f.link and platypus_link_underline)
                    strike = f.strike
                    link = f.link
                    if underline: _do_under_line(0, dx, ws, tx)
                    if strike: _do_under_line(0, dx, ws, tx, lm=0.125)
                    if link: _do_link_line(0, dx, ws, tx)
                    if noJustifyLast and nLines==1 and style.endDots and dpl!=_rightDrawParaLine: _do_dots(0, dx, ws, xs, tx, dpl)

                    #now the middle of the paragraph, aligned with the left margin which is our origin.
                    for i in xrange(1, nLines):
                        ws = lines[i][0]
                        t_off = dpl( tx, _offsets[i], ws, lines[i][1], noJustifyLast and i==lim)
                        dx = t_off+leftIndent
                        if dpl!=_justifyDrawParaLine: ws = 0
                        if underline: _do_under_line(i, dx, ws, tx)
                        if strike: _do_under_line(i, dx, ws, tx, lm=0.125)
                        if link: _do_link_line(i, dx, ws, tx)
                        if noJustifyLast and i==lim and style.endDots and dpl!=_rightDrawParaLine: _do_dots(i, dx, ws, xs, tx, dpl)
                else:
                    for i in xrange(1, nLines):
                        dpl( tx, _offsets[i], lines[i][0], lines[i][1], noJustifyLast and i==lim)
            else:
                f = lines[0]
                if rl_config.paraFontSizeHeightOffset:
                    cur_y = self.height - f.fontSize
                else:
                    cur_y = self.height - getattr(f,'ascent',f.fontSize)
                # default?
                dpl = _leftDrawParaLineX
                if bulletText:
                    oo = offset
                    offset = _drawBullet(canvas,offset,cur_y,bulletText,style)
                if alignment == TA_LEFT:
                    dpl = _leftDrawParaLineX
                elif alignment == TA_CENTER:
                    dpl = _centerDrawParaLineX
                elif self.style.alignment == TA_RIGHT:
                    dpl = _rightDrawParaLineX
                elif self.style.alignment == TA_JUSTIFY:
                    dpl = _justifyDrawParaLineX
                else:
                    raise ValueError("bad align %s" % repr(alignment))

                #set up the font etc.
                tx = self.beginText(cur_x, cur_y)
                xs = tx.XtraState=ABag()
                xs.textColor=None
                xs.backColor=None
                xs.rise=0
                xs.underline=0
                xs.underlines=[]
                xs.underlineColor=None
                xs.strike=0
                xs.strikes=[]
                xs.strikeColor=None
                xs.backColors=[]
                xs.links=[]
                xs.link=None

                #----------------------DAVID ADDDED THESE LINES------------------------
                if not self.firstLineSpace is None:
                    xs.leading =  style.leading + self.firstLineSpace
                else:
                    xs.leading = style.leading
                #----------------------------------------------------------------------

                xs.leftIndent = leftIndent
                tx._leading = None
                tx._olb = None
                xs.cur_y = cur_y
                xs.f = f
                xs.style = style
                xs.autoLeading = autoLeading

                tx._fontname,tx._fontsize = None, None
                dpl( tx, offset, lines[0], noJustifyLast and nLines==1)
                _do_post_text(tx)


                #----------------------DAVID ADDDED THESE LINES------------------------
                xs.leading = style.leading
                #----------------------------------------------------------------------

                #now the middle of the paragraph, aligned with the left margin which is our origin.
                for i in xrange(1, nLines):
                    f = lines[i]
                    dpl( tx, _offsets[i], f, noJustifyLast and i==lim)
                    _do_post_text(tx)

            canvas.drawText(tx)
            canvas.restoreState()

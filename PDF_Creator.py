# %% Import important libraries that you'll need
from reportlab.lib.pagesizes import LEDGER,ELEVENSEVENTEEN,letter
import logging
from sheets import Sheets
from reportlab.lib.units import inch,mm
import os
import glob
logger = logging.getLogger('root')

# Change to DEBUG for more messages, and WARNING for less messages
logger.setLevel(logging.getLevelName('INFO'))

# %% Main Function...this is where you change things
def main():
    # Inputs you may need to change
    card_image_folder = 'Deck 1'
    output_pdf_FN = 'OCEASUCKS.pdf'
    pagesize = LEDGER #I only have
                               #letter, LEDGER, and ELEVENSEVENTEEN as options
                               # but more exist, LEDGER is 17x11
    margin = 0.15*inch #You can use mm if you want, but has to have the * like: 3*mm
                       #This is the margin to the edge of the page.  I assume
                       #constant for all sides.
    card_width = 2.5*inch
    card_height = 3.5*inch
    cut_space = 1*mm #Space between images

    # This is where I make the PDF sheet object...no need to mess with this.
    sheet = add_cards(fn=output_pdf_FN,card_width=card_width,
        card_height=card_height, cut_space=cut_space,margin=margin,
        pagesize=pagesize)

    # Here is where you add pictures...there are lots of ways to do this, I'll
    # show some examples here.  You only need to do one of the methods,
    #but you can do whatever you want. I've given you several methods to help you out

    # Get all the cards in the folder and do that
    add_by_pattern(sheet,card_image_folder,'*.jpg',multiplyer=4) # Gets all the JPG in the folder

    # If you were clever with your file names you could do something like:
    # add_by_pattern(sheet,card_image_folder,'course*.jpg')

    # You can also just make a list of files (this could be repeats too):
    #fns = ['swords-to-plowshares-15015-medium.jpg',
    #     'ambush-party-24415-medium.jpg']

    # add_by_path_list(sheet,card_image_folder,fns)

    #Using the same method above, you could repeat 1 or more cards lots of times
    # fns = ['swords-to-plowshares-15015-medium.jpg']*20

    # add_by_path_list(sheet,card_image_folder,fns)

    # Add all the images in a folder
    # for i in range(32):
    #     sheet.draw_single_card(os.path.join(card_image_folder,'swords-to-plowshares-15015-medium.jpg'))

    #This always needs to be here to save
    sheet.save()
    logger.info('Ouput saved to %s'%(output_pdf_FN))


# %% Functions I made
def add_by_pattern(sheet_obj,card_path,pattern,multiplyer=1):
    fn_list = glob.glob(os.path.join(card_path,pattern))
    draw_fnlist(sheet_obj,fn_list*multiplyer)

def add_by_path_list(sheet_obj,card_path,fn_list):
    new_fns = []
    for fn in fn_list:
        new_fns.append(os.path.join(card_path,fn))
    draw_fnlist(sheet_obj,new_fns)
    return new_fns

def draw_fnlist(sheet_obj,fn_list):
    logger.info('Number of files in list: %d'%(len(fn_list)))
    for fn in fn_list:
        sheet_obj.draw_single_card(fn)

class add_cards(Sheets):
    def __init__(
        self,cut_space=1*mm, card_width=2.5*inch,card_height=3.5*inch,**kwargs):

        # Call Super
        Sheets.__init__(self, **kwargs)

        # Copy values
        self.cut_space = cut_space
        self.indent_space = 0.0
        self.card_width=card_width
        self.card_height=card_height

        #Perform initial shift to make sure we're at the right spot...not robust.
        self.shiftPos(self.card_height)


    # Leverage the Sheets.createImage with the proper inputs to wrap around.
    def draw_single_card(self,fn):
        shift = self.checkSideFit(self.card_width)
        padding = self.cut_space
        if shift:
            if self.checkBadPos(self.card_height + self.cut_space):
                self.new_page()
                padding = 0.0

        self.createImage(
            fn = fn,
            width=self.card_width,
            height=self.card_height,
            indent=self.indent_space,
            padding=padding,
            shift=shift)

        self.indent_space += self.card_width + self.cut_space


    # Checks to see if we've reached the end of a line
    def checkSideFit(self,width):
        if self.indent_space + width > self.mwidth:
            logger.debug('Didnt fit at end, starting new line')
            self.indent_space = 0.0
            return True
        else:
            return False

    def checkBadPos(self,distance):
        if self.pos[1] - distance < self.margin:
            return True
    def new_page(self):
        logger.debug('Starting New Page')
        self.c.showPage()
        self.init_pos()


# %%
if __name__ == '__main__':
    main()

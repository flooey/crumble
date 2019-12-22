import Image, ImageDraw, crumble

#FORMAT = 'L'
#BLACK = 0
#WHITE = 255
#NORMAL_OUTLINE = 127
#CAPTURE_OUTLINE = 127
#SOURCE_OUTLINE = 127
#DEST_OUTLINE = 127
FORMAT = 'RGB'
BLACK = "#000000"
WHITE = "#FFFFFF"
NORMAL_OUTLINE = "#7F7F7F"
CAPTURE_OUTLINE = "#FF0000"
SOURCE_OUTLINE = "#00CCCC"
DEST_OUTLINE = "#CCCC00"
SWAP_OUTLINE = "#FF7F00"

THIN_OUTLINE_WIDTH = 1
THICK_OUTLINE_WIDTH = 3
ALWAYS_SHOW_NORMAL_OUTLINE = True

class CrumbleVisualizer:
    def __init__(self,
                 black=BLACK,
                 white=WHITE,
                 normal_outline=NORMAL_OUTLINE,
                 capture_outline=CAPTURE_OUTLINE,
                 source_outline=SOURCE_OUTLINE,
                 dest_outline=DEST_OUTLINE,
                 swap_outline=SWAP_OUTLINE,
                 thin_width=THIN_OUTLINE_WIDTH,
                 thick_width=THICK_OUTLINE_WIDTH):
        self.black = black
        self.white = white
        self.normal_outline = normal_outline
        self.capture_outline = capture_outline
        self.source_outline = source_outline
        self.dest_outline = dest_outline
        self.swap_outline = swap_outline
        self.thin_width = thin_width
        self.thick_width = thick_width

    def setNormalOnly(self):
        self.capture_outline = self.normal_outline
        self.source_outline = self.normal_outline
        self.dest_outline = self.normal_outline
        self.swap_outline = self.normal_outline
        self.thick_width = self.thin_width
    
    def draw(self, board, filename, size=400):
        size = size / crumble.BOARD_LENGTH * crumble.BOARD_LENGTH
        im = Image.new(FORMAT, (size, size))
        draw = ImageDraw.Draw(im)
        mult = size / crumble.BOARD_LENGTH
        for p in board.pieces():
            if p.color == 'b':
                fill = self.black
            else:
                fill = self.white
            if p in board._lastcaptures:
                outline = self.capture_outline
                ow = self.thick_width
            elif p in board._lastdests:
                outline = self.dest_outline
                ow = self.thick_width
            elif p in board._lastsources:
                outline = self.source_outline
                ow = self.thick_width
            elif p in board._lastswaps:
                outline = self.swap_outline
                ow = self.thick_width
            else:
                outline = self.normal_outline
                ow = self.thin_width
            lowX, lowY = p.x * mult, (crumble.BOARD_LENGTH - p.y - p.height) * mult
            highX, highY = (p.x + p.width) * mult - 1, (crumble.BOARD_LENGTH - p.y) * mult - 1
            draw.rectangle((lowX, lowY, highX, highY), fill=outline, outline=outline)
            draw.rectangle((lowX + ow, lowY + ow, highX - ow, highY - ow), fill=fill, outline=fill)
            if ALWAYS_SHOW_NORMAL_OUTLINE:
                draw.rectangle((lowX, lowY, highX, highY), outline=self.normal_outline)
    #        draw.rectangle(((p.x * mult, (crumble.BOARD_LENGTH - p.y) * mult - OUTLINE_WIDTH), ((p.x + p.width) * mult - OUTLINE_WIDTH, (crumble.BOARD_LENGTH - p.y - p.height) * mult)), outline=outline, fill=fill)
        im.save(filename)

def draw(board, filename, size=400):
    CrumbleVisualizer().draw(board, filename, size)

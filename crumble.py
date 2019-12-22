import re

UNIT_LENGTH = 8
PIECES_PER_SIDE = 6
BOARD_LENGTH = PIECES_PER_SIDE * UNIT_LENGTH

class Board:
    def __init__(self):
        self._pieces = []
        self._board = [None] * BOARD_LENGTH
        self._mover = "b"
        self._winner = None
        self._lastsources = []
        self._lastdests = []
        self._lastcaptures = []
        self._lastswaps = []
        self._turn = 0
        for i in range(BOARD_LENGTH):
            self._board[i] = [None] * BOARD_LENGTH
        width = UNIT_LENGTH
        color = "w"
        for i in range(PIECES_PER_SIDE):
            for j in range(PIECES_PER_SIDE):
                Piece(self, i * width, j * width, width, width, color)
                if color == "w":
                    color = "b"
                else:
                    color = "w"
            if color == "w":
                color = "b"
            else:
                color = "w"

    def parse(self, command):
        command = command.upper().replace(' ', '').replace('\t', '').replace('\n', '')
        if len(command) == 0:
            return
        if self._winner:
            raise IllegalMove, "Game has been won."
        self._lastsources = []
        self._lastdests = []
        self._lastcaptures = []
        self._lastswaps = []
        origcommand = command
        m = re.match(r'\d+(,\d+)*[HJV]', command)
        if not m:
            raise IllegalMove, "Did not find initial split or join in %s" % origcommand
        piece, command = self._findPiece(command[:m.end() - 1]), command[m.end() - 1:]
        if command[0] == 'J':
            m = re.match(r'J\d+,\d+', command)
            if not m:
                raise IllegalMove, "Did not find join specification in %s" % command
            piecespec, command = command[1:m.end()], command[m.end():]
            swappingPiece = self._processJoin(piece, piecespec)
        elif command[0] == 'H' or command[0] == 'V':
            if '-' in command:
                if command[1] in "123456789":    # This is a multi-split
                    dir, command = command[0], command[1:]
                    command = command.split('-')
                    splitspec, piecespec, command = command[0], command[1], command[2]
                    swappingPiece = self._multiSplit(piece, dir, splitspec, piecespec)
                else:                            # This is a split with a piece specification
                    if command[2] != '-':
                        raise IllegalMove, "Illegal piece specification in %s" % origcommand
                    dir, piecespec, command = command[0], command[1], command[3:]
                    swappingPiece = self._simpleSplit(piece, dir, piecespec, command)
            else:
                dir, command = command[0], command[1:]
                if len(command) > 0 and command[0] in "123456789":  # This is a multi-split
                    swappingPiece, command = self._multiSplit(piece, dir, command, None), ""
                else:
                    swappingPiece = self._simpleSplit(piece, dir, None, command)
        else:
            raise IllegalMove, "Invalid action specification in %s" % origcommand
        self._swapChain(swappingPiece, command)
        if self._mover == 'w':
            self._mover = 'b'
        else:
            self._mover = 'w'
        self._turn += 1

    def _followVertexes(self, spec, startX, startY):
        pieceLocation = spec.split(',')
        goingUp = False
        curX, curY = startX, startY
        for l in pieceLocation:
            for i in range(int(l)):
                if goingUp:
                    # If we're on the board edge already, this will take us over
                    if curY == BOARD_LENGTH:
                        raise IllegalMove, "Vertex specification went off board in %s" % spec
                    if curX == 0:
                        p1 = p2 = self._board[curX][curY]
                    elif curX == BOARD_LENGTH:
                        p1 = p2 = self._board[curX-1][curY]
                    else:
                        p1 = self._board[curX-1][curY]
                        p2 = self._board[curX][curY]
                    curY = min(p1.height + p1.y, p2.height + p2.y)
                else:
                    # If we're on the board edge already, this will take us over
                    if curX == BOARD_LENGTH:
                        raise IllegalMove, "Vertex specification went off board in %s" % spec
                    if curY == 0:
                        p1 = p2 = self._board[curX][curY]
                    elif curY == BOARD_LENGTH:
                        p1 = p2 = self._board[curX][curY-1]
                    else:
                        p1 = self._board[curX][curY-1]
                        p2 = self._board[curX][curY]
                    curX = min(p1.width + p1.x, p2.width + p2.x)
            goingUp = not goingUp
        return (curX, curY)
        
    def _findPiece(self, spec, startX=0, startY=0):
        x, y = self._followVertexes(spec, startX, startY)
        if x >= BOARD_LENGTH or y >= BOARD_LENGTH:
            raise IllegalMove, "Location spec went off board in %s" % spec
        piece = self._board[x][y]
        if piece.x != x or piece.y != y:
            raise IllegalMove, "Location spec did not result in corner of piece in %s" % spec
        if piece.color != self._mover:
            raise IllegalMove, "Location spec resulted in other player's piece in %s" % spec
        return piece

    def _simpleSplit(self, piece, dir, piecespec, command):
        if self._mover != piece.color:
            raise IllegalMove, "Attempted to split opponent's piece."
        if dir == 'H':
            piece = piece.splitH()
            self._lastsources.append(piece)
            self._lastsources.append(self._board[piece.x][piece.y + piece.height])
            if len(command) > 0:
                if command[0] == 'N' or piecespec == 'N':
                    if piecespec and piecespec != 'N':
                        raise IllegalMove, "Invalid piece selector for H split and N swap: %s" % piecespec
                    piece = self._board[piece.x][piece.y + piece.height]
                elif command[0] == 'S' or piecespec == 'S':
                    if piecespec and piecespec != 'S':
                        raise IllegalMove, "Invalid piece selector for H split and S swap: %s" % piecespec
                else:
                    raise IllegalMove, "Horizontal split followed by E or W swap must specify swapping piece."
        elif dir == 'V':
            piece = piece.splitV()
            self._lastsources.append(piece)
            self._lastsources.append(self._board[piece.x + piece.width][piece.y])
            if len(command) > 0:
                if command[0] == 'E' or piecespec == 'E':
                    if piecespec and piecespec != 'E':
                        raise IllegalMove, "Invalid piece selector for V split and E swap: %s" % piecespec
                    piece = self._board[piece.x + piece.width][piece.y]
                elif command[0] == 'W' or piecespec == 'W':
                    if piecespec and piecespec != 'W':
                        raise IllegalMove, "Invalid piece selector for V split and W swap: %s" % piecespec
                else:
                    raise IllegalMove, "Vertical split followed by N or S swap must specify swapping piece."
        else:
            raise IllegalMove, "Invalid split direction %s" % dir
        return piece

    def _multiSplit(self, piece, dir, splitspec, piecespec):
        try:
            pieceno = int(splitspec)
        except ValueError:
            raise IllegalMove, "Multi-split length specification of %s is not an integer" % splitspec
        if pieceno < 2:
            raise IllegalMove, "Multi-split length specification of %s must be at least 2" % splitspec
        if not (piecespec is None or piecespec[0] in '0123456789'):
            raise IllegalMove, "Multi-split swapping piece specification of %s is not an integer" % piecespec[0]
        if dir == 'H':
            if not (piecespec is None or piecespec[1] == 'S' or piecespec[1] == 'N'):
                raise IllegalMove, "Horizontal multi-split must select a piece by N or S"
            if piecespec is None:
                target, piecespec = 1, "S"
            else:
                target, piecespec = int(piecespec[0]), piecespec[1]
            curX, curY = piece.x, piece.y + piece.height / 2
            for i in range(1, pieceno + 1):
                if curY != self._board[curX][curY].y + self._board[curX][curY].height / 2:
                    raise IllegalMove, "Multi-split encountered invalid split."
                result = self._simpleSplit(self._board[curX][curY], 'H', piecespec, piecespec)
                if i == target:
                    resultingPiece = result
                if i != pieceno:
                    curX += result.width
                    while self._board[curX][curY].y == curY:
                        curX += self._board[curX][curY].width
        elif dir == 'V':
            if not (piecespec is None or piecespec[1] == 'W' or piecespec[1] == 'E'):
                raise IllegalMove, "Vertical multi-split must select a piece by E or W"
            if piecespec is None:
                target, piecespec = 1, "W"
            else:
                target, piecespec = int(piecespec[0]), piecespec[1]
            curX, curY = piece.x + piece.width / 2, piece.y
            for i in range(1, pieceno + 1):
                if curX != self._board[curX][curY].x + self._board[curX][curY].width / 2:
                    raise IllegalMove, "Multi-split encoutered invalid split."
                result = self._simpleSplit(self._board[curX][curY], 'V', piecespec, piecespec)
                if i == target:
                    resultingPiece = result
                if i != pieceno:
                    curY += result.height
                    while self._board[curX][curY].x == curX:
                        curY += self._board[curX][curY].height
        else:
            raise IllegalMove, "Invalid split direction %s" % dir
        return resultingPiece

    def _swapChain(self, piece, spec):
        self._lastswaps.append(piece)
        for dir in spec:
            piece = piece.swap(dir)
            self._lastswaps.append(piece)
            self._clearCaptures()
            self._checkForVictory()
        self._lastdests.append(piece)

    def _processJoin(self, piece, spec):
        if re.match(r"^\d+,\d+$", spec) is None:
            raise IllegalMove, "Join specification %s did not provide two values" % spec
        topX, topY = self._followVertexes(spec, piece.x, piece.y)
        piece = piece.join(topX, topY)
        self._lastsources.append(piece)
        return piece

    def _clearCaptures(self):
        marked = []
        for p in self._pieces:
            if p.x == 0 or p.y == 0 or (p.x + p.width) == BOARD_LENGTH or (p.y + p.height) == BOARD_LENGTH:
                marked.append(p)
        for p in marked:
            for n in p.neighbors():
                if n.color == p.color and n not in marked:
                    marked.append(n)
        for p in self._pieces:
            if p not in marked:
                p.capture()
                self._lastcaptures.append(p)

    def _checkForVictory(self, player=None):
        if player is None:
            self._checkForVictory('b')
            self._checkForVictory('w')
            return
        initial = self._board[0][0]
        while initial:
            marked = []
            west, north, east = False, False, False
            if initial.color == player:
                marked.append(initial)
                for p in marked:
                    if p.x == 0:
                        west = True
                    if p.x + p.width == BOARD_LENGTH:
                        east = True
                    if p.y + p.height == BOARD_LENGTH:
                        north = True
                    for n in p.full_neighbors():
                        if n.color == player and n not in marked:
                            marked.append(n)
                if west and north and east:
                    self._winner = player
                    return
            if initial.x + initial.width == BOARD_LENGTH:
                initial = None
            else:
                initial = self._board[initial.x + initial.width][0]

    def pieceAt(self, x, y):
        return self._board[x][y]
        
    def pieces(self):
        return self._pieces

    def turn(self):
        return self._turn

    def mover(self):
        return self._mover

    def winner(self):
        return self._winner

class Piece:
    def __init__(self, board, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        if board is not None:
            self.board = board
            board._pieces.append(self)
            for i in range(x, x + width):
                for j in range(y, y + height):
                    board._board[i][j] = self

    def splitH(self):
        if not ((self.width == self.height) or (self.width == self.height / 2)):
            raise IllegalMove, "Resulting piece would not be proper dimensions."
        self.board._pieces.remove(self)
        Piece(self.board, self.x, self.y + self.height / 2, self.width, self.height / 2, self.color)
        return Piece(self.board, self.x, self.y, self.width, self.height / 2, self.color)

    def splitV(self):
        if not ((self.width == self.height) or (self.width / 2== self.height)):
            raise IllegalMove, "Resulting piece would not be proper dimensions."
        self.board._pieces.remove(self)
        Piece(self.board, self.x + self.width / 2, self.y, self.width / 2, self.height, self.color)
        return Piece(self.board, self.x, self.y, self.width / 2, self.height, self.color)

    def join(self, topX, topY):
        width, height = topX - self.x, topY - self.y
        if not ((width == height) or (width == height / 2) or (width / 2 == height)):
            raise IllegalMove, "Resulting piece would not be proper dimensions (%d, %d)" % (width, height)
        for p in filter(lambda p : p.x >= self.x and p.y >= self.y and p.x < topX and p.y < topY, self.board._pieces):
            if p.color != self.color:
                raise IllegalMove, "Join spec includes piece belonging to opponent."
        self.board._pieces = filter(lambda p : p.x < self.x or p.y < self.y or p.x >= topX or p.y >= topY, self.board._pieces)
        return Piece(self.board, self.x, self.y, width, height, self.color)

    def swap(self, direction):
        if self.board._winner:
            raise IllegalMove, "Game has been won."
        if direction == 'N':
            if self.y + self.height >= BOARD_LENGTH:
                raise IllegalMove, "Swap moves off the board."
            destPiece = self.board._board[self.x][self.y + self.height]
            if destPiece.x != self.x or destPiece.width != self.width:
                raise IllegalMove, "Swap pair does not share full side."
        elif direction == 'S':
            if self.y - 1 < 0:
                raise IllegalMove, "Swap moves off the board."
            destPiece = self.board._board[self.x][self.y - 1]
            if destPiece.x != self.x or destPiece.width != self.width:
                raise IllegalMove, "Swap pair does not share full side."
        elif direction == 'W':
            if self.x - 1 < 0:
                raise IllegalMove, "Swap moves off the board."
            destPiece = self.board._board[self.x - 1][self.y]
            if destPiece.y != self.y or destPiece.height != self.height:
                raise IllegalMove, "Swap pair does not share full side."
        elif direction == 'E':
            if self.x + self.width >= BOARD_LENGTH:
                raise IllegalMove, "Swap moves off the board."
            destPiece = self.board._board[self.x + self.width][self.y]
            if destPiece.y != self.y or destPiece.height != self.height:
                raise IllegalMove, "Swap pair does not share full side."
        else:
            raise IllegalMove, "Unknown swap direction: %s" % direction
        if destPiece.color == self.color:
            raise IllegalMove, "Both sides of swap pair (%d, %d) and (%d, %d) are the same color." % (self.x, self.y, destPiece.x, destPiece.y)
        destPiece.color, self.color = self.color, destPiece.color
        return destPiece

    def capture(self):
        if self.color == 'b':
            self.color = 'w'
        else:
            self.color = 'b'

    def neighbors(self):
        upperX, upperY = self.x + self.width, self.y + self.height
        neighbors = self.full_neighbors()
        if self.x > 0 and self.y > 0:
            p = self.board._board[self.x - 1][self.y - 1]
            if p not in neighbors:
                neighbors.append(p)
        if self.x > 0 and upperY < BOARD_LENGTH:
            p = self.board._board[self.x - 1][upperY]
            if p not in neighbors:
                neighbors.append(p)
        if upperX < BOARD_LENGTH and upperY < BOARD_LENGTH:
            p = self.board._board[upperX][upperY]
            if p not in neighbors:
                neighbors.append(p)
        if upperX < BOARD_LENGTH and self.y > 0:
            p = self.board._board[upperX][self.y - 1]
            if p not in neighbors:
                neighbors.append(p)
        return neighbors

    def full_neighbors(self):
        upperX, upperY = self.x + self.width, self.y + self.height
        neighbors = []
        if self.x > 0:
            y = self.y
            while y < upperY:
                p = self.board._board[self.x - 1][y]
                if p not in neighbors:
                    neighbors.append(p)
                y += p.height + p.y - y
        if upperY < BOARD_LENGTH:
            x = self.x
            while x < upperX:
                p = self.board._board[x][upperY]
                if p not in neighbors:
                    neighbors.append(p)
                x += p.width + p.x - x
        if upperX < BOARD_LENGTH:
            y = self.y
            while y < upperY:
                p = self.board._board[upperX][y]
                if p not in neighbors:
                    neighbors.append(p)
                y += p.height + p.y - y
        if self.y > 0:
            x = self.x
            while x < upperX:
                p = self.board._board[x][self.y - 1]
                if p not in neighbors:
                    neighbors.append(p)
                x += p.width + p.x - x
        return neighbors

    def __eq__(self, other):
        return (self.x == other.x
                and self.y == other.y
                and self.width == other.width
                and self.height == other.height
                and self.color == other.color)

    def __ne__(self, other):
        return not self == other

class IllegalMove(Exception):
    def value(self):
        return self.args[0]

def read(file, board=None, visualizer=None, filename="turn%02d.png"):
    if board is None:
        board = Board()
    if visualizer is not None:
        visualizer.draw(board, filename % 0)
    for line in file:
        line = line.replace(' ', '').replace('\t', '').replace('\n', '').replace('\r', '')
        if len(line) > 0:
            board.parse(line)
            if visualizer is not None:
                visualizer.draw(board, filename % board.turn())
    return board

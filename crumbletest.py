#!/usr/bin/python

import unittest, crumble
from crumble import Piece, IllegalMove

UNIT = crumble.UNIT_LENGTH

class ParsingTestCase(unittest.TestCase):
    def setUp(self):
        self.board = crumble.Board()

    def testInitialSetup(self):
        assert len(self.board.pieces()) == 36
        w, h = self.board.pieces()[0].width, self.board.pieces()[0].height
        for p in self.board.pieces():
            assert w == p.width and h == p.height
        assert self.board.pieceAt(0, 0).color == "w"
        assert self.board.pieceAt(UNIT, 0).color == "b"
        assert self.board.pieceAt(0, UNIT).color == "b"

    def testHorizontalSplit(self):
        self.board.parse("0,1H")
        assert self.board.pieceAt(0, UNIT) != self.board.pieceAt(0, UNIT * 3 / 2)
        assert self.board.pieceAt(0, UNIT) == Piece(None, 0, UNIT, UNIT, UNIT / 2, 'b')

    def testVerticalSplit(self):
        self.board.parse("0,1V")
        assert self.board.pieceAt(0, UNIT) != self.board.pieceAt(UNIT / 2, UNIT)
        assert self.board.pieceAt(0, UNIT) == Piece(None, 0, UNIT, UNIT / 2, UNIT, 'b')

    def testHorizontalSplitSwap(self):
        self.board.parse("0,1HN")
        assert self.board.pieceAt(0, UNIT) != self.board.pieceAt(0, UNIT * 3 / 2)
        assert self.board.pieceAt(0, UNIT * 3 / 2).height == UNIT / 2
        assert self.board.pieceAt(0, 0).color == 'w'
        assert self.board.pieceAt(0, UNIT).color == 'b'
        assert self.board.pieceAt(0, UNIT * 3 / 2).color == 'w'
        assert self.board.pieceAt(0, UNIT * 2).color == 'b'

    def testVerticalSplitSwap(self):
        self.board.parse("0,1VE")
        assert self.board.pieceAt(0, UNIT).width == UNIT / 2
        assert self.board.pieceAt(0, UNIT).color == 'b'
        assert self.board.pieceAt(UNIT / 2, UNIT).color == 'w'
        assert self.board.pieceAt(UNIT, UNIT).color == 'b'

    def testHorizontalSpecifiedPieceSwap(self):
        self.board.parse("1H")
        self.board.parse("0HN-E")
        assert self.board.pieceAt(0, 0) == Piece(None, 0, 0, UNIT, UNIT / 2, 'w')
        assert self.board.pieceAt(0, UNIT / 2) == Piece(None, 0, UNIT / 2, UNIT, UNIT / 2, 'b')
        assert self.board.pieceAt(UNIT, 0) == Piece(None, UNIT, 0, UNIT, UNIT / 2, 'b')
        assert self.board.pieceAt(UNIT, UNIT / 2) == Piece(None, UNIT, UNIT / 2, UNIT, UNIT / 2, 'w')

    def testVerticalSpecifiedPieceSwap(self):
        self.board.parse("0,1V")
        self.board.parse("0VW-N")
        assert self.board.pieceAt(0, 0) == Piece(None, 0, 0, UNIT / 2, UNIT, 'b')
        assert self.board.pieceAt(0, UNIT) == Piece(None, 0, UNIT, UNIT / 2, UNIT, 'w')
        assert self.board.pieceAt(UNIT / 2, 0) == Piece(None, UNIT / 2, 0, UNIT / 2, UNIT, 'w')
        assert self.board.pieceAt(UNIT / 2, UNIT) == Piece(None, UNIT / 2, UNIT, UNIT / 2, UNIT, 'b')

    def testBasicSwapChain(self):
        self.board.parse("0,1V")
        self.board.parse("2H")
        self.board.parse("1,2HS")
        self.board.parse("0VW-NEE")
        assert self.board.pieceAt(0, 0).color == 'b'
        assert self.board.pieceAt(0, UNIT).color == 'b'
        assert self.board.pieceAt(UNIT / 2, UNIT).color == 'b'
        assert self.board.pieceAt(UNIT, UNIT).color == 'w'

    def testHorizontalMultiSplit(self):
        self.board.parse("1HN")
        self.board.parse("2H")
        self.board.parse("0,1H3")
        assert self.board.pieceAt(0, UNIT) == Piece(None, 0, UNIT, UNIT, UNIT / 2, 'b')
        assert self.board.pieceAt(0, UNIT * 3 / 2) == Piece(None, 0, UNIT * 3 / 2, UNIT, UNIT / 2, 'b')
        assert self.board.pieceAt(UNIT, UNIT) == Piece(None, UNIT, UNIT, UNIT, UNIT / 2, 'b')
        assert self.board.pieceAt(UNIT, UNIT * 3 / 2) == Piece(None, UNIT, UNIT * 3 / 2, UNIT, UNIT / 2, 'b')
        assert self.board.pieceAt(UNIT * 2, UNIT) == Piece(None, UNIT * 2, UNIT, UNIT, UNIT / 2, 'b')
        assert self.board.pieceAt(UNIT * 2, UNIT * 3 / 2) == Piece(None, UNIT * 2, UNIT * 3 / 2, UNIT, UNIT / 2, 'b')

    def testInvalidHorizontalMultiSplit(self):
        try:
            self.board.parse("3,2H2-1S-S")
            assert False, "Horizontal splits containing opponent's pieces should throw an exception."
        except IllegalMove:
            pass    # Expected

    def testVerticalMultiSplit(self):
        self.board.parse("0,1VE")
        self.board.parse("2H")
        self.board.parse("1V3")
        assert self.board.pieceAt(UNIT, 0) == Piece(None, UNIT, 0, UNIT / 2, UNIT, 'b')
        assert self.board.pieceAt(UNIT * 3 / 2, 0) == Piece(None, UNIT * 3 / 2, 0, UNIT / 2, UNIT, 'b')
        assert self.board.pieceAt(UNIT, UNIT) == Piece(None, UNIT, UNIT, UNIT / 2, UNIT, 'b')
        assert self.board.pieceAt(UNIT * 3 / 2, UNIT) == Piece(None, UNIT * 3 / 2, UNIT, UNIT / 2, UNIT, 'b')
        assert self.board.pieceAt(UNIT, UNIT * 2) == Piece(None, UNIT, UNIT * 2, UNIT / 2, UNIT, 'b')
        assert self.board.pieceAt(UNIT * 3 / 2, UNIT * 2) == Piece(None, UNIT * 3 / 2, UNIT * 2, UNIT / 2, UNIT, 'b')

    def testInvalidVerticalMultiSplit(self):
        try:
            self.board.parse("2,1V3-3E-E")
            assert False, "Vertical splits containing opponent's pieces should throw an exception."
        except IllegalMove:
            pass    # Expected

    def testHorizontalMultiSplitWithBreak(self):
        self.board.parse("1HN")
        self.board.parse("0H2")
        assert self.board.pieceAt(0, 0) == Piece(None, 0, 0, UNIT, UNIT / 2, 'w')
        assert self.board.pieceAt(0, UNIT / 2) == Piece(None, 0, UNIT / 2, UNIT, UNIT / 2, 'w')
        assert self.board.pieceAt(UNIT, 0) == Piece(None, UNIT, 0, UNIT, UNIT / 2, 'b')
        assert self.board.pieceAt(UNIT, UNIT / 2) == Piece(None, UNIT, UNIT / 2, UNIT, UNIT / 2, 'w')
        assert self.board.pieceAt(UNIT * 2, 0) == Piece(None, UNIT * 2, 0, UNIT, UNIT / 2, 'w')
        assert self.board.pieceAt(UNIT * 2, UNIT / 2) == Piece(None, UNIT * 2, UNIT / 2, UNIT, UNIT / 2, 'w')
        assert self.board.pieceAt(UNIT * 3, 0) == Piece(None, UNIT * 3, 0, UNIT, UNIT, 'b')

    def testVerticalMultiSplitWithBreak(self):
        self.board.parse("0,1VE")
        self.board.parse("0V2")
        assert self.board.pieceAt(0, 0) == Piece(None, 0, 0, UNIT / 2, UNIT, 'w')
        assert self.board.pieceAt(UNIT / 2, 0) == Piece(None, UNIT / 2, 0, UNIT / 2, UNIT, 'w')
        assert self.board.pieceAt(0, UNIT) == Piece(None, 0, UNIT, UNIT / 2, UNIT, 'b')
        assert self.board.pieceAt(UNIT / 2, UNIT) == Piece(None, UNIT / 2, UNIT, UNIT / 2, UNIT, 'w')
        assert self.board.pieceAt(0, UNIT * 2) == Piece(None, 0, UNIT * 2, UNIT / 2, UNIT, 'w')
        assert self.board.pieceAt(UNIT / 2, UNIT * 2) == Piece(None, UNIT / 2, UNIT * 2, UNIT / 2, UNIT, 'w')
        assert self.board.pieceAt(0, UNIT * 3) == Piece(None, 0, UNIT * 3, UNIT, UNIT, 'b')
 
    def testHorizontalMultiSplitWithDirection(self):
        self.board.parse("1HN")
        self.board.parse("2H")
        try:
            self.board.parse("0,1H3E")
            assert False, "Specifying a direction on a multi-split should throw an exception"
        except IllegalMove:
            pass   # Expected

    def testVerticalMultiSplitWithDirection(self):
        self.board.parse("0,1VE")
        self.board.parse("2H")
        try:
            self.board.parse("1V3N")
            assert False, "Specifying a direction on a multi-split should throw an exception"
        except IllegalMove:
            pass   # Expected

    def testMultiSplitWithSwapChain(self):
        self.board.parse("1HN")
        self.board.parse("0H2-2N-NWW")
        assert self.board.pieceAt(0, UNIT) == Piece(None, 0, UNIT, UNIT, UNIT, 'w')
        assert self.board.pieceAt(UNIT, UNIT) == Piece(None, UNIT, UNIT, UNIT, UNIT, 'b')
        assert self.board.pieceAt(UNIT * 2, UNIT) == Piece(None, UNIT * 2, UNIT, UNIT, UNIT, 'b')
        assert self.board.pieceAt(UNIT * 2, UNIT / 2) == Piece(None, UNIT * 2, UNIT / 2, UNIT, UNIT / 2, 'b')

    def testMultiSplitWithBadPieceId(self):
        self.board.parse("1HN")
        try:
            self.board.parse("0H2-iN-NWW")
            assert False, "Specifying an invalid piece spec should throw an exception"
        except IllegalMove:
            pass   # Expected

    def testHorizontalOvershoot(self):
        try:
            self.board.parse("7VE")
            assert False, "Specifying an invalid piece spec should throw an exception"
        except IllegalMove:
            pass   # Expected

    def testHorizontalSpecifyBoardEdge(self):
        try:
            self.board.parse("6VE")
            assert False, "Specifying an invalid piece spec should throw an exception"
        except IllegalMove:
            pass   # Expected

    def testVerticalOvershoot(self):
        try:
            self.board.parse("0,7VE")
            assert False, "Specifying an invalid piece spec should throw an exception"
        except IllegalMove:
            pass   # Expected

    def testVerticalSpecifyBoardEdge(self):
        try:
            self.board.parse("0,6VE")
            assert False, "Specifying an invalid piece spec should throw an exception"
        except IllegalMove:
            pass   # Expected

    def testSimpleJoin(self):
        self.board.parse("1VW")
        self.board.parse("3H")
        self.board.parse("0J1,2")
        assert self.board.pieceAt(0, 0) == Piece(None, 0, 0, UNIT, UNIT * 2, 'b')
        assert self.board.pieceAt(0, 0) in self.board.pieces()
        assert len(self.board.pieces()) == 37

    def testIllegalJoinSpec(self):
        self.board.parse("1H")
        self.board.parse("0H")
        try:
            self.board.parse("1J1")
            assert False, "1J1 should not be a legal join spec"
        except IllegalMove:
            pass   # Expected

    def testIllegalJoinSpec2(self):
        self.board.parse("1H")
        self.board.parse("0H")
        try:
            self.board.parse("1J1,2,1")
            assert False, "1J1,2,1 should not be a legal join spec"
        except IllegalMove:
            pass   # Expected

    def testIllegalJoinSpec3(self):
        self.board.parse("1H")
        self.board.parse("0H")
        try:
            self.board.parse("1J1,2-N")
            assert False, "1J1,2-N uses the old notation and should no longer be accepted"
        except IllegalMove:
            pass   # Expected

    def testJoinWithSwap(self):
        self.board.parse("1VW")
        self.board.parse("3H")
        self.board.parse("0J1,2N")
        assert self.board.pieceAt(0, 0) == Piece(None, 0, 0, UNIT, UNIT * 2, 'w')
        assert self.board.pieceAt(0, UNIT * 2) == Piece(None, 0, UNIT * 2, UNIT, UNIT, 'b')
        assert self.board.pieceAt(0, 0) in self.board.pieces()
        assert len(self.board.pieces()) == 37

    def testJoinVertexSpec(self):
        self.board.parse("2,3VW")
        self.board.parse("2,4HN")
        self.board.parse("4,3VW")
        self.board.parse("2,2HS")
        self.board.parse("2,2J1,2S")
        self.board.parse("4,3H")
        self.board.parse("2,3J2,1S")
        self.board.parse("0H")
        self.board.parse("4,3,1H")
        self.board.parse("4,3VE")
        self.board.parse("1,3J3,4")
        assert self.board.pieceAt(UNIT, 2*UNIT) == Piece(None, UNIT, 2*UNIT, 3*UNIT, 3*UNIT, 'b')

    def testJoinWithNoPieceAtDestination(self):
        self.board.parse("1H")
        self.board.parse("1,2VE")
        self.board.parse("0,1HN")
        self.board.parse("2J1,2")
        self.board.parse("1J1,2")
        assert self.board.pieceAt(UNIT, 0) == Piece(None, UNIT, 0, UNIT, UNIT, 'b')

    def testJoinWithOpponentsPieceInSpec(self):
        self.board.parse("1H")
        self.board.parse("1,2VE")
        self.board.parse("0,1HN")
        self.board.parse("2J1,2")
        try:
            self.board.parse("1J1,3")
            assert False, "Should not be able to swallow an opponent's piece in a join."
        except IllegalMove:
            pass   # Expected

    def testSimpleNeighbors(self):
        n = self.board.pieceAt(0, 0).neighbors()
        assert len(n) == 3
        assert self.board.pieceAt(UNIT, 0) in n
        assert self.board.pieceAt(UNIT, UNIT) in n
        assert self.board.pieceAt(0, UNIT) in n
        n = self.board.pieceAt(0, crumble.BOARD_LENGTH - 1).neighbors()
        assert len(n) == 3
        assert self.board.pieceAt(0, crumble.BOARD_LENGTH - UNIT - 1) in n
        assert self.board.pieceAt(UNIT, crumble.BOARD_LENGTH - UNIT - 1) in n
        assert self.board.pieceAt(UNIT, crumble.BOARD_LENGTH - 1) in n
        n = self.board.pieceAt(crumble.BOARD_LENGTH - 1, crumble.BOARD_LENGTH - 1).neighbors()
        assert len(n) == 3
        assert self.board.pieceAt(crumble.BOARD_LENGTH - UNIT - 1, crumble.BOARD_LENGTH - 1) in n
        assert self.board.pieceAt(crumble.BOARD_LENGTH - UNIT - 1, crumble.BOARD_LENGTH - UNIT - 1) in n
        assert self.board.pieceAt(crumble.BOARD_LENGTH - 1, crumble.BOARD_LENGTH - UNIT - 1) in n
        n = self.board.pieceAt(crumble.BOARD_LENGTH - 1, 0).neighbors()
        assert len(n) == 3
        assert self.board.pieceAt(crumble.BOARD_LENGTH - UNIT - 1, 0) in n
        assert self.board.pieceAt(crumble.BOARD_LENGTH - UNIT - 1, UNIT) in n
        assert self.board.pieceAt(crumble.BOARD_LENGTH - 1, UNIT) in n

    def testComplexNeighbors(self):
        self.board.parse("1H")
        self.board.parse("0,2V")
        self.board.parse("1,3V")
        self.board.parse("2,3VWW")
        self.board.parse("0,3H")
        self.board.parse("0,2,1J2,1")
        n = self.board.pieceAt(0, UNIT).neighbors()
        assert len(n) == 5
        assert Piece(None, 0, 0, UNIT, UNIT, 'w') in n
        assert Piece(None, UNIT, UNIT / 2, UNIT, UNIT / 2, 'b') in n
        assert Piece(None, UNIT, UNIT, UNIT, UNIT, 'w') in n
        assert Piece(None, 0, UNIT * 2, UNIT / 2, UNIT, 'w') in n
        assert Piece(None, UNIT / 2, UNIT * 2, UNIT, UNIT, 'w') in n

    def testSimpleCapture(self):
        self.board.parse("1HN")
        self.board.parse("2H")
        self.board.parse("0,3VE")
        self.board.parse("0H")
        self.board.parse("4,3VW")
        self.board.parse("4H")
        assert self.board.pieceAt(UNIT * 2, UNIT * 2) == Piece(None, UNIT * 2, UNIT * 2, UNIT, UNIT, 'w')
        self.board.parse("3HN")
        assert self.board.pieceAt(UNIT * 2, UNIT * 2) == Piece(None, UNIT * 2, UNIT * 2, UNIT, UNIT, 'b')

    def testWinBlack(self):
        self.board.parse("2,1VW")
        self.board.parse("1,3VW")
        self.board.parse("2,3HN")
        self.board.parse("2VE")
        assert self.board.winner() is None
        self.board.parse("5,5HS")
        assert self.board.winner() == 'b'

    def testWinWhite(self):
        self.board.parse("3,4HN")
        self.board.parse("1,3HN")
        self.board.parse("4,1VW")
        assert self.board.winner() is None
        self.board.parse("3,3VE")
        assert self.board.winner() == 'w'

    def testOpponentWin(self):
        self.board.parse("2,1VW")
        self.board.parse("1,3VW")
        self.board.parse("2,3HN")
        assert self.board.winner() is None
        self.board.parse("4,4HS")
        assert self.board.winner() == 'b'

    def testNoMoveAfterWin(self):
        self.board.parse("2,1VW")
        self.board.parse("1,3VW")
        self.board.parse("2,3HN")
        self.board.parse("4,4HS")
        try:
            self.board.parse("0,1HN")
            assert False, "Attempting to move after the game is won should throw an exception."
        except IllegalMove:
            pass   # Expected

    def testNoContinueSwapAfterWin(self):
        self.board.parse("3,4HN")
        self.board.parse("1,3HN")
        self.board.parse("4,1VW")
        self.board.parse("2VW")
        self.board.parse("4,2HN")
        assert self.board.winner() is None
        try:
            self.board.parse("2,2HNEEW")
            assert False, "Attempting to move after the game is won should throw an exception."
        except IllegalMove:
            pass   # Expected

    def testJoinAlongRightBoardEdge(self):
        self.board.parse("5HN")
        self.board.parse("0HN")
        self.board.parse("5,2J1,2N")
        assert self.board.pieceAt(UNIT * 5, UNIT) == Piece(None, UNIT * 5, UNIT, UNIT, UNIT * 2, 'w')

    def testJoinAlongTopBoardEdge(self):
        self.board.parse("1,4HN")
        self.board.parse("0HN")
        self.board.parse("1,7J2,1E")
        assert self.board.pieceAt(UNIT, UNIT * 5) == Piece(None, UNIT, UNIT * 5, UNIT * 2, UNIT, 'w')

    def testSwapSouthOffBoardProducesError(self):
        try:
            self.board.parse("1HS")
            assert False, "Attempting to move off the board should throw an exception."
        except IllegalMove:
            pass   # Expected

    def testSwapNorthOffBoardProducesError(self):
        try:
            self.board.parse("2,5HN")
            assert False, "Attempting to move off the board should throw an exception."
        except IllegalMove:
            pass   # Expected

    def testSwapEastOffBoardProducesError(self):
        try:
            self.board.parse("5,2VE")
            assert False, "Attempting to move off the board should throw an exception."
        except IllegalMove:
            pass   # Expected

    def testSwapWestOffBoardProducesError(self):
        try:
            self.board.parse("0,3VW")
            assert False, "Attempting to move off the board should throw an exception."
        except IllegalMove:
            pass   # Expected

if __name__ == "__main__":
    unittest.main()

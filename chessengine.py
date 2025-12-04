class GameState:
    def __init__(self):
        self.board = [
            ['bR','bN','bB','bQ','bK','bB','bN','bR'],
            ['bP','bP','bP','bP','bP','bP','bP','bP'],
            ['--','--','--','--','--','--','--','--'],
            ['--','--','--','--','--','--','--','--'],
            ['--','--','--','--','--','--','--','--'],
            ['--','--','--','--','--','--','--','--'],
            ['wP','wP','wP','wP','wP','wP','wP','wP'],
            ['wR','wN','wB','wQ','wK','wB','wN','wR']
        ]

        self.whiteToMove = True
        self.moveLog = []

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) # log the move so we can undo it later
        self.whiteToMove = not self.whiteToMove # #swap players

    # undo functions 
    def undoMove(self):
        if len(self.moveLog) != 0: # make sure there is a move to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove


    # all moves considering checks
    def getValidMoves(self):
        return self.getAllPossibleMoves() # for now, we will not worry about checks


    def getAllPossibleMoves(self):
        moves = []
        for r in range(8):
            for c in range(8):
                pieceColor = self.board[r][c][0]
                pieceType = self.board[r][c][1]

            # Only select your own pieces
                if (pieceColor == 'w' and self.whiteToMove) or \
               (pieceColor == 'b' and not self.whiteToMove):

                    if pieceType == 'P':
                        self.getPawnMoves(r, c, moves)
                    elif pieceType == 'R':
                        self.getRookMoves(r, c, moves)
                    elif pieceType == 'N':
                        self.getKnightMoves(r, c, moves)
                    elif pieceType == 'B':
                        self.getBishopMoves(r, c, moves)
                    elif pieceType == 'Q':
                        self.getQueenMoves(r, c, moves)
                    elif pieceType == 'K':
                        self.getKingMoves(r, c, moves)

        return moves
    
    def getPawnMoves(self, r, c, moves):   
        pass
    def getRookMoves(self, r, c, moves):
        pass
    def getKnightMoves(self, r, c, moves):
        pass
    def getBishopMoves(self, r, c, moves):  
        pass
    def getQueenMoves(self, r, c, moves):
        pass
    def getKingMoves(self, r, c, moves):
        pass



    
class Move:
    # maps keys to ranks/files
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}

    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]

        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

# override equals method
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False  

    def getChessNotation(self):
        """Optional: convert move to standard notation"""
        return self.getRankFile(self.startRow, self.startCol) + \
               self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]


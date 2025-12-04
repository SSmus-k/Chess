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
        piece = self.board[r][c]
        if piece[0] == 'w':  # white pawn
            if r-1 >= 0 and self.board[r-1][c] == "--":
                moves.append(Move((r,c),(r-1,c),self.board))
                if r == 6 and self.board[r-2][c] == "--":
                    moves.append(Move((r,c),(r-2,c),self.board))
            # captures
            if r-1 >= 0 and c-1 >= 0 and self.board[r-1][c-1][0] == 'b':
                moves.append(Move((r,c),(r-1,c-1),self.board))
            if r-1 >= 0 and c+1 < 8 and self.board[r-1][c+1][0] == 'b':
                moves.append(Move((r,c),(r-1,c+1),self.board))
        else:  # black pawn
            if r+1 < 8 and self.board[r+1][c] == "--":
                moves.append(Move((r,c),(r+1,c),self.board))
                if r == 1 and self.board[r+2][c] == "--":
                    moves.append(Move((r,c),(r+2,c),self.board))
            # captures
            if r+1 < 8 and c-1 >= 0 and self.board[r+1][c-1][0] == 'w':
                moves.append(Move((r,c),(r+1,c-1),self.board))
            if r+1 < 8 and c+1 < 8 and self.board[r+1][c+1][0] == 'w':
                moves.append(Move((r,c),(r+1,c+1),self.board))

    def getRookMoves(self, r, c, moves):
        directions = [(-1,0),(1,0),(0,-1),(0,1)]
        enemy_color = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1,8):
                end_row = r + d[0]*i
                end_col = c + d[1]*i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--":
                        moves.append(Move((r,c),(end_row,end_col),self.board))
                    elif end_piece[0] == enemy_color:
                        moves.append(Move((r,c),(end_row,end_col),self.board))
                        break
                    else:
                        break
                else:
                    break

    def getKnightMoves(self, r, c, moves):
        knight_moves = [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]
        ally_color = 'w' if self.whiteToMove else 'b'
        for m in knight_moves:
            end_row, end_col = r+m[0], c+m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece == "--" or end_piece[0] != ally_color:
                    moves.append(Move((r,c),(end_row,end_col),self.board))

    def getBishopMoves(self, r, c, moves):
        directions = [(-1,-1),(-1,1),(1,-1),(1,1)]
        enemy_color = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1,8):
                end_row = r + d[0]*i
                end_col = c + d[1]*i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--":
                        moves.append(Move((r,c),(end_row,end_col),self.board))
                    elif end_piece[0] == enemy_color:
                        moves.append(Move((r,c),(end_row,end_col),self.board))
                        break
                    else:
                        break
                else:
                    break

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        king_moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
        ally_color = 'w' if self.whiteToMove else 'b'
        for m in king_moves:
            end_row, end_col = r+m[0], c+m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece == "--" or end_piece[0] != ally_color:
                    moves.append(Move((r,c),(end_row,end_col),self.board))


    
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


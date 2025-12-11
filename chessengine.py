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
        self.enpassantPossible = ()  # square where en passant is possible
        self.castleRights = {'wK': True, 'wQ': True, 'bK': True, 'bQ': True}

    def makeMove(self, move):
        # Move piece
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)

        # Pawn promotion
        if move.pieceMoved[1] == 'P':
            if (move.pieceMoved[0] == 'w' and move.endRow == 0) or \
               (move.pieceMoved[0] == 'b' and move.endRow == 7):
                self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'
                move.isPawnPromotion = True

        # En passant
        if hasattr(move, 'isEnpassantMove') and move.isEnpassantMove:
            capture_row = move.startRow
            if move.pieceMoved[0] == 'w':
                capture_row = move.endRow + 1
            else:
                capture_row = move.endRow - 1
            self.board[capture_row][move.endCol] = "--"

        # Set en passant possibility
        self.enpassantPossible = ()
        if move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.startRow + move.endRow)//2, move.startCol)

        # Castling
        if hasattr(move, 'isCastleMove') and move.isCastleMove:
            if move.endCol - move.startCol == 2:  # kingside
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1]
                self.board[move.endRow][move.endCol+1] = "--"
            else:  # queenside
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2]
                self.board[move.endRow][move.endCol-2] = "--"

        # Update castling rights
        if move.pieceMoved[1] == 'K':
            if move.pieceMoved[0] == 'w':
                self.castleRights['wK'] = False
                self.castleRights['wQ'] = False
            else:
                self.castleRights['bK'] = False
                self.castleRights['bQ'] = False
        if move.pieceMoved[1] == 'R':
            if move.startRow == 7 and move.startCol == 0:
                self.castleRights['wQ'] = False
            elif move.startRow == 7 and move.startCol == 7:
                self.castleRights['wK'] = False
            elif move.startRow == 0 and move.startCol == 0:
                self.castleRights['bQ'] = False
            elif move.startRow == 0 and move.startCol == 7:
                self.castleRights['bK'] = False

        self.whiteToMove = not self.whiteToMove

    def undoMove(self):
        if not self.moveLog:
            return
        move = self.moveLog.pop()
        self.board[move.startRow][move.startCol] = move.pieceMoved
        self.board[move.endRow][move.endCol] = move.pieceCaptured

        # Undo en passant
        if hasattr(move, 'isEnpassantMove') and move.isEnpassantMove:
            capture_row = move.startRow
            if move.pieceMoved[0] == 'w':
                capture_row = move.endRow + 1
            else:
                capture_row = move.endRow - 1
            self.board[capture_row][move.endCol] = move.pieceCaptured

        # Undo castling
        if hasattr(move, 'isCastleMove') and move.isCastleMove:
            if move.endCol - move.startCol == 2:  # kingside
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]
                self.board[move.endRow][move.endCol-1] = "--"
            else:  # queenside
                self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1]
                self.board[move.endRow][move.endCol+1] = "--"

        self.whiteToMove = not self.whiteToMove

    def getValidMoves(self):
        # TODO: add check detection
        return self.getAllPossibleMoves()

    def getAllPossibleMoves(self):
        moves = []
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece == "--":
                    continue
                pieceColor, pieceType = piece[0], piece[1]
                if (pieceColor == 'w' and self.whiteToMove) or (pieceColor == 'b' and not self.whiteToMove):
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

    # ----------------- Piece Moves -----------------
    def getPawnMoves(self, r, c, moves):
        piece = self.board[r][c]
        if piece[0] == 'w':
            if r-1 >=0 and self.board[r-1][c] == "--":
                moves.append(Move((r,c),(r-1,c),self.board))
                if r == 6 and self.board[r-2][c] == "--":
                    moves.append(Move((r,c),(r-2,c),self.board))
            # captures
            if r-1>=0 and c-1>=0 and self.board[r-1][c-1][0]=='b':
                moves.append(Move((r,c),(r-1,c-1),self.board))
            if r-1>=0 and c+1<8 and self.board[r-1][c+1][0]=='b':
                moves.append(Move((r,c),(r-1,c+1),self.board))
            # en passant
            if self.enpassantPossible == (r-1,c-1):
                move = Move((r,c),(r-1,c-1),self.board)
                move.isEnpassantMove = True
                moves.append(move)
            if self.enpassantPossible == (r-1,c+1):
                move = Move((r,c),(r-1,c+1),self.board)
                move.isEnpassantMove = True
                moves.append(move)
        else:
            if r+1 <8 and self.board[r+1][c] == "--":
                moves.append(Move((r,c),(r+1,c),self.board))
                if r==1 and self.board[r+2][c] == "--":
                    moves.append(Move((r,c),(r+2,c),self.board))
            # captures
            if r+1<8 and c-1>=0 and self.board[r+1][c-1][0]=='w':
                moves.append(Move((r,c),(r+1,c-1),self.board))
            if r+1<8 and c+1<8 and self.board[r+1][c+1][0]=='w':
                moves.append(Move((r,c),(r+1,c+1),self.board))
            # en passant
            if self.enpassantPossible == (r+1,c-1):
                move = Move((r,c),(r+1,c-1),self.board)
                move.isEnpassantMove = True
                moves.append(move)
            if self.enpassantPossible == (r+1,c+1):
                move = Move((r,c),(r+1,c+1),self.board)
                move.isEnpassantMove = True
                moves.append(move)

    def getRookMoves(self, r, c, moves):
        directions = [(-1,0),(1,0),(0,-1),(0,1)]
        enemy = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1,8):
                end_row = r + d[0]*i
                end_col = c + d[1]*i
                if 0<=end_row<8 and 0<=end_col<8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--":
                        moves.append(Move((r,c),(end_row,end_col),self.board))
                    elif end_piece[0] == enemy:
                        moves.append(Move((r,c),(end_row,end_col),self.board))
                        break
                    else:
                        break
                else:
                    break

    def getKnightMoves(self, r, c, moves):
        knight_moves = [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]
        ally = 'w' if self.whiteToMove else 'b'
        for m in knight_moves:
            end_row, end_col = r+m[0], c+m[1]
            if 0<=end_row<8 and 0<=end_col<8:
                end_piece = self.board[end_row][end_col]
                if end_piece=="--" or end_piece[0]!=ally:
                    moves.append(Move((r,c),(end_row,end_col),self.board))

    def getBishopMoves(self, r, c, moves):
        directions = [(-1,-1),(-1,1),(1,-1),(1,1)]
        enemy = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1,8):
                end_row = r + d[0]*i
                end_col = c + d[1]*i
                if 0<=end_row<8 and 0<=end_col<8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece=="--":
                        moves.append(Move((r,c),(end_row,end_col),self.board))
                    elif end_piece[0]==enemy:
                        moves.append(Move((r,c),(end_row,end_col),self.board))
                        break
                    else:
                        break
                else:
                    break

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r,c,moves)
        self.getBishopMoves(r,c,moves)

    def getKingMoves(self, r, c, moves):
        king_moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
        ally = 'w' if self.whiteToMove else 'b'
        for m in king_moves:
            end_row, end_col = r+m[0], c+m[1]
            if 0<=end_row<8 and 0<=end_col<8:
                end_piece = self.board[end_row][end_col]
                if end_piece=="--" or end_piece[0]!=ally:
                    moves.append(Move((r,c),(end_row,end_col),self.board))

# -------------------- Move class --------------------
class Move:
    ranksToRows = {"1":7,"2":6,"3":5,"4":4,"5":3,"6":2,"7":1,"8":0}
    rowsToRanks = {v:k for k,v in ranksToRows.items()}
    filesToCols = {"a":0,"b":1,"c":2,"d":3,"e":4,"f":5,"g":6,"h":7}
    colsToFiles = {v:k for k,v in filesToCols.items()}

    def __init__(self, startSq, endSq, board):
        self.startRow, self.startCol = startSq
        self.endRow, self.endCol = endSq
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        self.moveID = self.startRow*1000 + self.startCol*100 + self.endRow*10 + self.endCol

        # Special move flags
        self.isPawnPromotion = False
        self.isCastleMove = False
        self.isEnpassantMove = False

    def __eq__(self, other):
        return isinstance(other, Move) and self.moveID == other.moveID

    def getChessNotation(self):
        return self.getRankFile(self.startRow,self.startCol) + self.getRankFile(self.endRow,self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]

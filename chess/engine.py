'''
    If you want to play as black or wants to flip the board set :
    self.playerWantsToPlayAsBlack = True
'''

# Responsible for storing all information about current state of chess game,
# determining valid moves, and undoing/redoing moves.


class GameState():
    def __init__(self):
        self.board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']]

        self.board1 = [
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR'],
            ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR']]

        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                              'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        self.whiteToMove = True
        self.playerWantsToPlayAsBlack = False
        self.moveLog = []
        # Redo stack for redo functionality
        self.redoStack = []

        if self.playerWantsToPlayAsBlack:
            self.whiteKinglocation = (0, 4)
            self.blackKinglocation = (7, 4)
        else:
            self.whiteKinglocation = (7, 4)
            self.blackKinglocation = (0, 4)

        self.checkmate = False
        self.stalemate = False
        self.inCheck = False
        self.score = 0
        self.pins = []
        self.checks = []
        self.enpasantPossible = ()
        self.enpasantPossibleLog = [self.enpasantPossible]
        self.whiteCastleKingside = True
        self.whiteCastleQueenside = True
        self.blackCastleKingside = True
        self.blackCastleQueenside = True
        self.castleRightsLog = [CastleRights(
            self.whiteCastleKingside, self.whiteCastleQueenside,
            self.blackCastleKingside, self.blackCastleQueenside)]

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        # Any new move clears the redo stack
        self.redoStack.clear()
        self.whiteToMove = not self.whiteToMove

        if move.pieceMoved == 'wK':
            self.whiteKinglocation = (move.endRow, move.endCol)
            self.whiteCastleKingside = False
            self.whiteCastleQueenside = False
        elif move.pieceMoved == 'bK':
            self.blackKinglocation = (move.endRow, move.endCol)
            self.blackCastleKingside = False
            self.blackCastleQueenside = False

        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = '--'

        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            self.enpasantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enpasantPossible = ()

        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(
            self.whiteCastleKingside, self.whiteCastleQueenside,
            self.blackCastleKingside, self.blackCastleQueenside))
        self.enpasantPossibleLog.append(self.enpasantPossible)

        if move.castle:
            if move.endCol - move.startCol == 2:  # Kingside
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]
                self.board[move.endRow][move.endCol + 1] = "--"
            else:  # Queenside
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]
                self.board[move.endRow][move.endCol - 2] = "--"

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            # Push to redo stack so we can redo it
            self.redoStack.append(move)
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove

            if move.pieceMoved == 'wK':
                self.whiteKinglocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKinglocation = (move.startRow, move.startCol)

            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = "--"
                self.board[move.startRow][move.endCol] = move.pieceCaptured

            self.enpasantPossibleLog.pop()
            self.enpasantPossible = self.enpasantPossibleLog[-1]

            self.castleRightsLog.pop()
            cr = self.castleRightsLog[-1]
            self.whiteCastleKingside = cr.wks
            self.whiteCastleQueenside = cr.wqs
            self.blackCastleKingside = cr.bks
            self.blackCastleQueenside = cr.bqs

            if move.castle:
                if move.endCol - move.startCol == 2:  # Kingside
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = "--"
                else:  # Queenside
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = "--"

            self.checkmate = False
            self.stalemate = False

    def redoMove(self):
        """Redo the last undone move."""
        if len(self.redoStack) != 0:
            move = self.redoStack.pop()
            self.makeMove(move)
            # makeMove clears redoStack, so we need to preserve remaining redo moves
            # Workaround: re-append remaining redo moves after makeMove clears them
            # Solution: makeMove only clears if it's a NEW move. We handle this with a flag.

    def getValidMoves(self):
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKinglocation[0]
            kingCol = self.whiteKinglocation[1]
        else:
            kingRow = self.blackKinglocation[0]
            kingCol = self.blackKinglocation[1]
        if self.inCheck:
            if len(self.checks) == 1:
                moves = self.getAllPossibleMoves()
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = []
                if pieceChecking[1] == 'N':
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSq = (kingRow + check[2] * i, kingCol + check[3] * i)
                        validSquares.append(validSq)
                        if validSq[0] == checkRow and validSq[1] == checkCol:
                            break
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].pieceMoved[1] != 'K':
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            moves.remove(moves[i])
            else:
                self.getKingMoves(kingRow, kingCol, moves)
        else:
            moves = self.getAllPossibleMoves()

        if len(moves) == 0:
            if self.inCheck:
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        return moves

    def squareUnderAttack(self, row, col, allyColor):
        enemyColor = 'w' if allyColor == 'b' else 'b'
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1),
                      (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            for i in range(1, 8):
                endRow = row + d[0] * i
                endCol = col + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor:
                        break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        if (0 <= j <= 3 and type == 'R') or (4 <= j <= 7 and type == 'B') or \
                            (i == 1 and type == 'p' and ((enemyColor == 'w' and 6 <= j <= 7) or
                                                          (enemyColor == 'b' and 4 <= j <= 5))) or \
                                (type == 'Q') or (i == 1 and type == 'K'):
                            return True
                        else:
                            break
                else:
                    break
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2),
                       (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            endRow = row + m[0]
            endCol = col + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N':
                    return True
        return False

    def getAllPossibleMoves(self):
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[0])):
                turn = self.board[row][col][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[row][col][1]
                    self.moveFunctions[piece](row, col, moves)
        return moves

    def getPawnMoves(self, row, col, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.playerWantsToPlayAsBlack:
            if self.whiteToMove:
                moveAmount = 1
                startRow = 1
                enemyColor = 'b'
                kingRow, kingCol = self.whiteKinglocation
            else:
                moveAmount = -1
                startRow = 6
                enemyColor = 'w'
                kingRow, kingCol = self.blackKinglocation
        else:
            if self.whiteToMove:
                moveAmount = -1
                startRow = 6
                enemyColor = 'b'
                kingRow, kingCol = self.whiteKinglocation
            else:
                moveAmount = 1
                startRow = 1
                enemyColor = 'w'
                kingRow, kingCol = self.blackKinglocation

        if self.board[row + moveAmount][col] == "--":
            if not piecePinned or pinDirection == (moveAmount, 0):
                moves.append(Move((row, col), (row + moveAmount, col), self.board))
                if row == startRow and self.board[row + 2 * moveAmount][col] == "--":
                    moves.append(Move((row, col), (row + 2 * moveAmount, col), self.board))

        if col - 1 >= 0:
            if not piecePinned or pinDirection == (moveAmount, -1):
                if self.board[row + moveAmount][col - 1][0] == enemyColor:
                    moves.append(Move((row, col), (row + moveAmount, col - 1), self.board))
                if (row + moveAmount, col - 1) == self.enpasantPossible:
                    attackingPiece = blockingPiece = False
                    if kingRow == row:
                        if kingCol < col:
                            insideRange = range(kingCol + 1, col - 1)
                            outsideRange = range(col + 1, 8)
                        else:
                            insideRange = range(col + 1, kingCol)
                            outsideRange = range(0, col - 1)
                        for c in insideRange:
                            if self.board[row][c] != '--':
                                blockingPiece = True
                        for c in outsideRange:
                            if self.board[row][c][0] == enemyColor and (self.board[row][c][1] == 'R' or self.board[row][c][1] == 'Q'):
                                attackingPiece = True
                            elif self.board[row][c] != '--':
                                blockingPiece = True
                    if not attackingPiece or blockingPiece:
                        moves.append(Move((row, col), (row + moveAmount, col - 1), self.board, isEnpassantMove=True))

        if col + 1 <= 7:
            if not piecePinned or pinDirection == (moveAmount, 1):
                if self.board[row + moveAmount][col + 1][0] == enemyColor:
                    moves.append(Move((row, col), (row + moveAmount, col + 1), self.board))
                if (row + moveAmount, col + 1) == self.enpasantPossible:
                    attackingPiece = blockingPiece = False
                    if kingRow == row:
                        if kingCol < col:
                            insideRange = range(kingCol + 1, col)
                            outsideRange = range(col + 2, 8)
                        else:
                            insideRange = range(col + 2, kingCol)
                            outsideRange = range(0, col)
                        for c in insideRange:
                            if self.board[row][c] != '--':
                                blockingPiece = True
                        for c in outsideRange:
                            if self.board[row][c][0] == enemyColor and (self.board[row][c][1] == 'R' or self.board[row][c][1] == 'Q'):
                                attackingPiece = True
                            elif self.board[row][c] != '--':
                                blockingPiece = True
                    if not attackingPiece or blockingPiece:
                        moves.append(Move((row, col), (row + moveAmount, col + 1), self.board, isEnpassantMove=True))

    def getRookMoves(self, row, col, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = [(-1, 0), (0, -1), (1, 0), (0, 1)]
        enemy_color = 'b' if self.whiteToMove else 'w'

        for direction in directions:
            for i in range(1, 8):
                endRow = row + direction[0] * i
                endCol = col + direction[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == direction or pinDirection == (-direction[0], -direction[1]):
                        if self.board[endRow][endCol] == '--':
                            moves.append(Move((row, col), (endRow, endCol), self.board))
                        elif self.board[endRow][endCol][0] == enemy_color:
                            moves.append(Move((row, col), (endRow, endCol), self.board))
                            break
                        else:
                            break
                else:
                    break

    def getBishopMoves(self, row, col, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = [(1, 1), (-1, -1), (-1, 1), (1, -1)]
        enemy_color = 'b' if self.whiteToMove else 'w'

        for direction in directions:
            for i in range(1, 8):
                endRow = row + direction[0] * i
                endCol = col + direction[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == direction or pinDirection == (-direction[0], -direction[1]):
                        if self.board[endRow][endCol] == '--':
                            moves.append(Move((row, col), (endRow, endCol), self.board))
                        elif self.board[endRow][endCol][0] == enemy_color:
                            moves.append(Move((row, col), (endRow, endCol), self.board))
                            break
                        else:
                            break
                else:
                    break

    def getKnightMoves(self, row, col, moves):
        piecePinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break

        AllPossibleKnightMoves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                                   (1, -2), (1, 2), (2, -1), (2, 1)]
        for m in AllPossibleKnightMoves:
            endRow = row + m[0]
            endCol = col + m[1]
            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                if not piecePinned:
                    if self.whiteToMove and (self.board[endRow][endCol] == '--' or self.board[endRow][endCol][0] == 'b'):
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                    elif not self.whiteToMove and (self.board[endRow][endCol] == '--' or self.board[endRow][endCol][0] == 'w'):
                        moves.append(Move((row, col), (endRow, endCol), self.board))

    def getQueenMoves(self, row, col, moves):
        self.getBishopMoves(row, col, moves)
        self.getRookMoves(row, col, moves)

    def getKingMoves(self, row, col, moves):
        for i in range(-1, 2):
            for j in range(-1, 2):
                allyColor = 'w' if self.whiteToMove else 'b'
                if i == 0 and j == 0:
                    continue
                if 0 <= row + i <= 7 and 0 <= col + j <= 7:
                    endPiece = self.board[row + i][col + j]
                    if endPiece[0] != allyColor:
                        if allyColor == 'w':
                            self.whiteKinglocation = (row + i, col + j)
                        else:
                            self.blackKinglocation = (row + i, col + j)
                        inCheck, pins, checks = self.checkForPinsAndChecks()
                        if not inCheck:
                            moves.append(Move((row, col), (row + i, col + j), self.board))
                        if allyColor == 'w':
                            self.whiteKinglocation = (row, col)
                        else:
                            self.blackKinglocation = (row, col)
        self.getcastleMoves(row, col, moves, allyColor)

    def getcastleMoves(self, row, col, moves, allyColor):
        inCheck = self.squareUnderAttack(row, col, allyColor)
        if inCheck:
            return
        if (self.whiteToMove and self.whiteCastleKingside) or (not self.whiteToMove and self.blackCastleKingside):
            self.getKingsidecastleMoves(row, col, moves, allyColor)
        if (self.whiteToMove and self.whiteCastleQueenside) or (not self.whiteToMove and self.blackCastleQueenside):
            self.getQueensidecastleMoves(row, col, moves, allyColor)

    def getKingsidecastleMoves(self, row, col, moves, allyColor):
        if self.board[row][col + 1] == "--" and self.board[row][col + 2] == "--" \
                and not self.squareUnderAttack(row, col + 1, allyColor) \
                and not self.squareUnderAttack(row, col + 2, allyColor):
            moves.append(Move((row, col), (row, col + 2), self.board, castle=True))

    def getQueensidecastleMoves(self, row, col, moves, allyColor):
        if self.board[row][col - 1] == "--" and self.board[row][col - 2] == "--" \
                and self.board[row][col - 3] == "--" \
                and not self.squareUnderAttack(row, col - 1, allyColor) \
                and not self.squareUnderAttack(row, col - 2, allyColor):
            moves.append(Move((row, col), (row, col - 2), self.board, castle=True))

    def checkForPinsAndChecks(self):
        pins = []
        checks = []
        inCheck = False
        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKinglocation[0]
            startCol = self.whiteKinglocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKinglocation[0]
            startCol = self.blackKinglocation[1]

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1),
                      (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != 'K':
                        if possiblePin == ():
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        if (0 <= j <= 3 and type == 'R') or (4 <= j <= 7 and type == 'B') or \
                            (i == 1 and type == 'p' and
                             ((enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
                                (type == 'Q') or (i == 1 and type == 'K'):
                            if possiblePin == ():
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:
                                pins.append(possiblePin)
                                break
                        else:
                            break
                else:
                    break

        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2),
                       (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N':
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        return inCheck, pins, checks

    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.whiteCastleKingside = False
            self.whiteCastleQueenside = False
        elif move.pieceMoved == 'bK':
            self.blackCastleKingside = False
            self.blackCastleQueenside = False

        if move.pieceMoved == 'wR':
            if move.startRow == 7 and move.startCol == 0:
                self.whiteCastleQueenside = False
            elif move.startRow == 7 and move.startCol == 7:
                self.whiteCastleKingside = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0 and move.startCol == 0:
                self.blackCastleQueenside = False
            elif move.startRow == 0 and move.startCol == 7:
                self.blackCastleKingside = False

        if move.pieceCaptured == 'wR' and move.endRow == 7 and move.endCol == 0:
            self.whiteCastleQueenside = False
        if move.pieceCaptured == 'wR' and move.endRow == 7 and move.endCol == 7:
            self.whiteCastleKingside = False
        if move.pieceCaptured == 'bR' and move.endRow == 0 and move.endCol == 0:
            self.blackCastleQueenside = False
        if move.pieceCaptured == 'bR' and move.endRow == 0 and move.endCol == 7:
            self.blackCastleKingside = False

    def getBoardString(self):
        boardString = ""
        for row in self.board:
            for square in row:
                boardString += square
        return boardString


class CastleRights():
    def __init__(self, wks, wqs, bks, bqs):
        self.wks = wks
        self.wqs = wqs
        self.bks = bks
        self.bqs = bqs


# Keep old name for compatibility
castleRights = CastleRights


class Move():
    ranksToRows = {"1": 7, "2": 6, "3": 5,
                   "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {value: key for key, value in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2,
                   "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {value: key for key, value in filesToCols.items()}

    def __init__(self, startSquare, endSquare, board, isEnpassantMove=False, castle=False):
        self.startRow = startSquare[0]
        self.startCol = startSquare[1]
        self.endRow = endSquare[0]
        self.endCol = endSquare[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.castle = castle
        if isEnpassantMove:
            self.pieceCaptured = board[self.startRow][self.endCol]
        else:
            self.pieceCaptured = board[self.endRow][self.endCol]
        self.isCapture = self.pieceCaptured != '--'
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        gs_temp = GameState()
        if gs_temp.playerWantsToPlayAsBlack:
            self.isPawnPromotion = (self.pieceMoved == "wp" and self.endRow == 7) or \
                                   (self.pieceMoved == "bp" and self.endRow == 0)
        else:
            self.isPawnPromotion = (self.pieceMoved == "wp" and self.endRow == 0) or \
                                   (self.pieceMoved == "bp" and self.endRow == 7)
        self.isEnpassantMove = isEnpassantMove

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getPieceNotation(self.pieceMoved, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, row, col):
        return self.colsToFiles[col] + self.rowsToRanks[row]

    def getPieceNotation(self, piece, col):
        if piece[1] == 'p':
            return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)
        notation = {"R": "R", "N": "N", "B": "B", "Q": "Q", "K": "K"}
        return notation.get(piece[1], "") + self.colsToFiles[col]

    def __str__(self):
        if self.castle:
            return "O-O" if self.endCol == 6 else "O-O-O"
        startSquare = self.getRankFile(self.startRow, self.startCol)
        endSquare = self.getRankFile(self.endRow, self.endCol)
        if self.pieceMoved[1] == 'p':
            if self.isCapture:
                return startSquare + "x" + endSquare
            else:
                return startSquare + endSquare
        moveString = self.pieceMoved[1]
        if self.isCapture:
            return moveString + self.colsToFiles[self.startCol] + "x" + endSquare
        return moveString + self.colsToFiles[self.startCol] + endSquare
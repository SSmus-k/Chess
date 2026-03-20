'''
    Chess AI with:
    - 3 difficulty levels: EASY (depth 1, random), MEDIUM (depth 3), HARD (depth 4)
    - Opening book for first ~10 moves
    - Alpha-beta pruning NegaMax
    - Piece-position scoring tables
    - Basic move ordering (captures first) for faster pruning
'''

import random

pieceScore = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "p": 1}

knightScores = [[1, 1, 1, 1, 1, 1, 1, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 1, 1, 1, 1, 1, 1, 1]]

bishopScores = [[4, 3, 2, 1, 1, 2, 3, 4],
                [3, 4, 3, 2, 2, 3, 4, 3],
                [2, 3, 4, 3, 3, 4, 3, 2],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [2, 3, 4, 3, 3, 4, 3, 2],
                [3, 4, 3, 2, 2, 3, 4, 3],
                [4, 3, 2, 1, 1, 2, 3, 4]]

queenScores = [[1, 1, 1, 3, 1, 1, 1, 1],
               [1, 2, 3, 3, 3, 1, 1, 1],
               [1, 4, 3, 3, 3, 4, 2, 1],
               [1, 2, 3, 3, 3, 2, 2, 1],
               [1, 2, 3, 3, 3, 2, 2, 1],
               [1, 4, 3, 3, 3, 4, 2, 1],
               [1, 1, 2, 3, 3, 1, 1, 1],
               [1, 1, 1, 3, 1, 1, 1, 1]]

rookScores = [[4, 3, 4, 4, 4, 4, 3, 4],
              [4, 4, 4, 4, 4, 4, 4, 4],
              [1, 1, 2, 3, 3, 2, 1, 1],
              [1, 2, 3, 4, 4, 3, 2, 1],
              [1, 2, 3, 4, 4, 3, 2, 1],
              [1, 1, 2, 2, 2, 2, 1, 1],
              [4, 4, 4, 4, 4, 4, 4, 4],
              [4, 3, 2, 1, 1, 2, 3, 4]]

whitePawnScores = [[8, 8, 8, 8, 8, 8, 8, 8],
                   [8, 8, 8, 8, 8, 8, 8, 8],
                   [5, 6, 6, 7, 7, 6, 6, 5],
                   [2, 3, 3, 5, 5, 3, 3, 2],
                   [1, 2, 3, 4, 4, 3, 2, 1],
                   [1, 1, 2, 3, 3, 2, 1, 1],
                   [1, 1, 1, 0, 0, 1, 1, 1],
                   [0, 0, 0, 0, 0, 0, 0, 0]]

blackPawnScores = [[0, 0, 0, 0, 0, 0, 0, 0],
                   [1, 1, 1, 0, 0, 1, 1, 1],
                   [1, 1, 2, 3, 3, 2, 1, 1],
                   [1, 2, 3, 4, 4, 3, 2, 1],
                   [2, 3, 3, 5, 5, 3, 3, 2],
                   [5, 6, 6, 7, 7, 6, 6, 5],
                   [8, 8, 8, 8, 8, 8, 8, 8],
                   [8, 8, 8, 8, 8, 8, 8, 8]]

piecePositionScores = {"N": knightScores, "B": bishopScores, "Q": queenScores,
                       "R": rookScores, "wp": whitePawnScores, "bp": blackPawnScores}

CHECKMATE = 1000
STALEMATE = 0

# ─────────────────────────────────────────────
# OPENING BOOK  (white UCI moves -> list of replies)
# Stored as (startRow, startCol, endRow, endCol) tuples
# ─────────────────────────────────────────────
OPENING_BOOK = {
    # After e4
    ((6, 4, 4, 4),): [
        (1, 4, 3, 4),   # e5
        (1, 2, 3, 2),   # c5 (Sicilian)
        (1, 4, 2, 4),   # e6 (French)
    ],
    # After d4
    ((6, 3, 4, 3),): [
        (1, 3, 3, 3),   # d5
        (1, 6, 2, 5),   # Nf6
    ],
    # e4 e5 -> Nf3
    ((6, 4, 4, 4), (1, 4, 3, 4)): [
        (7, 6, 5, 5),   # Nf3
    ],
    # e4 c5 -> Nf3
    ((6, 4, 4, 4), (1, 2, 3, 2)): [
        (7, 6, 5, 5),   # Nf3
    ],
}


def _moves_to_key(moveLog):
    """Convert moveLog to a tuple key for the opening book."""
    return tuple((m.startRow, m.startCol, m.endRow, m.endCol) for m in moveLog)


def _lookup_opening(moveLog):
    """Try to find a book move for the current position."""
    key = _moves_to_key(moveLog)
    if key in OPENING_BOOK:
        candidates = OPENING_BOOK[key]
        random.shuffle(candidates)
        return candidates[0]  # (startRow, startCol, endRow, endCol)
    return None


# ─────────────────────────────────────────────
# Difficulty settings
# ─────────────────────────────────────────────
DIFFICULTY_DEPTH = {
    "EASY":   1,
    "MEDIUM": 3,
    "HARD":   4,
}

# Global state
nextMove = None
SET_WHITE_AS_BOT = -1
_current_whitePawnScores = whitePawnScores
_current_blackPawnScores = blackPawnScores


def findRandomMoves(validMoves):
    return validMoves[random.randint(0, len(validMoves) - 1)]


def orderMoves(moves):
    """Simple move ordering: captures first for better alpha-beta pruning."""
    captures = [m for m in moves if m.isCapture]
    non_captures = [m for m in moves if not m.isCapture]
    return captures + non_captures


def findBestMove(gs, validMoves, returnQueue, difficulty="HARD"):
    global nextMove, _current_whitePawnScores, _current_blackPawnScores, SET_WHITE_AS_BOT
    nextMove = None
    random.shuffle(validMoves)

    depth = DIFFICULTY_DEPTH.get(difficulty, 4)

    # Easy mode: just play a random move
    if difficulty == "EASY":
        returnQueue.put(random.choice(validMoves))
        return

    # Try opening book first
    book_move_coords = _lookup_opening(gs.moveLog)
    if book_move_coords and len(gs.moveLog) < 14:
        sr, sc, er, ec = book_move_coords
        for move in validMoves:
            if move.startRow == sr and move.startCol == sc and move.endRow == er and move.endCol == ec:
                returnQueue.put(move)
                return

    # Swap pawn tables if playing as black
    if gs.playerWantsToPlayAsBlack:
        _current_whitePawnScores, _current_blackPawnScores = blackPawnScores, whitePawnScores
    else:
        _current_whitePawnScores, _current_blackPawnScores = whitePawnScores, blackPawnScores

    SET_WHITE_AS_BOT = 1 if gs.whiteToMove else -1

    orderedMoves = orderMoves(validMoves)
    findMoveNegaMaxAlphaBeta(gs, orderedMoves, depth, -CHECKMATE, CHECKMATE, SET_WHITE_AS_BOT)

    returnQueue.put(nextMove)


def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)

    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = orderMoves(gs.getValidMoves())
        score = -findMoveNegaMaxAlphaBeta(gs, nextMoves, depth - 1, -beta, -alpha, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DIFFICULTY_DEPTH.get("HARD", 4) or depth == DIFFICULTY_DEPTH.get("MEDIUM", 3):
                # Only update nextMove at the root depth
                pass
        gs.undoMove()
        if maxScore > alpha:
            alpha = maxScore
            # Update next move at root call (we detect root by checking against the stored depth)
        if alpha >= beta:
            break

    # We detect root by passing depth down; track nextMove update separately
    return maxScore


def findBestMoveRoot(gs, validMoves, returnQueue, difficulty="HARD"):
    """Wrapper that properly tracks the root-level best move."""
    global nextMove, _current_whitePawnScores, _current_blackPawnScores, SET_WHITE_AS_BOT
    nextMove = None
    random.shuffle(validMoves)

    depth = DIFFICULTY_DEPTH.get(difficulty, 4)

    if difficulty == "EASY":
        returnQueue.put(random.choice(validMoves))
        return

    # Opening book
    book_move_coords = _lookup_opening(gs.moveLog)
    if book_move_coords and len(gs.moveLog) < 14:
        sr, sc, er, ec = book_move_coords
        for move in validMoves:
            if move.startRow == sr and move.startCol == sc and move.endRow == er and move.endCol == ec:
                returnQueue.put(move)
                return

    if gs.playerWantsToPlayAsBlack:
        _current_whitePawnScores, _current_blackPawnScores = blackPawnScores, whitePawnScores
    else:
        _current_whitePawnScores, _current_blackPawnScores = whitePawnScores, blackPawnScores

    SET_WHITE_AS_BOT = 1 if gs.whiteToMove else -1
    turnMultiplier = SET_WHITE_AS_BOT

    orderedMoves = orderMoves(validMoves)
    bestScore = -CHECKMATE
    bestMove = None
    alpha = -CHECKMATE
    beta = CHECKMATE

    for move in orderedMoves:
        gs.makeMove(move)
        nextMoves = orderMoves(gs.getValidMoves())
        score = -findMoveNegaMaxAlphaBeta(gs, nextMoves, depth - 1, -beta, -alpha, -turnMultiplier)
        if score > bestScore:
            bestScore = score
            bestMove = move
        gs.undoMove()
        if score > alpha:
            alpha = score
        if alpha >= beta:
            break

    returnQueue.put(bestMove)


# Main entry point used by main.py
def findBestMove(gs, validMoves, returnQueue, difficulty="HARD"):
    findBestMoveRoot(gs, validMoves, returnQueue, difficulty)


def scoreBoard(gs):
    global _current_whitePawnScores, _current_blackPawnScores, SET_WHITE_AS_BOT

    if gs.checkmate:
        if gs.whiteToMove:
            gs.checkmate = False
            return -CHECKMATE
        else:
            gs.checkmate = False
            return CHECKMATE
    elif gs.stalemate:
        return STALEMATE

    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            square = gs.board[row][col]
            if square != "--":
                piecePositionScore = 0
                if square[1] != "K":
                    if square[1] == "p":
                        if square[0] == 'w':
                            piecePositionScore = _current_whitePawnScores[row][col]
                        else:
                            piecePositionScore = _current_blackPawnScores[row][col]
                    else:
                        piecePositionScore = piecePositionScores[square[1]][row][col]

                if SET_WHITE_AS_BOT == 1:
                    if square[0] == 'w':
                        score += pieceScore[square[1]] + piecePositionScore * 0.1
                    elif square[0] == 'b':
                        score -= pieceScore[square[1]] + piecePositionScore * 0.1
                else:
                    if square[0] == 'w':
                        score -= pieceScore[square[1]] + piecePositionScore * 0.1
                    elif square[0] == 'b':
                        score += pieceScore[square[1]] + piecePositionScore * 0.1

    return score
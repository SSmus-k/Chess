import copy
import random
from typing import List, Optional, Tuple

Piece = Tuple[str, str]  # ('K','w')
Board = List[List[Optional[Piece]]]
PIECE_POINTS = {'P':1, 'N':3, 'B':3, 'R':5, 'Q':9, 'K':0} 

class Move:
    def __init__(self, start, end, piece, captured=None, promotion=None, is_castle=False, is_en_passant=False):
        self.start = start
        self.end = end
        self.piece = piece
        self.captured = captured
        self.promotion = promotion
        self.is_castle = is_castle
        self.is_en_passant = is_en_passant


class ChessEngine:
    def __init__(self):
        self.board = self._create_start_board()
        self.score = {'w': 0, 'b': 0}

    def capture_piece(self, piece):
        p_type, color = piece
        self.score[color] += PIECE_POINTS[p_type]

    def reset(self):
        self.board = self._create_start_board()
        self.white_to_move = True
        self.move_history = []
        self.state_stack = []
        self.castling_rights = {'wK': True, 'wQ': True, 'bK': True, 'bQ': True}
        self.en_passant_target = None

    def _create_start_board(self) -> Board:
        board: Board = [[None for _ in range(8)] for _ in range(8)]

        pieces = ['R','N','B','Q','K','B','N','R']
        for i, p in enumerate(pieces):
            board[0][i] = (p, 'b')
            board[7][i] = (p, 'w')

        for i in range(8):
            board[1][i] = ('P', 'b')
            board[6][i] = ('P', 'w')

        return board


    # ---------------- MOVE HANDLING ----------------

    def make_move(self, move):
        self._push_state()
        self._apply_move(move)
        self.move_history.append(move)
        self.white_to_move = not self.white_to_move

    def undo_move(self):
        if self.state_stack:
            self.board, self.castling_rights, self.en_passant_target, self.white_to_move = self.state_stack.pop()
            if self.move_history:
                self.move_history.pop()

    def _push_state(self):
        self.state_stack.append((
            copy.deepcopy(self.board),
            copy.deepcopy(self.castling_rights),
            self.en_passant_target,
            self.white_to_move
        ))

    # ---------------- VALID MOVES ----------------

    def get_valid_moves(self):
        moves = self._generate_all_moves(self.white_to_move)
        legal_moves = []
        for move in moves:
            self._push_state()
            self._apply_move(move)
            self.white_to_move = not self.white_to_move
            if not self._is_in_check(not self.white_to_move):
                legal_moves.append(move)
            self.undo_move()
        return legal_moves

    # ---------------- CHECK DETECTION ----------------

    def is_check(self, white):
        return self._is_in_check(white)

    def _is_in_check(self, white):
        king_pos = None
        color = 'w' if white else 'b'
        for r in range(8):
            for c in range(8):
                if self.board[r][c] == ('K', color):
                    king_pos = (r,c)
                    break
        if not king_pos:
            return False

        enemy_moves = self._generate_all_moves(not white)
        return any(m.end == king_pos for m in enemy_moves)

# ------------------ Points System ------------------

    # ---------------- AI ----------------

    def get_ai_move(self, depth=2):
        moves = self.get_valid_moves()
        if not moves:
            return None
        best_move = None
        best_score = -9999 if self.white_to_move else 9999

        for move in moves:
            self._push_state()
            self._apply_move(move)
            self.white_to_move = not self.white_to_move

            score = self._minimax(depth-1, -10000, 10000, not self.white_to_move)

            self.undo_move()

            if self.white_to_move and score > best_score:
                best_score = score
                best_move = move
            elif not self.white_to_move and score < best_score:
                best_score = score
                best_move = move

        return best_move or random.choice(moves)

    def _minimax(self, depth, alpha, beta, maximizing):
        if depth == 0:
            return self.evaluate_board()

        moves = self.get_valid_moves()
        if not moves:
            return self.evaluate_board()

        if maximizing:
            max_eval = -9999
            for move in moves:
                self._push_state()
                self._apply_move(move)
                self.white_to_move = not self.white_to_move
                eval = self._minimax(depth-1, alpha, beta, False)
                self.undo_move()
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = 9999
            for move in moves:
                self._push_state()
                self._apply_move(move)
                self.white_to_move = not self.white_to_move
                eval = self._minimax(depth-1, alpha, beta, True)
                self.undo_move()
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def evaluate_board(self):
        values = {'P':1,'N':3,'B':3,'R':5,'Q':9,'K':0}
        score = 0
        for row in self.board:
            for piece in row:
                if piece:
                    val = values[piece[0]]
                    score += val if piece[1]=='w' else -val
        return score

    # ---------------- APPLY MOVE ----------------

    def _apply_move(self, move):
        sr,sc = move.start
        er,ec = move.end
        piece = self.board[sr][sc]
        self.board[sr][sc] = None

        if move.promotion:
            self.board[er][ec] = (move.promotion, piece[1])
        else:
            self.board[er][ec] = piece

    # ---------------- MOVE GENERATION (same as before but trimmed) ----------------
    # For space, reuse your existing pawn/rook/bishop/etc move functions here unchanged
    def _generate_all_moves(self, white):
            # Basic move generation for all pieces (no special moves yet)
            moves = []
            color = 'w' if white else 'b'
            for r in range(8):
                for c in range(8):
                    piece = self.board[r][c]
                    if piece and piece[1] == color:
                        if piece[0] == 'P':
                            moves.extend(self._pawn_moves(r, c, color))
                        elif piece[0] == 'N':
                            moves.extend(self._knight_moves(r, c, color))
                        elif piece[0] == 'B':
                            moves.extend(self._bishop_moves(r, c, color))
                        elif piece[0] == 'R':
                            moves.extend(self._rook_moves(r, c, color))
                        elif piece[0] == 'Q':
                            moves.extend(self._queen_moves(r, c, color))
                        elif piece[0] == 'K':
                            moves.extend(self._king_moves(r, c, color))
            return moves

    def _pawn_moves(self, r, c, color):
            moves = []
            direction = -1 if color == 'w' else 1
            start_row = 6 if color == 'w' else 1
            last_row = 0 if color == 'w' else 7
            # Forward move
            if 0 <= r + direction < 8 and self.board[r + direction][c] is None:
                # Promotion
                if r + direction == last_row:
                    for promo in ['Q', 'R', 'B', 'N']:
                        moves.append(Move((r, c), (r + direction, c), ('P', color), promotion=promo))
                else:
                    moves.append(Move((r, c), (r + direction, c), ('P', color)))
                # Double move from start
                if r == start_row and self.board[r + 2 * direction][c] is None:
                    moves.append(Move((r, c), (r + 2 * direction, c), ('P', color)))
            # Captures
            for dc in [-1, 1]:
                nc = c + dc
                if 0 <= r + direction < 8 and 0 <= nc < 8:
                    target = self.board[r + direction][nc]
                    if target and target[1] != color:
                        # Promotion
                        if r + direction == last_row:
                            for promo in ['Q', 'R', 'B', 'N']:
                                moves.append(Move((r, c), (r + direction, nc), ('P', color), captured=target, promotion=promo))
                        else:
                            moves.append(Move((r, c), (r + direction, nc), ('P', color), captured=target))
            # En passant
            if self.en_passant_target:
                ep_r, ep_c = self.en_passant_target
                if r + direction == ep_r and abs(ep_c - c) == 1:
                    moves.append(Move((r, c), (ep_r, ep_c), ('P', color), captured=('P', 'b' if color == 'w' else 'w'), is_en_passant=True))
            return moves

    def _knight_moves(self, r, c, color):
            moves = []
            for dr, dc in [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < 8 and 0 <= nc < 8:
                    target = self.board[nr][nc]
                    if not target or target[1] != color:
                        moves.append(Move((r, c), (nr, nc), ('N', color), captured=target if target and target[1] != color else None))
            return moves

    def _bishop_moves(self, r, c, color):
            moves = []
            for dr, dc in [(-1,-1),(-1,1),(1,-1),(1,1)]:
                nr, nc = r + dr, c + dc
                while 0 <= nr < 8 and 0 <= nc < 8:
                    target = self.board[nr][nc]
                    if not target:
                        moves.append(Move((r, c), (nr, nc), ('B', color)))
                    elif target[1] != color:
                        moves.append(Move((r, c), (nr, nc), ('B', color), captured=target))
                        break
                    else:
                        break
                    nr += dr
                    nc += dc
            return moves

    def _rook_moves(self, r, c, color):
            moves = []
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                nr, nc = r + dr, c + dc
                while 0 <= nr < 8 and 0 <= nc < 8:
                    target = self.board[nr][nc]
                    if not target:
                        moves.append(Move((r, c), (nr, nc), ('R', color)))
                    elif target[1] != color:
                        moves.append(Move((r, c), (nr, nc), ('R', color), captured=target))
                        break
                    else:
                        break
                    nr += dr
                    nc += dc
            return moves

    def _queen_moves(self, r, c, color):
            return self._rook_moves(r, c, color) + self._bishop_moves(r, c, color)

    def _king_moves(self, r, c, color):
            moves = []
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < 8 and 0 <= nc < 8:
                        target = self.board[nr][nc]
                        if not target or target[1] != color:
                            moves.append(Move((r, c), (nr, nc), ('K', color), captured=target if target and target[1] != color else None))
            # Castling
            if color == 'w' and r == 7 and c == 4:
                if self.castling_rights['wK'] and self.board[7][5] is None and self.board[7][6] is None:
                    moves.append(Move((7, 4), (7, 6), ('K', 'w'), is_castle=True))
                if self.castling_rights['wQ'] and self.board[7][3] is None and self.board[7][2] is None and self.board[7][1] is None:
                    moves.append(Move((7, 4), (7, 2), ('K', 'w'), is_castle=True))
            if color == 'b' and r == 0 and c == 4:
                if self.castling_rights['bK'] and self.board[0][5] is None and self.board[0][6] is None:
                    moves.append(Move((0, 4), (0, 6), ('K', 'b'), is_castle=True))
                if self.castling_rights['bQ'] and self.board[0][3] is None and self.board[0][2] is None and self.board[0][1] is None:
                    moves.append(Move((0, 4), (0, 2), ('K', 'b'), is_castle=True))
            return moves

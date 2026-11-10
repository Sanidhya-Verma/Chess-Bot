import chess


class GameError(Exception):
    """Parent class of all game related exceptions."""


class LimitError(GameError):
    """Raised in case of empty stack i.e. no move to undo."""


class GameOverError(GameError):
    """Raised in case Game is already over."""


class InvalidFen(GameError):
    """Raised in case the FEN is invalid."""


class InvalidNotation(GameError):
    """Raised in case the move notation is wrong"""


class IllegalMoveError(GameError):
    """Raised if move is illegal"""


class Game:
    def __init__(self, Fen=None):
        if Fen is not None:
            try:
                self._Board = chess.Board(Fen)
                self._Fen = Fen
            except ValueError:
                raise InvalidFen("Invalid FEN")
        else:
            self._Board = chess.Board()
            self._Fen = self._Board.fen()

    def apply_move(self, move):
        if self._Board.outcome() is not None:
            raise GameOverError(f"Game is already over \n{self._Board.outcome()}")
        try:
            mv = chess.Move.from_uci(move)
        except ValueError:
            raise InvalidNotation("Invalid move notation")
        if self._Board.is_legal(mv):
            self._Board.push(mv)
        else:
            raise IllegalMoveError("Move is illegal")

    def undo(self, times=1):
        for _ in range(times):
            if self._Board.move_stack:
                self._Board.pop()
            else:
                raise LimitError("Undo limit reached")

    def turn(self):
        return "White" if self._Board.turn else "Black"

    def legal_moves(self):
        return [move.uci() for move in self._Board.legal_moves]

    def last_move(self):
        if self._Board.move_stack:
            return self._Board.peek().uci()
        else:
            return None

    def board_copy(self):
        return self._Board.copy()

    def move_history(self):
        return [move.uci() for move in self._Board.move_stack]

    def outcome(self):
        if self._Board.is_game_over():
            win = self._Board.outcome().winner
            if win:
                win = "White"
            elif win is None:
                win = "Draw"
            else:
                win = "Black"
            return {
                "winner": win,
                "termination": self._Board.outcome().termination.name,
            }

    def snapshot(self):
        return {
            "fen": self._Board.fen(),
            "turn": self.turn(),
            "last_move": self.last_move(),
            "history": self.move_history(),
            "outcome": self.outcome(),
            "legal_moves": self.legal_moves(),
        }

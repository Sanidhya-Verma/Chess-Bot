import chess

PIECE_WEIGHTAGE = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
}


def evaluate(board: chess.Board) -> int:
    if board.is_checkmate():
        return -100000 if board.turn == chess.WHITE else 100000
    if board.is_stalemate() or board.is_insufficient_material():
        return 0
    score = 0
    for piece in board.piece_map().values():
        if piece.piece_type in PIECE_WEIGHTAGE:
            score += (-1 if piece.color == chess.BLACK else 1) * PIECE_WEIGHTAGE[
                piece.piece_type
            ]
    return score
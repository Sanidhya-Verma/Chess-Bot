import chess
from chessbot.evaluation import evaluate

def test_starting_position_is_equal():
    board = chess.Board()
    score = evaluate(board)
    assert score == 0

def test_white_extra_pawn():
    board = chess.Board()
    board.remove_piece_at(chess.A7)
    score = evaluate(board)
    assert score == 100

def test_black_extra_pawn():
    board = chess.Board()
    board.remove_piece_at(chess.A2)
    score = evaluate(board)
    assert score == -100

def test_kings_only_is_draw():
    board = chess.Board("7k/8/8/8/8/8/8/K7 w - - 0 1")
    assert evaluate(board) == 0

def test_evaluation_does_not_change_board():
    board = chess.Board()
    position_before = board.fen()

    evaluate(board)

    assert board.fen() == position_before

def test_white_checkmated():
    board = chess.Board()
    for move in["f2f3","e7e5","g2g4","d8h4"]:
        board.push_uci(move)
    assert board.is_checkmate()
    assert evaluate(board) == -100000

def test_black_checkmated():
    board = chess.Board()
    for move in["e2e4","e7e5","f1c4","b8c6","d1h5","g8f6","h5f7"]:
        board.push_uci(move)
    assert board.is_checkmate()
    assert evaluate(board) == 100000

def test_stalemate_is_draw():
    board = chess.Board("7k/5Q2/6K1/8/8/8/8/8 b - - 0 1")

    assert board.is_stalemate()
    assert evaluate(board) == 0
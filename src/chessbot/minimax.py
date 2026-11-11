import chess
from chessbot.evaluation import evaluate
def minimax_engine(depth:int,board:chess.Board)->chess.Move:
    res=-float('inf')
    best=None
    for move in board.legal_moves:
        board.push(move)
        val=-minimax(depth-1,board)
        if res<val:
            res=val
            best=move
        board.pop()
    return best
def minimax(depth:int,board:chess.Board)->int:
    if board.is_checkmate(): return -10**5
    k=1 if board.turn else -1
    if depth==0: return evaluate(board)*k
    else:
        res=-float('inf')
        for move in board.legal_moves:
            board.push(move)
            res=max(res,-minimax(depth-1,board))
            board.pop()
        return res
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import chess

from chessbot.evaluation import evaluate

app = FastAPI(
    title="Chess Bot API",
    description="API for a chess engine using Minimax, Alpha-Beta Pruning, and MCTS.",
    version="0.2.0",
)


class PositionRequest(BaseModel):
    fen: str = Field(
        default="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        description="Chess position in FEN notation.",
    )


@app.get("/")
def home():
    return {
        "message": "Chess Bot API is running!",
        "status": "online",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


def load_board(fen: str) -> chess.Board:
    try:
        return chess.Board(fen)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid FEN position.",
        )


@app.post("/board")
def get_board(request: PositionRequest):
    board = load_board(request.fen)

    return {
        "fen": board.fen(),
        "board": str(board),
        "turn": "white" if board.turn else "black",
        "is_check": board.is_check(),
        "is_checkmate": board.is_checkmate(),
        "is_stalemate": board.is_stalemate(),
        "is_game_over": board.is_game_over(),
    }


@app.post("/legal-moves")
def get_legal_moves(request: PositionRequest):
    board = load_board(request.fen)

    return {
        "fen": board.fen(),
        "side_to_move": "white" if board.turn else "black",
        "legal_moves": [move.uci() for move in board.legal_moves],
        "count": board.legal_moves.count(),
    }


@app.post("/evaluate")
def evaluate_position(request: PositionRequest):
    board = load_board(request.fen)

    try:
        score = evaluate(board)

        # Convert NumPy scalar results to ordinary Python numbers.
        if hasattr(score, "item"):
            score = score.item()

        if not isinstance(score, (int, float)):
            raise TypeError("Evaluation must return a numeric score.")

        return {
            "fen": board.fen(),
            "evaluation": score,
            "side_to_move": "white" if board.turn else "black",
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Evaluation failed: {error}",
        )
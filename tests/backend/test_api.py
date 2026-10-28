from fastapi.testclient import TestClient
from chessbot.api import app

def test_health_endpoint():
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status":"healthy"}

def test_starting_position_legal_moves():
    with TestClient(app) as client:
        response = client.post("/legal-moves",json = {})
    assert response.status_code == 200
    data = response.json()
    assert data["side_to_move"] == "white"
    assert data["count"] == 20
    assert len(data["legal_moves"]) == 20
    assert "e2e4" in data["legal_moves"]
    assert "e2e5" not in data["legal_moves"]

def test_invalid_fen_is_rejected():
    with TestClient(app) as client:
        response = client.post(
            "/board",
            json = {"fen":"not a chess position"},
        )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid FEN position."

def test_evaluation_position_with_white_advantage():
    fen = "rnbqkbnr/1ppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    with TestClient(app) as client:
        response = client.post("/evaluate",json = {"fen":fen})
    assert response.status_code == 200
    data = response.json()
    assert data["evaluation"] == 100
    assert data["side_to_move"] == "white"
    assert data["fen"] == fen

def test_board_reports_stalemate():
    fen = "7k/5Q2/6K1/8/8/8/8/8 b - - 0 1"
    with TestClient(app) as client:
        response = client.post("/board",json = {"fen":fen})
    assert response.status_code == 200
    data = response.json()
    assert data["turn"] == "black"
    assert data["is_check"] is False
    assert data["is_checkmate"] is False
    assert data["is_stalemate"] is True
    assert data["is_game_over"] is True
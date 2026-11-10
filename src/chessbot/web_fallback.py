"""No-JavaScript fallback UI for the chess bot.

Server-rendered page: chess.svg board + a text box for UCI moves.
Built on chessbot.game.Game, so all rules live in the wrapper.

Run (from the repo root, venv active):
    python -m pip install fastapi uvicorn python-multipart
    uvicorn scripts.web_fallback:app --reload     # or: python scripts/web_fallback.py
Then open http://127.0.0.1:8000

Localhost only: one global game, no auth, no sessions.
"""

import html
import random
from urllib.parse import quote

import chess
import chess.svg
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse

from chessbot.game import Game, GameError

app = FastAPI(title="Chess Bot fallback UI")
game = Game()


def bot_move(g: Game) -> str:
    """Pick the bot's reply as a UCI string.

    PLUG-IN POINT: replace the body with your minimax / MCTS engine,
    e.g. return engine.choose_move(g.board_copy()).uci()
    Engines must only ever see g.board_copy(), never the live board.
    """
    return random.choice(g.legal_moves())


def render_board() -> str:
    board = g_board = game.board_copy()
    last = game.last_move()
    lastmove = chess.Move.from_uci(last) if last else None
    check_sq = g_board.king(board.turn) if board.is_check() else None
    return chess.svg.board(board, lastmove=lastmove, check=check_sq, size=480)


def page(message: str = "") -> str:
    snap = game.snapshot()
    outcome = snap["outcome"]
    if outcome:
        status = f"Game over: {outcome['winner']} ({outcome['termination']})"
    else:
        status = f"{snap['turn']} to move"

    history = snap["history"]
    pairs = []
    for i in range(0, len(history), 2):
        pairs.append(f"{i // 2 + 1}. " + " ".join(history[i : i + 2]))
    history_html = "<br>".join(pairs) or "(no moves yet)"

    legal = ", ".join(snap["legal_moves"]) or "(none)"
    msg_html = f'<p class="err">{html.escape(message)}</p>' if message else ""
    disabled = "disabled" if outcome else ""

    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Chess Bot</title>
<style>
  body {{ font-family: sans-serif; max-width: 900px; margin: 2rem auto; padding: 0 1rem; }}
  .row {{ display: flex; gap: 2rem; flex-wrap: wrap; }}
  .err {{ color: #b00020; font-weight: bold; }}
  input[type=text] {{ font-size: 1.1rem; padding: .3rem; width: 8rem; }}
  button {{ font-size: 1rem; padding: .3rem .8rem; }}
  .legal {{ font-size: .85rem; color: #555; max-width: 480px; }}
</style></head><body>
<h1>Chess Bot</h1>
<div class="row">
  <div>{render_board()}</div>
  <div>
    <h2>{html.escape(status)}</h2>
    {msg_html}
    <form method="post" action="/move">
      <input type="text" name="uci" placeholder="e2e4" autofocus
             autocomplete="off" {disabled}>
      <label><input type="checkbox" name="bot_reply" value="1" checked>
        bot replies</label>
      <button type="submit" {disabled}>Move</button>
    </form>
    <p>UCI format: from-square + to-square, e.g. <code>g1f3</code>.
       Promotions add a letter: <code>e7e8q</code>.</p>
    <form method="post" action="/undo" style="display:inline">
      <button type="submit">Undo</button></form>
    <form method="post" action="/new" style="display:inline">
      <button type="submit">New game</button></form>
    <h3>Moves</h3><p>{history_html}</p>
  </div>
</div>
<p class="legal"><b>Legal moves:</b> {legal}</p>
</body></html>"""


def back(message: str = "") -> RedirectResponse:
    url = "/" + (f"?msg={quote(message)}" if message else "")
    return RedirectResponse(url, status_code=303)


@app.get("/", response_class=HTMLResponse)
def index(msg: str = "") -> str:
    return page(msg)


@app.post("/move")
def move(uci: str = Form(""), bot_reply: str = Form("")):
    try:
        game.apply_move(uci.strip().lower())
    except GameError as err:
        return back(f"{type(err).__name__}: {err}")
    if bot_reply and game.outcome() is None:
        game.apply_move(bot_move(game))
    return back()


@app.post("/undo")
def undo():
    try:
        game.undo()
        # With a bot opponent, undo the bot's reply too so it is your turn again.
        if game.move_history():
            game.undo()
    except GameError as err:
        return back(f"{type(err).__name__}: {err}")
    return back()


@app.post("/new")
def new_game():
    global game
    game = Game()
    return back()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)

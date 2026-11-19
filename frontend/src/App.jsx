import { useMemo, useState } from "react";
import { Chess } from "chess.js";
import { Chessboard } from "react-chessboard";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
const PROMOTION_PIECES = [
  { piece: "q", label: "Queen", symbol: "♕" },
  { piece: "r", label: "Rook", symbol: "♖" },
  { piece: "b", label: "Bishop", symbol: "♗" },
  { piece: "n", label: "Knight", symbol: "♘" },
];

function App() {
  const [game, setGame] = useState(new Chess());
  const [thinking, setThinking] = useState(false);
  const [engineInfo, setEngineInfo] = useState(null);
  const [error, setError] = useState("");
  const [selectedSquare, setSelectedSquare] = useState(null);
  const [promotion, setPromotion] = useState(null);

  const legalMoves = useMemo(() => {
    if (!selectedSquare || game.turn() !== "w" || thinking || game.isGameOver()) {
      return [];
    }
    return game.moves({ square: selectedSquare, verbose: true });
  }, [game, selectedSquare, thinking]);

  const squareStyles = useMemo(() => {
    const styles = {};
    if (selectedSquare) {
      styles[selectedSquare] = {
        background: "rgba(246, 208, 92, 0.55)",
        boxShadow: "inset 0 0 0 3px rgba(246, 208, 92, 0.95)",
      };
    }

    legalMoves.forEach((move) => {
      const isCapture = move.flags.includes("c") || move.flags.includes("e");
      styles[move.to] = isCapture
        ? {
            background:
              "radial-gradient(transparent 0 58%, rgba(225, 85, 85, 0.78) 60% 70%, transparent 72%)",
          }
        : {
            background:
              "radial-gradient(circle, rgba(30, 35, 43, 0.38) 0 18%, transparent 20%)",
          };
    });

    return styles;
  }, [selectedSquare, legalMoves]);

  async function getAIMove(currentGame) {
    setThinking(true);
    setError("");

    try {
      const response = await fetch(`${API_URL}/best-move`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ fen: currentGame.fen(), depth: 3 }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "AI request failed");
      }

      const aiGame = new Chess(currentGame.fen());
      const move = data.best_move;
      const appliedMove = aiGame.move({
        from: move.substring(0, 2),
        to: move.substring(2, 4),
        promotion: move.length === 5 ? move[4] : "q",
      });

      if (!appliedMove) throw new Error("The AI returned an invalid move.");

      setGame(aiGame);
      setEngineInfo(data);
    } catch (err) {
      setError(err.message || "Could not connect to the AI.");
    } finally {
      setThinking(false);
    }
  }

  function finishPlayerMove(from, to, promotionPiece = "q") {
    const nextGame = new Chess(game.fen());
    try {
      const move = nextGame.move({ from, to, promotion: promotionPiece });
      if (!move) return false;

      setGame(nextGame);
      setSelectedSquare(null);
      setPromotion(null);
      setEngineInfo(null);
      setError("");

      if (!nextGame.isGameOver()) getAIMove(nextGame);
      return true;
    } catch {
      return false;
    }
  }

  function attemptMove(from, to) {
    const matchingMoves = game.moves({ square: from, verbose: true }).filter(
      (move) => move.to === to,
    );
    if (matchingMoves.length === 0) return false;

    const promotionMove = matchingMoves.find((move) => move.promotion);
    if (promotionMove) {
      setPromotion({ from, to });
      setSelectedSquare(null);
      return true;
    }

    return finishPlayerMove(from, to);
  }

  function onPieceDrop({ sourceSquare, targetSquare }) {
    if (
      !targetSquare ||
      thinking ||
      promotion ||
      game.turn() !== "w" ||
      game.isGameOver()
    ) {
      return false;
    }
    return attemptMove(sourceSquare, targetSquare);
  }

  function onSquareClick({ square }) {
    if (thinking || promotion || game.turn() !== "w" || game.isGameOver()) return;

    if (selectedSquare) {
      if (selectedSquare === square) {
        setSelectedSquare(null);
        return;
      }

      const moved = attemptMove(selectedSquare, square);
      if (moved) return;
    }

    const piece = game.get(square);
    if (piece && piece.color === "w") {
      setSelectedSquare(square);
    } else {
      setSelectedSquare(null);
    }
  }

  function resetGame() {
    setGame(new Chess());
    setThinking(false);
    setEngineInfo(null);
    setError("");
    setSelectedSquare(null);
    setPromotion(null);
  }

  function undoMove() {
    if (thinking || promotion) return;
    const previousGame = new Chess(game.fen());
    if (previousGame.history().length >= 2) {
      previousGame.undo();
      previousGame.undo();
      setGame(previousGame);
      setEngineInfo(null);
      setError("");
      setSelectedSquare(null);
    }
  }

  const status = game.isGameOver()
    ? game.isCheckmate()
      ? `Checkmate — ${game.turn() === "w" ? "Black" : "White"} wins`
      : "Game drawn"
    : thinking
      ? "Engine is calculating its best move…"
      : game.isCheck()
        ? `${game.turn() === "w" ? "White" : "Black"} is in check`
        : "Your move — White";

  const moveCount = Math.ceil(game.history().length / 2);

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="/" aria-label="Chess Bot home">
          <span className="brand-mark">♞</span>
          <span>CHESS<span className="brand-accent">BOT</span></span>
        </a>
        <span className="topbar-tag">MINIMAX · ALPHA-BETA</span>
      </header>

      <section className="page-heading">
        <div>
          <p className="eyebrow">PLAY AGAINST THE ENGINE</p>
          <h1>Make your move.</h1>
          <p className="subtitle">A chess engine powered by Minimax and Alpha-Beta Pruning.</p>
        </div>
        <div className="move-counter">
          <span className="counter-label">MOVE</span>
          <strong>{String(moveCount).padStart(2, "0")}</strong>
        </div>
      </section>

      <section className="game-layout">
        <div className="board-panel">
          <div className="player-strip">
            <div className="player-avatar engine-avatar">♟</div>
            <div className="player-details">
              <strong>Chess Bot</strong>
              <span>Black · AI opponent</span>
            </div>
            <span className={`player-indicator ${thinking ? "active" : ""}`}>
              {thinking ? "THINKING" : "ENGINE"}
            </span>
          </div>

          <div className="board-frame">
            <Chessboard
              options={{
                position: game.fen(),
                onPieceDrop,
                onSquareClick,
                squareStyles,
                boardOrientation: "white",
                allowDragging: !thinking && !promotion && game.turn() === "w" && !game.isGameOver(),
                boardStyle: { borderRadius: "5px", overflow: "hidden" },
              }}
            />
          </div>

          <div className="player-strip bottom-player">
            <div className="player-avatar human-avatar">♙</div>
            <div className="player-details">
              <strong>You</strong>
              <span>White · Player</span>
            </div>
            <span className="player-indicator">YOU</span>
          </div>
        </div>

        <aside className="side-panel">
          <div className="status-card">
            <div className="status-heading">
              <span className={`status-dot ${thinking ? "thinking" : ""}`} />
              <span>GAME STATUS</span>
            </div>
            <h2>{status}</h2>
            <p className="status-hint">
              {thinking
                ? "Searching possible positions and evaluating the board."
                : game.isGameOver()
                  ? "Start a new game whenever you're ready."
                  : "Select a piece to see its legal moves, or drag it to a square."}
            </p>
          </div>

          <div className="controls-card">
            <h3>GAME CONTROLS</h3>
            <div className="button-row">
              <button className="primary-button" onClick={resetGame} disabled={thinking}>
                <span>＋</span> New game
              </button>
              <button
                className="secondary-button"
                onClick={undoMove}
                disabled={thinking || promotion || game.history().length < 2}
              >
                ↶ Undo
              </button>
            </div>
            <div className="move-guide">
              <span className="guide-dot" />
              <span>Legal move</span>
              <span className="guide-capture" />
              <span>Capture</span>
            </div>
          </div>

          <div className="engine-card">
            <div className="engine-card-heading">
              <h3>ENGINE ANALYSIS</h3>
              <span className="depth-tag">DEPTH 3</span>
            </div>
            {engineInfo ? (
              <div className="stats-grid">
                <div className="stat"><span>Best move</span><strong>{engineInfo.best_move}</strong></div>
                <div className="stat"><span>Evaluation</span><strong>{engineInfo.score}</strong></div>
                <div className="stat"><span>Nodes searched</span><strong>{engineInfo.nodes_searched.toLocaleString()}</strong></div>
                <div className="stat"><span>Leaves evaluated</span><strong>{engineInfo.leaves_evaluated.toLocaleString()}</strong></div>
                <div className="stat full-stat"><span>Alpha-Beta cutoffs</span><strong>{engineInfo.cutoffs.toLocaleString()}</strong></div>
              </div>
            ) : (
              <div className="analysis-empty">
                <span className="analysis-icon">⌁</span>
                <p>Engine statistics will appear here after the bot makes a move.</p>
              </div>
            )}
          </div>

          {error && <div className="error-card">⚠ {error}</div>}
          <p className="side-footnote">Built with React · chess.js · FastAPI</p>
        </aside>
      </section>

      {promotion && (
        <div className="modal-backdrop" role="presentation">
          <section className="promotion-modal" role="dialog" aria-modal="true" aria-labelledby="promotion-title">
            <p className="eyebrow">PAWN PROMOTION</p>
            <h2 id="promotion-title">Choose your piece</h2>
            <p>Your pawn reached the final rank. What should it become?</p>
            <div className="promotion-options">
              {PROMOTION_PIECES.map(({ piece, label, symbol }) => (
                <button
                  className="promotion-choice"
                  key={piece}
                  onClick={() => finishPlayerMove(promotion.from, promotion.to, piece)}
                >
                  <span>{symbol}</span>
                  <small>{label}</small>
                </button>
              ))}
            </div>
            <button className="cancel-promotion" onClick={() => setPromotion(null)}>
              Cancel
            </button>
          </section>
        </div>
      )}
    </main>
  );
}

export default App;

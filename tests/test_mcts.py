import chess
import pytest

from chessbot.mcts import MCTSNode


def test_node_initialization():
    board = chess.Board()
    node = MCTSNode(board)

    assert node.board is board
    assert node.parent is None
    assert node.move is None
    assert node.prior == 0.0
    assert node.children == []
    assert node.visits == 0
    assert node.value_sum == 0.0
    assert len(node.untried_moves) == 20


def test_expand_creates_child():
    root = MCTSNode(chess.Board())
    original_fen = root.board.fen()

    child = root.expand()

    assert child.parent is root
    assert child.move is not None
    assert child in root.children

    assert len(root.children) == 1
    assert len(root.untried_moves) == 19

    # Expansion must not change the parent's position.
    assert root.board.fen() == original_fen

    # The child must represent the position after one White move.
    assert child.board.fen() != original_fen
    assert child.board.turn == chess.BLACK


def test_expand_stores_prior():
    root = MCTSNode(chess.Board())

    child = root.expand(prior=0.75)

    assert child.prior == 0.75


def test_select_child_prefers_unvisited_child():
    root = MCTSNode(chess.Board())
    root.visits = 11

    visited_child = root.expand()
    unvisited_child = root.expand()

    visited_child.visits = 10
    visited_child.value_sum = 10.0

    selected = root.select_child()

    assert selected is unvisited_child


def test_prior_breaks_unvisited_tie():
    root = MCTSNode(chess.Board())

    low_prior_child = root.expand(prior=0.2)
    high_prior_child = root.expand(prior=0.8)

    selected = root.select_child()

    assert selected is high_prior_child


def test_select_child_prefers_higher_value():
    root = MCTSNode(chess.Board())
    root.visits = 20

    lower_value_child = root.expand()
    higher_value_child = root.expand()

    lower_value_child.visits = 10
    lower_value_child.value_sum = 2.0

    higher_value_child.visits = 10
    higher_value_child.value_sum = 8.0

    selected = root.select_child(c2=0.0)

    assert selected is higher_value_child


def test_backpropagate_flips_perspective():
    root = MCTSNode(chess.Board())
    child = root.expand()
    grandchild = child.expand()

    grandchild.backpropagate(1.0)

    assert grandchild.visits == 1
    assert grandchild.value_sum == 1.0

    assert child.visits == 1
    assert child.value_sum == -1.0

    assert root.visits == 1
    assert root.value_sum == 1.0


def test_backpropagate_draw():
    root = MCTSNode(chess.Board())
    child = root.expand()

    child.backpropagate(0.0)

    assert child.visits == 1
    assert child.value_sum == 0.0

    assert root.visits == 1
    assert root.value_sum == 0.0


def test_terminal_node_cannot_expand():
    # Black is checkmated.
    board = chess.Board(
        "7k/5Q2/6K1/8/8/8/8/8 b - - 0 1"
    )
    node = MCTSNode(board)

    assert node.is_terminal

    with pytest.raises(ValueError):
        node.expand()
import math
import chess
import time

from chessbot.evaluation import evaluate   


PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0,
}
CENTER_SQUARES = {chess.D4, chess.E4, chess.D5, chess.E5}
EXTENDED_CENTER = {
    chess.C3, chess.D3, chess.E3, chess.F3,
    chess.C4, chess.F4, chess.C5, chess.F5,
    chess.C6, chess.D6, chess.E6, chess.F6,
}


class MCTSNode:
    def __init__(self, board, parent=None, move=None, prior=0.0):
        self.board = board
        self.parent = parent
        self.move = move
        self.prior = prior
        self.children = []
        self.visits = 0
        self.value_sum = 0.0

# like if prior is 0.0 and we have less iteration, then lot of time waste still guess it's best to put capture and check moves first in the
#  untried moves list so that they are explored first and then the other moves are explored later. This is because 
# capture and are more likely to be good moves So expore them first later we use pop and pop takes the last element out.
        self.untried_moves = sorted(    
            board.legal_moves,
            key=lambda m: move_prior(board, m)
        )

    @property
    def is_fully_expanded(self) -> bool:
        return len(self.untried_moves) == 0

    @property
    def is_terminal(self) -> bool:
        return self.board.is_game_over(claim_draw=True)

    @property
    def average_value(self) -> float:
        if self.visits == 0:
            return 0.0

        return self.value_sum / self.visits

# if the prior part is not done and is kept at default 0.0 the selection will behave as UCB1
#  else as much better performance  decaying heuristic prior bonus is added.

    def expand(self, prior=0.0):
        if self.is_terminal:
            raise ValueError("Cannot expand a terminal node")

        if self.is_fully_expanded:
            
            raise ValueError("Node has no untried moves")

        move = self.untried_moves.pop()
        keep_stack = (self.parent is None)
        next_board = self.board.copy(stack=keep_stack)
        next_board.push(move)
        child = MCTSNode(next_board, parent=self, move=move, prior=prior)
        self.children.append(child)
        return child

    def select_child(self, c=0.5, c2=0.8):
# Unvisited children get top priority (10000), 
# AND ties are broken by whichever child has the highest prior!
        if not self.children:
            raise ValueError("Cannot select from a node with no children")

        best_child = None
        best_score = float("-inf")
        parent_visits = max(1, self.visits)

        for child in self.children:
            if child.visits == 0:
                score = 10000.0 + (c2 * child.prior)
            else:
                exploitation = child.value_sum / child.visits
                exploration = c * math.sqrt(math.log(parent_visits) / child.visits)
                prior_bonus = (c2 * child.prior) / (child.visits + 1)
                score = exploitation + exploration + prior_bonus

            if score > best_score:
                best_score = score
                best_child = child

        return best_child

    def backpropagate(self, result):
        """
        Propagates a result from this node toward the root.

        `result` is from the perspective of the player who made
         the move from this node's parent to this node.

        +1.0 = win
        0.0 = draw
        -1.0 = loss
        ...
        """
        if not (-1.0 <= result <= 1.0):
            raise ValueError("Result must be between -1.0 and 1.0")

        node = self
        current_result = result

        while node is not None:
            node.visits += 1
            node.value_sum += current_result

            current_result = -current_result
            node = node.parent

def move_prior(board, move):
    prior = 0.0
    if move.promotion == chess.QUEEN:
        prior += 1.0
    elif move.promotion is not None:
        prior -= 0.5
    if board.is_capture(move):
        attacker = board.piece_type_at(move.from_square)
        victim = chess.PAWN if board.is_en_passant(move) else board.piece_type_at(move.to_square)
        if attacker and victim:
            prior += 0.5 + 0.1 * (PIECE_VALUES[victim] - 0.5 * PIECE_VALUES[attacker])
        else:
            prior += 0.5
    if board.gives_check(move):
        prior += 0.3
    if move.to_square in CENTER_SQUARES:
        prior += 0.2
    return max(0.0, prior)

def positional_bonus(board):
    bonus = 0
    for sq, piece in board.piece_map().items():
        sign = 1 if piece.color == chess.WHITE else -1
        pt = piece.piece_type

        if pt in (chess.PAWN, chess.KNIGHT, chess.BISHOP):
            if sq in CENTER_SQUARES:
                bonus += sign * 20
            elif sq in EXTENDED_CENTER:
                bonus += sign * 10

        if pt == chess.PAWN:
            rank = chess.square_rank(sq)
            advancement = rank if piece.color == chess.WHITE else (7 - rank)
            bonus += sign * (advancement * 5)

    return bonus

def simulate(board):
    """Value of the position for White, in [-1, 1]."""
    if board.is_checkmate():
        return -1.0 if board.turn == chess.WHITE else 1.0
    if board.is_game_over(claim_draw=True) or board.is_repetition(2):
        return 0.0
    return math.tanh((evaluate(board) + positional_bonus(board)) / 400)

def mcts_search(board, iterations=1000, time_limit=None):
    if iterations < 1:
        raise ValueError("Iterations must be at least 1")

    root = MCTSNode(board.copy(stack=True))
    if root.is_terminal:
        return None

    start = time.monotonic()
    for i in range(iterations):
        if i > 0 and time_limit is not None and time.monotonic() - start >= time_limit:
            break

        # 1. Selection
        node = root
        while not node.is_terminal and node.is_fully_expanded:
            node = node.select_child()

        # 2. Expansion
        if not node.is_terminal:
            prior = move_prior(node.board, node.untried_moves[-1])
            node = node.expand(prior=prior)

        # 3. Simulation 
        white_value = simulate(node.board)

        # 4. Backpropagation 
        result = white_value if node.board.turn == chess.BLACK else -white_value
        node.backpropagate(result)

    return max(root.children, key=lambda child: child.visits).move
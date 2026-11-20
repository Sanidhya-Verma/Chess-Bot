import math
import chess
import time

from chessbot.evaluation import evaluate   


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
            key=lambda m: (board.is_capture(m), board.gives_check(m))
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
        next_board = self.board.copy(stack = False)
        next_board.push(move)
        child = MCTSNode(next_board, parent=self, move=move, prior=prior)
        self.children.append(child)
        return child

    def select_child(self, c=1.414, c2=1.0):
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
    if board.is_capture(move):
        prior += 0.5
    if board.gives_check(move):
        prior += 0.3
    return prior

def simulate(board):
    """Value of the position for White, in [-1, 1]."""
    if board.is_checkmate():
        return -1.0 if board.turn == chess.WHITE else 1.0
    if board.is_game_over(claim_draw=True):
        return 0.0
    return math.tanh(evaluate(board) / 400)

def mcts_search(board, iterations=1000, time_limit=None):
    if iterations < 1:
        raise ValueError("Iterations must be at least 1")

    root = MCTSNode(board.copy(stack=False))
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



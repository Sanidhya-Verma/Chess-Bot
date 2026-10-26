#pragma once // Safety shield: prevents the compiler from reading this file twice
#include "types.hpp"
#include <vector>
#include <string>

// Stores past board states so undo_move() can instantly restore the board during AI search
struct UndoState {
    Move move;
    int captured_piece;
    int castling_rights;
    int en_passant_sq;
    int halfmove_clock;
};

class Board {
public:
    // The chessboard represented as 64 squares (0 = a1, 7 = h1, 56 = a8, 63 = h8)
    int squares[64];

    int side_to_move;       // Whose turn is it? (WHITE or BLACK)
    int castling_rights;    // Bitmask tracking who hasn't moved their rook/king yet
    int en_passant_sq;      // Target square index for en passant capture (-1 if none)
    int halfmove_clock;     // Counts halfmoves for the 50-move draw rule
    int fullmove_number;    // Total full moves played so far

    // A stack that saves old board states so we can undo moves easily
    std::vector<UndoState> history;

    // Constructor: initializes a blank board
    Board();

    // Sets up pieces on the board using a FEN string (defaults to the standard starting position)
    void load_fen(const std::string& fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1");

    // Prints a nice text version of the board in your terminal for debugging
    void print() const;

    // Updates the board state when a move is played
    void make_move(const Move& move);

    // Reverts the last move played, using the history stack
    void undo_move();

    // CRITICAL HELPER: Returns true if square 'sq' is being attacked by 'attacker_color'
    bool is_square_attacked(int sq, int attacker_color) const;

    // Helper: Returns true if the king of the given color is currently in check
    bool in_check(int color) const;

    // Helper: Converts a square number (like 12) into chess notation (like "e2")
    static std::string sq_to_string(int sq);
};

#pragma once // Safety shield: prevents the compiler from reading this file twice

// ----------------------------------------------------------------
// 1. COLORS: Who is making the move?
// ----------------------------------------------------------------
const int WHITE = 0;
const int BLACK = 1;

// ----------------------------------------------------------------
// 2. PIECES: Unique numbers for every chess piece
// ----------------------------------------------------------------
// White pieces are 1 to 6. Black pieces are 7 to 12. 0 means empty square.
const int EMPTY = 0;
const int W_PAWN = 1, W_KNIGHT = 2, W_BISHOP = 3, W_ROOK = 4, W_QUEEN = 5, W_KING = 6;
const int B_PAWN = 7, B_KNIGHT = 8, B_BISHOP = 9, B_ROOK = 10, B_QUEEN = 11, B_KING = 12;

// ----------------------------------------------------------------
// 3. CASTLING RIGHTS: Binary flags (Who can still castle?)
// ----------------------------------------------------------------
const int NO_CASTLING = 0;
const int WHITE_OO  = 1; // White can castle Kingside
const int WHITE_OOO = 2; // White can castle Queenside
const int BLACK_OO  = 4; // Black can castle Kingside
const int BLACK_OOO = 8; // Black can castle Queenside

// ----------------------------------------------------------------
// 4. MOVE TYPES: Normal move, capture, or special move?
// ----------------------------------------------------------------
const int QUIET = 0;
const int CAPTURE = 1;
const int DOUBLE_PAWN_PUSH = 2;
const int KING_CASTLE = 3;
const int QUEEN_CASTLE = 4;
const int EN_PASSANT = 5;
const int PROMOTION = 6;

// ----------------------------------------------------------------
// 5. THE MOVE STRUCTURE: A single package holding move info
// ----------------------------------------------------------------
struct Move {
    int from_sq = 0;            // Where the piece started (0 to 63)
    int to_sq = 0;              // Where the piece is going (0 to 63)
    int promoted_piece = 0;     // If a pawn promotes, what piece does it become?
    int flag = 0;               // Is it a capture, castling, etc.?
    int score = 0;              // Used later so Alpha-Beta checks captures first
};

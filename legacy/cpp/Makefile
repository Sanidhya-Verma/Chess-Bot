CXX = g++
CXXFLAGS = -std=c++17 -O3 -Wall -Iinclude

SRCS = src/main.cpp src/board.cpp src/movegen.cpp src/evaluation.cpp src/search.cpp
TARGET = chess_bot

all:
	$(CXX) $(CXXFLAGS) $(SRCS) -o $(TARGET)

clean:
	rm -f $(TARGET)

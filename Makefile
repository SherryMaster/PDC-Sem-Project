CC = gcc
CFLAGS = -O3 -Wall -Wextra
LDFLAGS = -fopenmp -lpthread -lm
TARGET = bin/frame_analyzer
SRC = src/analyzer.c
INC = -Iinclude

.PHONY: all clean gui generate benchmark

all: $(TARGET)

$(TARGET): $(SRC) include/analyzer.h
	@mkdir -p bin
	$(CC) $(CFLAGS) $(INC) $(SRC) -o $(TARGET) $(LDFLAGS)

clean:
	rm -f $(TARGET)
	rm -rf test_frames/*.ppm
	rm -rf test_frames_output

generate:
	python3 scripts/generate_frames.py

benchmark: $(TARGET)
	./$(TARGET) --benchmark --dir test_frames --workers 4

gui: $(TARGET)
	python3 gui.py

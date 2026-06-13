CC = gcc
CFLAGS = -O3 -Wall -Wextra
LDFLAGS = -fopenmp -lpthread -lm
TARGET = bin/frame_analyzer
SRCS = src/analyzer.c src/ppm.c src/sobel.c src/system_info.c src/report.c
OBJS = $(SRCS:.c=.o)
INC = -Iinclude

.PHONY: all clean gui generate benchmark

all: $(TARGET)

$(TARGET): $(OBJS)
	@mkdir -p bin
	$(CC) $(OBJS) -o $(TARGET) $(LDFLAGS)

src/%.o: src/%.c include/analyzer.h include/ppm.h include/sobel.h include/system_info.h include/report.h
	$(CC) $(CFLAGS) $(INC) -c $< -o $@

clean:
	rm -f $(OBJS) $(TARGET)
	rm -rf test_frames/*.ppm
	rm -rf test_frames_output

generate:
	python3 scripts/generate_frames.py

benchmark: $(TARGET)
	./$(TARGET) --benchmark --dir test_frames --workers 4

gui: $(TARGET)
	python3 gui.py

CC = gcc
CFLAGS = -O3 -Wall -Wextra
LDFLAGS = -fopenmp -lpthread -lm
TARGET = bin/frame_analyzer
SRCS = src/analyzer.c src/ppm.c src/sobel.c src/system_info.c src/report.c
OBJS = $(SRCS:.c=.o)
INC = -Iinclude

.PHONY: all clean gui generate benchmark report

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

graphical: $(TARGET)
	python3 gui.py

# Build the DOCX project report from report_content.json + figures.
# Uses the project-local virtualenv at .venv/ for python-docx and Pillow.
report: .venv/bin/python scripts/report_content.json scripts/figures/ucp_logo.jpg scripts/figures/input.png scripts/figures/output.png
	.venv/bin/python scripts/build_report.py
	.venv/bin/python scripts/verify_report.py

.venv/bin/python:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt

scripts/figures/ucp_logo.jpg:
	bash scripts/figures/fetch_ucp_logo.sh

scripts/figures/input.png scripts/figures/output.png: scripts/figures/make_figures.py $(wildcard test_frames/frame_0000.ppm)
	.venv/bin/python scripts/figures/make_figures.py

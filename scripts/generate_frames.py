#!/usr/bin/env python3
import os
import random

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "test_frames")
WIDTH = 512
HEIGHT = 512
NUM_FRAMES = 20
MAX_COLOR = 255

def random_color():
    return (random.randint(0, MAX_COLOR), random.randint(0, MAX_COLOR), random.randint(0, MAX_COLOR))

def draw_rect(pixels, w, h, x0, y0, rw, rh, color):
    for y in range(max(0, y0), min(h, y0 + rh)):
        for x in range(max(0, x0), min(w, x0 + rw)):
            idx = (y * w + x) * 3
            pixels[idx] = color[0]
            pixels[idx+1] = color[1]
            pixels[idx+2] = color[2]

def draw_circle(pixels, w, h, cx, cy, r, color):
    for y in range(max(0, cy - r), min(h, cy + r)):
        for x in range(max(0, cx - r), min(w, cx + r)):
            if (x - cx)**2 + (y - cy)**2 <= r**2:
                idx = (y * w + x) * 3
                pixels[idx] = color[0]
                pixels[idx+1] = color[1]
                pixels[idx+2] = color[2]

def draw_triangle(pixels, w, h, x0, y0, size, color):
    for y in range(max(0, y0), min(h, y0 + size)):
        frac = (y - y0) / max(size, 1)
        half = int(size * (1 - frac) / 2)
        for x in range(max(0, x0 - half), min(w, x0 + half)):
            idx = (y * w + x) * 3
            pixels[idx] = color[0]
            pixels[idx+1] = color[1]
            pixels[idx+2] = color[2]

def draw_line(pixels, w, h, x0, y0, x1, y1, thickness, color):
    steps = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(steps + 1):
        t = i / steps
        x = int(x0 + (x1 - x0) * t)
        y = int(y0 + (y1 - y0) * t)
        for dy in range(-thickness // 2, thickness // 2 + 1):
            for dx in range(-thickness // 2, thickness // 2 + 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h:
                    idx = (ny * w + nx) * 3
                    pixels[idx] = color[0]
                    pixels[idx+1] = color[1]
                    pixels[idx+2] = color[2]

def generate_frame(frame_idx):
    pixels = bytearray(WIDTH * HEIGHT * 3)
    bg = random_color()
    for i in range(0, len(pixels), 3):
        pixels[i] = bg[0]
        pixels[i+1] = bg[1]
        pixels[i+2] = bg[2]

    num_shapes = random.randint(5, 12)
    for _ in range(num_shapes):
        shape = random.choice(["rect", "circle", "triangle", "line"])
        color = random_color()
        if shape == "rect":
            x0 = random.randint(0, WIDTH - 50)
            y0 = random.randint(0, HEIGHT - 50)
            rw = random.randint(30, 200)
            rh = random.randint(30, 200)
            draw_rect(pixels, WIDTH, HEIGHT, x0, y0, rw, rh, color)
        elif shape == "circle":
            cx = random.randint(50, WIDTH - 50)
            cy = random.randint(50, HEIGHT - 50)
            r = random.randint(20, 120)
            draw_circle(pixels, WIDTH, HEIGHT, cx, cy, r, color)
        elif shape == "triangle":
            x0 = random.randint(50, WIDTH - 50)
            y0 = random.randint(50, HEIGHT - 100)
            size = random.randint(40, 150)
            draw_triangle(pixels, WIDTH, HEIGHT, x0, y0, size, color)
        elif shape == "line":
            x0 = random.randint(0, WIDTH)
            y0 = random.randint(0, HEIGHT)
            x1 = random.randint(0, WIDTH)
            y1 = random.randint(0, HEIGHT)
            draw_line(pixels, WIDTH, HEIGHT, x0, y0, x1, y1, random.randint(2, 6), color)

    return bytes(pixels)

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Generating {NUM_FRAMES} frames ({WIDTH}x{HEIGHT}) in {OUTPUT_DIR}...")
    for i in range(NUM_FRAMES):
        pixels = generate_frame(i)
        filepath = os.path.join(OUTPUT_DIR, f"frame_{i:04d}.ppm")
        with open(filepath, "w") as f:
            f.write(f"P3\n{WIDTH} {HEIGHT}\n{MAX_COLOR}\n")
            for j in range(0, len(pixels), 3):
                f.write(f"{pixels[j]} {pixels[j+1]} {pixels[j+2]}\n")
        print(f"  Generated frame_{i:04d}.ppm")
    print(f"Done. {NUM_FRAMES} frames written to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()

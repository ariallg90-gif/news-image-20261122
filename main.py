#!/usr/bin/env python3
"""The World in One Page -- 22 November 2026.

A one-page newspaper front page summarising six world news stories from
Sunday 22 November 2026, drawn entirely in code: a hand-rolled PNG
encoder, a tiny rasteriser and a home-made 5x7 bitmap font. Standard
library only, no network, fully deterministic.
"""

import math
import os
import struct
import sys
import zlib

W, H = 1024, 1024
OUT = "/output/entry.png"

PAPER = (245, 239, 224)
INK = (20, 20, 20)
RED = (176, 32, 32)
BLUE = (31, 78, 121)
GREY = (110, 104, 90)
LIGHT = (232, 224, 205)


# ---------------------------------------------------------------- PNG encoder
def _chunk(tag, data):
    out = struct.pack(">I", len(data)) + tag + data
    out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    return out


def write_png(path, pixels, w, h):
    """pixels: flat list of (r, g, b) rows, top to bottom."""
    raw = bytearray()
    for y in range(h):
        raw.append(0)  # filter: none
        row = pixels[y * w:(y + 1) * w]
        for (r, g, b) in row:
            raw += bytes((r, g, b))
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


# ------------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = [bg] * (w * h)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.px[y * self.w + x] = c

    def rect(self, x, y, w, h, c):
        for yy in range(max(0, y), min(self.h, y + h)):
            base = yy * self.w
            for xx in range(max(0, x), min(self.w, x + w)):
                self.px[base + xx] = c

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.rect(x, y, t, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, fill=False):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = math.hypot(xx - cx, yy - cy)
                if fill:
                    if d <= r:
                        self.set(xx, yy, c)
                elif r - 0.7 <= d <= r + 0.7:
                    self.set(xx, yy, c)

    def triangle(self, x0, y0, x1, y1, x2, y2, c):
        self.line(x0, y0, x1, y1, c)
        self.line(x1, y1, x2, y2, c)
        self.line(x2, y2, x0, y0, c)


# ------------------------------------------------------- 5x7 bitmap font
# Each glyph: 7 rows of 5 cells, '#' = ink, '.' = empty. Drawn by hand.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
}

FONT.update({
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", "01100", "01100"),
    ",": (".....", ".....", ".....", ".....", "01100", "00100", "01000"),
    ":": (".....", "01100", "01100", ".....", "01100", "01100", "....."),
    ";": (".....", "01100", "01100", ".....", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", ".....", ".....", ".....", "....."),
    '"': ("01010", "01010", ".....", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "01110", ".....", ".....", "....."),
    "!": ("00100", "00100", "00100", "00100", "00100", ".....", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", ".....", "00100"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": (".....", "00100", "00100", "11111", "00100", "00100", "....."),
    "=": (".....", ".....", "11111", ".....", "11111", ".....", "....."),
    "*": (".....", "10101", "01110", "11111", "01110", "10101", "....."),
})


# ------------------------------------------------------------------- text
def text_width(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(cv, x, y, s, scale, color):
    """Draw uppercase text; unknown chars become a space."""
    cx = x
    for ch in s.upper():
        g = FONT.get(ch, FONT[" "])
        for gy, row in enumerate(g):
            for gx, bit in enumerate(row):
                if bit == "1":
                    cv.rect(cx + gx * scale, y + gy * scale,
                            scale, scale, color)
        cx += 6 * scale
    return cx


def draw_text_centered(cv, cx, y, s, scale, color):
    draw_text(cv, cx - text_width(s, scale) // 2, y, s, scale, color)


def wrap_text(s, max_width, scale):
    """Greedy word wrap; returns a list of lines fitting max_width px."""
    words = s.upper().split(" ")
    lines, cur = [], ""
    for w in words:
        trial = w if not cur else cur + " " + w
        if text_width(trial, scale) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_para(cv, x, y, s, scale, color, max_width, line_h):
    lines = wrap_text(s, max_width, scale)
    for i, ln in enumerate(lines):
        draw_text(cv, x, y + i * line_h, ln, scale, color)
    return y + len(lines) * line_h


# ------------------------------------------------------------------- icons
def draw_icon(cv, kind, x, y, s, color):
    """Small geometric emblem inside a s x s box at (x, y)."""
    cx, cy = x + s // 2, y + s // 2
    if kind == "globe":
        cv.circle(cx, cy, s // 2 - 2, color)
        cv.hline(x + 3, cy, s - 6, color)
        cv.vline(cx, y + 3, s - 6, color)
        cv.line(x + 8, y + 10, x + s - 8, y + 10, color)
        cv.line(x + 8, y + s - 10, x + s - 8, y + s - 10, color)
    elif kind == "ship":
        cv.line(x + 6, y + s - 12, x + s - 6, y + s - 12, color)
        cv.line(x + 10, y + s - 12, x + 14, y + s - 4, color)
        cv.line(x + s - 10, y + s - 12, x + s - 14, y + s - 4, color)
        cv.line(x + 14, y + s - 4, x + s - 14, y + s - 4, color)
        cv.vline(cx, y + 6, s - 20, color)
        cv.triangle(cx, y + 6, cx, y + 16, cx + 12, y + 16, color)
        cv.hline(x + 4, y + s - 1, 10, color)
        cv.hline(x + s - 14, y + s - 1, 10, color)
    elif kind == "blast":
        for k in range(8):
            a = math.pi * k / 4.0
            cv.line(cx, cy,
                    int(cx + (s // 2 - 3) * math.cos(a)),
                    int(cy + (s // 2 - 3) * math.sin(a)), color)
        cv.circle(cx, cy, 6, color, fill=True)
    elif kind == "star":
        pts = []
        for k in range(10):
            r = s // 2 - 2 if k % 2 == 0 else s // 5
            a = -math.pi / 2 + math.pi * k / 5.0
            pts.append((int(cx + r * math.cos(a)),
                        int(cy + r * math.sin(a))))
        for k in range(10):
            x0, y0 = pts[k]
            x1, y1 = pts[(k + 1) % 10]
            cv.line(x0, y0, x1, y1, color)
    elif kind == "plane":
        cv.line(x + 4, cy, x + s - 4, cy, color)
        cv.line(x + s - 12, cy - 8, x + s - 4, cy, color)
        cv.line(x + s - 12, cy + 8, x + s - 4, cy, color)
        cv.line(cx - 4, cy - 12, cx + 6, cy, color)
        cv.line(cx - 4, cy + 12, cx + 6, cy, color)
        cv.line(x + 6, cy - 6, x + 10, cy, color)
        cv.line(x + 6, cy + 6, x + 10, cy, color)
    elif kind == "flame":
        cv.triangle(cx, y + 4, x + 8, y + s - 8, x + s - 8, y + s - 8, color)
        cv.triangle(cx, y + 16, x + 16, y + s - 8, x + s - 16, y + s - 8, color)
        cv.circle(cx, y + s - 14, 4, color, fill=True)


# ----------------------------------------------------------------- stories
# Summaries written from the research notes for this page; facts checked
# against Reuters / AP reporting dated Sunday 22 November 2026.
STORIES = [
    ("CLIMATE - ANTALYA, TURKEY", "CLIMATE TALKS COLLAPSE",
     "COP31 in Antalya ended with no final deal after the EU and others "
     "rejected a draft that left fossil fuels unmentioned. Deadlock over "
     "quitting oil, gas and coal broke the summit.",
     "REUTERS", "globe"),
    ("ENERGY - STRAIT OF HORMUZ", "TANKERS HIT NEAR HORMUZ",
     "Iran said two supertankers hit mines east of the strait and caught "
     "fire. Trump threatened to sink ships that defy the US naval blockade "
     "as oil markets braced for trouble.",
     "REUTERS", "ship"),
    ("CONFLICT - BENGHAZI, LIBYA", "RUSSIAN WARSHIP SUNK",
     "Zelenskyy confirmed Ukraine was behind a drone attack that sank a "
     "Russian warship docked in Benghazi. Libya's eastern government blamed "
     "a drone strike.",
     "AP", "blast"),
    ("SECURITY - SINALOA, MEXICO", "CARTEL KINGPIN CAPTURED",
     "Mexican forces seized FBI most-wanted fugitive Fausto Isidro Meza "
     "Flores, known as El Chapo Isidro. The raid in Guasave left 11 dead "
     "and set off burning roadblocks.",
     "AP", "star"),
    ("TRAVEL - UNITED STATES", "DELTA OUTAGE GROUNDS FLIGHTS",
     "A system failure that calculates each plane's weight and balance "
     "delayed more than 1,600 Delta flights. The FAA briefly halted "
     "Atlanta-bound jets as crews did the math by hand.",
     "AP", "plane"),
    ("DISASTER - INDONESIA", "FACTORY FIRE: 34 MISSING",
     "More remains were recovered after a blaze tore through a candy "
     "factory, leaving 34 workers missing. Rescuers kept digging through "
     "the wreckage as families waited for news.",
     "AP", "flame"),
]


# ------------------------------------------------------------------ layout
def draw_cell(cv, x, y, w, h, story):
    kicker, headline, summary, source, icon = story
    cv.rect(x, y, w, 1, INK)
    cv.rect(x, y, 1, h, INK)
    cv.rect(x + w - 1, y, 1, h, INK)
    cv.rect(x, y + h - 1, w, 1, INK)
    draw_icon(cv, icon, x + w - 56, y + 10, 44, BLUE)
    draw_text(cv, x + 14, y + 14, kicker, 2, RED)
    draw_para(cv, x + 14, y + 42, headline, 3, INK, w - 84, 26)
    cv.hline(x + 14, y + 100, w - 28, GREY)
    draw_para(cv, x + 14, y + 112, summary, 2, INK, w - 28, 17)
    draw_text(cv, x + 14, y + h - 24, "SOURCE: " + source, 1, GREY)


def build():
    cv = Canvas(W, H, PAPER)
    # Top strip
    draw_text(cv, 28, 12, "SUNDAY EDITION", 1, GREY)
    draw_text(cv, W - 28 - text_width("NO. 22", 1), 12, "NO. 22", 1, GREY)
    # Masthead
    draw_text_centered(cv, W // 2, 30, "THE WORLD IN ONE PAGE", 6, INK)
    cv.hline(28, 86, W - 56, INK, 4)
    draw_text_centered(cv, W // 2, 100, "SUNDAY, 22 NOVEMBER 2026", 3, RED)
    draw_text_centered(cv, W // 2, 130,
                       "SIX STORIES THAT SHAPED THE DAY", 2, INK)
    cv.hline(28, 154, W - 56, INK, 2)
    # Story grid: 2 columns x 3 rows
    col_w, row_h = 476, 262
    for i, story in enumerate(STORIES):
        cx = 28 + (i % 2) * (col_w + 16)
        cy = 166 + (i // 2) * (row_h + 12)
        draw_cell(cv, cx, cy, col_w, row_h, story)
    # Footer
    draw_text_centered(
        cv, W // 2, 988,
        "ALL STORIES FIRST REPORTED SUNDAY 22 NOVEMBER 2026 - SOURCES: "
        "REUTERS, AP, BBC", 1, GREY)
    return cv


def main():
    os.makedirs("/output", exist_ok=True)
    cv = build()
    write_png(OUT, cv.px, W, H)
    size = os.path.getsize(OUT)
    print("wrote %s (%d bytes, %dx%d)" % (OUT, size, W, H))
    if size > 1048576:
        print("ERROR: over 1 MiB", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

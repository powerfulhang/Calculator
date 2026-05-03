# File Name: generate_icon.py
# Author: hang.shi
# Time: 2026-05-03
# Version: 2.0
# Description: Generate a calculator application icon (.ico) with proper multi-size support.

from __future__ import annotations

from PIL import Image, ImageDraw, ImageFont

__author__ = "hang.shi"


ICON_SIZES = [256, 128, 64, 48, 32, 16]


def _draw_calculator(size: int) -> Image.Image:
    """Draw a calculator icon at the given pixel size."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    scale = size / 256.0

    # --- Body: rounded rectangle ---
    margin = int(16 * scale)
    radius = int(24 * scale)
    draw.rounded_rectangle(
        [margin, margin, size - margin, size - margin],
        radius=radius,
        fill="#3B3B3B",
        outline="#2A2A2A",
        width=max(1, int(3 * scale)),
    )

    # --- Display area ---
    dx1 = int(36 * scale)
    dy1 = int(36 * scale)
    dx2 = size - int(36 * scale)
    dy2 = int(80 * scale)
    draw.rounded_rectangle(
        [dx1, dy1, dx2, dy2],
        radius=max(1, int(8 * scale)),
        fill="#D4D4D4",
    )

    # Display text
    font_size = max(10, int(32 * scale))
    try:
        font = ImageFont.truetype("consola.ttf", font_size)
    except OSError:
        font = ImageFont.load_default()
    draw.text((dx2 - int(60 * scale), dy1 + int(8 * scale)), "123", fill="#1A1A1A", font=font)

    # --- Button grid: 4 columns x 4 rows ---
    top = int(96 * scale)
    bottom = size - int(28 * scale)
    left = int(36 * scale)
    right = size - int(36 * scale)

    cols, rows = 4, 4
    gap = max(1, int(6 * scale))
    cell_w = (right - left - gap * (cols - 1)) / cols
    cell_h = (bottom - top - gap * (rows - 1)) / rows

    button_labels = [
        ["7", "8", "9", "÷"],
        ["4", "5", "6", "×"],
        ["1", "2", "3", "-"],
        ["0", ".", "=", "+"],
    ]
    op_chars = {"÷", "×", "-", "+", "="}

    btn_font_size = max(8, int(22 * scale))
    try:
        btn_font = ImageFont.truetype("consola.ttf", btn_font_size)
    except OSError:
        btn_font = ImageFont.load_default()

    for r in range(rows):
        for c in range(cols):
            x1 = int(left + c * (cell_w + gap))
            y1 = int(top + r * (cell_h + gap))
            x2 = int(x1 + cell_w)
            y2 = int(y1 + cell_h)

            label = button_labels[r][c]
            fill = "#6B6B6B" if label in op_chars else "#505050"
            draw.rounded_rectangle([x1, y1, x2, y2], radius=max(1, int(6 * scale)), fill=fill)

            bbox = draw.textbbox((0, 0), label, font=btn_font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            tx = x1 + (cell_w - tw) / 2
            ty = y1 + (cell_h - th) / 2 - max(1, int(2 * scale))
            draw.text((int(tx), int(ty)), label, fill="#FFFFFF", font=btn_font)

    return img


def generate_icon(output_path: str = "calculator.ico") -> None:
    """Generate a multi-size .ico file suitable for Windows."""
    images = [_draw_calculator(s) for s in ICON_SIZES]
    # First image is the base; rest are appended as additional sizes
    images[0].save(
        output_path,
        format="ICO",
        sizes=[(s, s) for s in ICON_SIZES],
        append_images=images[1:],
    )
    print(f"Icon saved to {output_path} ({len(ICON_SIZES)} sizes)")


if __name__ == "__main__":
    generate_icon("calculator.ico")

#!/usr/bin/env python3

from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WIDTH = 80
HEIGHT = 22
CHARSET = ".,-~:;=!*#$@"
FG_COLOR = "#9df79d"
BG_COLOR = "#050505"
PADDING_X = 24
PADDING_Y = 20


def render_ascii_frame(a: float, b: float) -> str:
    output = [" "] * (WIDTH * HEIGHT)
    zbuffer = [0.0] * (WIDTH * HEIGHT)

    theta = 0.0
    while theta < 2 * math.pi:
        costheta = math.cos(theta)
        sintheta = math.sin(theta)

        phi = 0.0
        while phi < 2 * math.pi:
            cosphi = math.cos(phi)
            sinphi = math.sin(phi)

            circlex = 2 + costheta
            circley = sintheta

            x = circlex * (math.cos(b) * cosphi + math.sin(a) * math.sin(b) * sinphi) - circley * math.cos(a) * math.sin(b)
            y = circlex * (math.sin(b) * cosphi - math.sin(a) * math.cos(b) * sinphi) + circley * math.cos(a) * math.cos(b)
            z = 5 + math.cos(a) * circlex * sinphi + circley * math.sin(a)
            ooz = 1 / z

            xp = int(WIDTH / 2 + 30 * ooz * x)
            yp = int(HEIGHT / 2 - 15 * ooz * y)

            luminance = (
                cosphi * costheta * math.sin(b)
                - math.cos(a) * costheta * sinphi
                - math.sin(a) * sintheta
                + math.cos(b) * (math.cos(a) * sintheta - costheta * math.sin(a) * sinphi)
            )

            idx = xp + WIDTH * yp
            if 0 <= yp < HEIGHT and 0 <= xp < WIDTH and ooz > zbuffer[idx]:
                zbuffer[idx] = ooz
                output[idx] = CHARSET[max(0, int(luminance * 8))]

            phi += 0.02
        theta += 0.07

    lines = ["".join(output[row * WIDTH : (row + 1) * WIDTH]) for row in range(HEIGHT)]
    return "\n".join(lines)


def load_font(font_size: int) -> ImageFont.ImageFont | ImageFont.FreeTypeFont:
    font_candidates = [
        "DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/Library/Fonts/Menlo.ttc",
        "C:\\Windows\\Fonts\\consola.ttf",
    ]

    for candidate in font_candidates:
        try:
            return ImageFont.truetype(candidate, font_size)
        except OSError:
            continue

    return ImageFont.load_default()


def frame_to_image(text: str, font: ImageFont.ImageFont | ImageFont.FreeTypeFont) -> Image.Image:
    dummy = Image.new("RGB", (1, 1), BG_COLOR)
    draw = ImageDraw.Draw(dummy)
    bbox = draw.multiline_textbbox((0, 0), text, font=font, spacing=4)
    width = bbox[2] - bbox[0] + PADDING_X * 2
    height = bbox[3] - bbox[1] + PADDING_Y * 2

    image = Image.new("RGB", (width, height), BG_COLOR)
    draw = ImageDraw.Draw(image)
    draw.multiline_text(
        (PADDING_X, PADDING_Y),
        text,
        font=font,
        fill=FG_COLOR,
        spacing=4,
    )
    return image


def build_gif(output_path: Path, frames: int, font_size: int, duration_ms: int) -> None:
    font = load_font(font_size)
    images = []

    for frame_index in range(frames):
        a = frame_index * 0.07
        b = frame_index * 0.03
        text = render_ascii_frame(a, b)
        images.append(frame_to_image(text, font))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    images[0].save(
        output_path,
        save_all=True,
        append_images=images[1:],
        duration=duration_ms,
        loop=0,
        optimize=False,
        disposal=2,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render an ASCII spinning donut GIF.")
    parser.add_argument("--output", type=Path, default=Path("assets/spinning-donut.gif"))
    parser.add_argument("--frames", type=int, default=90)
    parser.add_argument("--font-size", type=int, default=16)
    parser.add_argument("--duration-ms", type=int, default=40)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    build_gif(args.output, args.frames, args.font_size, args.duration_ms)


if __name__ == "__main__":
    main()

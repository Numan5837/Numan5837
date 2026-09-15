from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "header.gif"
WIDTH, HEIGHT = 1200, 340
FPS = 8
SECONDS = 8
FRAME_COUNT = FPS * SECONDS


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        Path("C:/Windows/Fonts") / name,
        Path("/usr/share/fonts/truetype/dejavu") / name,
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


FONT_NAME = font("segoeuib.ttf", 60)
FONT_SUBTITLE = font("segoeui.ttf", 22)
FONT_MONO = font("consola.ttf", 16)
FONT_MONO_BOLD = font("consolab.ttf", 16)
FONT_MONO_SMALL = font("consola.ttf", 13)


def mix(a: tuple[int, int, int], b: tuple[int, int, int], amount: float) -> tuple[int, int, int]:
    return tuple(round(x + (y - x) * amount) for x, y in zip(a, b))


def make_background() -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT))
    pixels = image.load()
    left = (5, 15, 28)
    middle = (9, 25, 42)
    right = (18, 36, 58)
    for x in range(WIDTH):
        ratio = x / (WIDTH - 1)
        color = mix(left, middle, ratio / 0.55) if ratio < 0.55 else mix(middle, right, (ratio - 0.55) / 0.45)
        for y in range(HEIGHT):
            vertical = 1.0 - 0.07 * (y / HEIGHT)
            pixels[x, y] = tuple(round(channel * vertical) for channel in color)

    draw = ImageDraw.Draw(image, "RGBA")
    for x in range(0, WIDTH, 38):
        draw.line((x, 0, x, HEIGHT), fill=(143, 179, 216, 18), width=1)
    for y in range(0, HEIGHT, 38):
        draw.line((0, y, WIDTH, y), fill=(143, 179, 216, 18), width=1)
    draw.ellipse((950, -150, 1300, 200), fill=(82, 116, 255, 18))
    draw.ellipse((-135, 225, 230, 590), fill=(48, 213, 178, 14))
    draw.rounded_rectangle((1, 1, WIDTH - 2, HEIGHT - 2), radius=24, outline=(44, 70, 97, 220), width=2)
    return image


def glow_dot(image: Image.Image, center: tuple[int, int], color: tuple[int, int, int], radius: int, strength: float) -> None:
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")
    x, y = center
    draw.ellipse((x - radius * 3, y - radius * 3, x + radius * 3, y + radius * 3), fill=(*color, round(70 * strength)))
    layer = layer.filter(ImageFilter.GaussianBlur(radius * 1.7))
    image.alpha_composite(layer)
    draw = ImageDraw.Draw(image, "RGBA")
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*color, round(230 * strength)))


def quadratic(p0: tuple[float, float], p1: tuple[float, float], p2: tuple[float, float], t: float) -> tuple[int, int]:
    inv = 1 - t
    return (
        round(inv * inv * p0[0] + 2 * inv * t * p1[0] + t * t * p2[0]),
        round(inv * inv * p0[1] + 2 * inv * t * p1[1] + t * t * p2[1]),
    )


def reveal(text: str, elapsed: float, start: float, rate: float = 18.0) -> str:
    if elapsed < start:
        return ""
    count = min(len(text), max(0, int((elapsed - start) * rate)))
    return text[:count]


def draw_static() -> Image.Image:
    image = make_background().convert("RGBA")
    draw = ImageDraw.Draw(image, "RGBA")

    # Terminal mark.
    draw.rounded_rectangle((66, 46, 124, 104), radius=15, fill=(12, 34, 54, 255), outline=(85, 230, 204, 255), width=2)
    draw.line((82, 65, 93, 75, 82, 85), fill=(116, 240, 220, 255), width=3, joint="curve")
    draw.line((99, 85, 111, 85), fill=(116, 240, 220, 255), width=3)
    draw.text((142, 58), "SYSTEMS ONLINE", font=FONT_MONO_SMALL, fill=(122, 157, 188, 255))

    draw.text((66, 117), "Numan S.", font=FONT_NAME, fill=(244, 248, 253, 255), stroke_width=1, stroke_fill=(244, 248, 253, 255))
    draw.rounded_rectangle((66, 190, 595, 194), radius=2, fill=(80, 108, 139, 255))
    draw.text((66, 213), "Agent evaluation · Verifier engineering · Cloud-native systems", font=FONT_SUBTITLE, fill=(193, 208, 223, 255))
    draw.text((66, 254), "> exact grading  /  reproducible runs  /  failure analysis", font=FONT_MONO_SMALL, fill=(102, 144, 180, 255))

    chips = [
        (66, 285, 166, "Python", (93, 231, 207)),
        (178, 285, 278, "Docker", (111, 175, 255)),
        (290, 285, 400, "Harbor", (188, 157, 255)),
    ]
    for x1, y1, x2, label, color in chips:
        draw.rounded_rectangle((x1, y1, x2, y1 + 37), radius=18, fill=(11, 31, 49, 255), outline=(48, 77, 103, 255))
        box = draw.textbbox((0, 0), label, font=FONT_MONO_SMALL)
        text_width = box[2] - box[0]
        draw.text(((x1 + x2 - text_width) / 2, y1 + 10), label, font=FONT_MONO_SMALL, fill=(*color, 255))

    # Validation terminal.
    panel = (672, 35, 1140, 306)
    draw.rounded_rectangle(panel, radius=19, fill=(7, 20, 34, 244), outline=(48, 75, 103, 255), width=2)
    draw.rounded_rectangle((672, 35, 1140, 73), radius=19, fill=(13, 34, 54, 255))
    draw.rectangle((672, 54, 1140, 73), fill=(13, 34, 54, 255))
    draw.ellipse((691, 50, 701, 60), fill=(255, 105, 122, 255))
    draw.ellipse((710, 50, 720, 60), fill=(242, 201, 76, 255))
    draw.ellipse((729, 50, 739, 60), fill=(85, 230, 165, 255))
    draw.text((758, 47), "validate / replica-reconciliation", font=FONT_MONO_SMALL, fill=(139, 171, 201, 255))

    labels = ["docker validation", "oracle reward", "no-op reward", "GPT-5.6 Sol"]
    for index, label in enumerate(labels):
        y = 88 + index * 36
        draw.text((702, y), label, font=FONT_MONO, fill=(153, 175, 197, 255))
        draw.line((860, y + 13, 1037, y + 13), fill=(42, 66, 87, 255), width=1)

    # Compact data path at the base of the terminal.
    draw.line((730, 248, 833, 248), fill=(60, 112, 123, 255), width=2)
    draw.line((730, 277, 833, 248), fill=(58, 100, 143, 255), width=2)
    draw.line((873, 248, 974, 248), fill=(112, 87, 163, 255), width=2)
    for x, y, label, color in [
        (715, 248, "A", (85, 230, 204)),
        (715, 277, "B", (101, 167, 255)),
        (853, 248, "S", (176, 140, 255)),
        (994, 248, "✓", (85, 230, 165)),
    ]:
        draw.ellipse((x - 15, y - 15, x + 15, y + 15), fill=(14, 38, 59, 255), outline=(*color, 255), width=2)
        box = draw.textbbox((0, 0), label, font=FONT_MONO_BOLD)
        tw, th = box[2] - box[0], box[3] - box[1]
        draw.text((x - tw / 2, y - th / 2 - 2), label, font=FONT_MONO_BOLD, fill=(*color, 255))

    return image


def make_frame(base: Image.Image, frame_number: int) -> Image.Image:
    elapsed = frame_number / FPS
    image = base.copy()
    draw = ImageDraw.Draw(image, "RGBA")

    # Status pulse and moving accent shimmer.
    pulse = 0.65 + 0.35 * (0.5 + 0.5 * math.sin(elapsed * math.tau / 2.0))
    glow_dot(image, (132, 65), (85, 230, 165), 4, pulse)
    shimmer_x = 66 + int((elapsed / SECONDS) * 529)
    draw.rounded_rectangle((max(66, shimmer_x - 48), 190, min(595, shimmer_x + 48), 194), radius=2, fill=(102, 167, 255, 210))

    # Type validation outcomes one at a time.
    outcomes = [
        ("PASSED", 0.45, (85, 230, 165)),
        ("1.0", 1.45, (85, 230, 204)),
        ("0.0", 2.25, (101, 167, 255)),
        ("0/5 solved", 3.05, (190, 157, 255)),
    ]
    for index, (value, start, color) in enumerate(outcomes):
        shown = reveal(value, elapsed, start)
        y = 88 + index * 36
        if shown:
            draw.text((1051, y), shown, font=FONT_MONO_BOLD, anchor="ra", fill=(*color, 255))
            if len(shown) < len(value) and int(elapsed * 5) % 2 == 0:
                end = draw.textbbox((1051, y), shown, font=FONT_MONO_BOLD, anchor="ra")
                draw.rectangle((end[2] + 3, y + 2, end[2] + 9, y + 18), fill=(*color, 230))
        else:
            draw.text((1051, y), "···", font=FONT_MONO_BOLD, anchor="ra", fill=(72, 94, 116, 170))

    # Packets travel through both replica lanes and then into the verifier.
    lane_phase = (elapsed * 0.42) % 1.0
    top = quadratic((730, 248), (790, 234), (853, 248), lane_phase)
    bottom = quadratic((730, 277), (792, 279), (853, 248), (lane_phase + 0.46) % 1.0)
    outbound = quadratic((873, 248), (932, 240), (994, 248), (lane_phase + 0.18) % 1.0)
    glow_dot(image, top, (85, 230, 204), 3, 0.95)
    glow_dot(image, bottom, (101, 167, 255), 3, 0.95)
    glow_dot(image, outbound, (190, 157, 255), 3, 0.95)

    # Accurate final state stays visible for the last third of the loop.
    if elapsed >= 4.8:
        fade = min(1.0, (elapsed - 4.8) / 0.45)
        draw.rounded_rectangle((871, 277, 1118, 297), radius=10, fill=(29, 24, 54, round(220 * fade)), outline=(151, 123, 224, round(180 * fade)))
        draw.text((994, 279), "TB5 CANDIDATE · REVIEW OPEN", font=FONT_MONO_SMALL, anchor="ma", fill=(203, 186, 255, round(255 * fade)))

    return image.convert("RGB")


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    base = draw_static()
    raw_frames = [make_frame(base, index) for index in range(FRAME_COUNT)]
    palette = raw_frames[-8].quantize(colors=64, method=Image.Quantize.MEDIANCUT)
    frames = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in raw_frames]
    frames[0].save(
        OUTPUT,
        save_all=True,
        append_images=frames[1:],
        duration=round(1000 / FPS),
        loop=0,
        optimize=True,
        disposal=1,
    )
    print(f"wrote {OUTPUT} ({OUTPUT.stat().st_size / 1024:.1f} KiB, {FRAME_COUNT} frames)")


if __name__ == "__main__":
    main()

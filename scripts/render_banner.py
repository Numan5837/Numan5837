from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "profile-header.gif"
WIDTH, HEIGHT = 1200, 320
FPS = 16
SECONDS = 16
FRAME_COUNT = FPS * SECONDS

BACKGROUND_LEFT = (5, 16, 27)
BACKGROUND_RIGHT = (10, 32, 49)
CARD = (7, 25, 39)
BORDER = (40, 70, 93)
TEAL = (105, 230, 207)
BLUE = (120, 167, 255)
TEXT = (244, 247, 251)
MUTED = (167, 182, 199)
SUCCESS = (93, 224, 170)

MESSAGES = [
    "I build hard agent benchmarks.",
    "I engineer exact verifiers.",
    "I reproduce failures in containers.",
    "I turn model failures into evidence.",
]
TYPE_RATE = 24.0
HOLD_DURATION = 1.55
ERASE_RATE = 40.0
GAP_DURATION = (
    SECONDS
    - sum(len(message) / TYPE_RATE + HOLD_DURATION + len(message) / ERASE_RATE for message in MESSAGES)
) / len(MESSAGES)


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        Path("C:/Windows/Fonts") / name,
        Path("/usr/share/fonts/truetype/dejavu") / name,
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


FONT_NAME = font("segoeuib.ttf", 64)
FONT_EYEBROW = font("seguisb.ttf", 20)
FONT_SUBTITLE = font("segoeui.ttf", 24)
FONT_TYPEWRITER = font("consolab.ttf", 26)
FONT_CARD_LABEL = font("consolab.ttf", 19)
FONT_CARD_TITLE = font("seguisb.ttf", 26)
FONT_METRIC = font("consola.ttf", 19)
FONT_METRIC_BOLD = font("consolab.ttf", 21)
FONT_STATUS = font("consolab.ttf", 18)


def mix(
    first: tuple[int, int, int],
    second: tuple[int, int, int],
    amount: float,
) -> tuple[int, int, int]:
    return tuple(round(left + (right - left) * amount) for left, right in zip(first, second))


def make_background() -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT))
    pixels = image.load()
    for x in range(WIDTH):
        horizontal = x / (WIDTH - 1)
        base = mix(BACKGROUND_LEFT, BACKGROUND_RIGHT, horizontal)
        for y in range(HEIGHT):
            vertical = 1.0 - 0.055 * (y / HEIGHT)
            pixels[x, y] = tuple(round(channel * vertical) for channel in base)

    draw = ImageDraw.Draw(image, "RGBA")
    draw.ellipse((870, -210, 1330, 250), fill=(66, 126, 190, 13))
    draw.ellipse((-190, 230, 300, 720), fill=(63, 205, 180, 8))
    draw.rounded_rectangle(
        (1, 1, WIDTH - 2, HEIGHT - 2),
        radius=22,
        outline=(*BORDER, 230),
        width=2,
    )
    return image


def draw_static() -> Image.Image:
    image = make_background().convert("RGBA")
    draw = ImageDraw.Draw(image, "RGBA")

    # Compact terminal mark and quiet eyebrow.
    draw.rounded_rectangle(
        (64, 42, 108, 86),
        radius=12,
        fill=(9, 30, 45, 255),
        outline=(*TEAL, 235),
        width=2,
    )
    draw.line((77, 57, 85, 64, 77, 72), fill=(*TEAL, 255), width=3, joint="curve")
    draw.line((89, 73, 98, 73), fill=(*TEAL, 255), width=3)
    draw.text((124, 52), "AI EVALUATION · SYSTEMS", font=FONT_EYEBROW, fill=(*MUTED, 255))

    draw.text((64, 91), "Numan S.", font=FONT_NAME, fill=(*TEXT, 255))
    draw.text(
        (64, 176),
        "Agent benchmarks · Exact verifiers · Cloud reliability",
        font=FONT_SUBTITLE,
        fill=(*MUTED, 255),
    )

    # The typewriter has enough internal padding to remain readable after GitHub scales it down.
    draw.rounded_rectangle(
        (64, 219, 724, 281),
        radius=12,
        fill=(5, 20, 32, 247),
        outline=(42, 82, 105, 255),
        width=2,
    )
    draw.text((84, 232), ">", font=FONT_TYPEWRITER, fill=(*TEAL, 255))

    # Static evidence card: the data stays legible while the typewriter moves.
    draw.rounded_rectangle(
        (764, 40, 1136, 280),
        radius=20,
        fill=(*CARD, 247),
        outline=(38, 71, 94, 255),
        width=2,
    )
    draw.text((808, 61), "CURRENT WORK", font=FONT_CARD_LABEL, fill=(*MUTED, 255))
    draw.text((790, 91), "Replica reconciliation", font=FONT_CARD_TITLE, fill=(*TEXT, 255))
    draw.line((790, 132, 1110, 132), fill=(39, 69, 90, 255), width=2)

    metrics = [
        (148, "Docker validation", "PASS", SUCCESS),
        (181, "Reference oracle", "1.0", TEAL),
        (214, "GPT-5.6 Sol", "0 / 5", BLUE),
    ]
    for y, label, value, color in metrics:
        draw.text((790, y), label, font=FONT_METRIC, fill=(*MUTED, 255))
        draw.text((1110, y), value, font=FONT_METRIC_BOLD, anchor="ra", fill=(*color, 255))

    draw.rounded_rectangle(
        (790, 242, 1110, 270),
        radius=14,
        fill=(10, 38, 50, 255),
        outline=(50, 111, 113, 255),
        width=1,
    )
    draw.text(
        (950, 256),
        "TB5 · OPEN FOR REVIEW",
        font=FONT_STATUS,
        anchor="mm",
        fill=(*TEAL, 255),
    )

    return image


def typewriter_state(elapsed: float) -> tuple[str, str, float]:
    """Return visible text, phase, and time within that phase."""
    cursor = elapsed % SECONDS
    for message in MESSAGES:
        type_duration = len(message) / TYPE_RATE
        erase_duration = len(message) / ERASE_RATE

        if cursor < type_duration:
            count = min(len(message), int(cursor * TYPE_RATE))
            return message[:count], "typing", cursor
        cursor -= type_duration

        if cursor < HOLD_DURATION:
            return message, "holding", cursor
        cursor -= HOLD_DURATION

        if cursor < erase_duration:
            count = max(0, len(message) - int(cursor * ERASE_RATE))
            return message[:count], "erasing", cursor
        cursor -= erase_duration

        if cursor < GAP_DURATION:
            return "", "gap", cursor
        cursor -= GAP_DURATION

    return "", "gap", 0.0


def make_frame(base: Image.Image, frame_number: int) -> Image.Image:
    elapsed = frame_number / FPS
    image = base.copy()
    draw = ImageDraw.Draw(image, "RGBA")

    # One quiet status pulse is the only secondary motion in the header.
    pulse = 0.50 + 0.28 * (0.5 + 0.5 * math.sin(elapsed * math.tau / 3.0))
    dot_color = mix((31, 92, 82), TEAL, pulse)
    draw.ellipse((784, 66, 794, 76), fill=(*dot_color, 255))

    typed, phase, phase_time = typewriter_state(elapsed)
    text_x, text_y = 116, 232
    draw.text((text_x, text_y), typed, font=FONT_TYPEWRITER, fill=(*TEXT, 255))

    if phase != "gap":
        typed_box = draw.textbbox((text_x, text_y), typed, font=FONT_TYPEWRITER)
        cursor_x = max(text_x, typed_box[2] + 4)
        show_cursor = phase != "holding" or int(phase_time / 0.5) % 2 == 0
        if show_cursor:
            draw.rectangle((cursor_x, 235, cursor_x + 3, 261), fill=(*TEAL, 255))

    return image.convert("RGB")


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    base = draw_static()
    raw_frames = [make_frame(base, index) for index in range(FRAME_COUNT)]
    palette = base.convert("RGB").quantize(colors=56, method=Image.Quantize.MEDIANCUT)
    frames = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in raw_frames]
    durations = [70 if index % 4 == 3 else 60 for index in range(FRAME_COUNT)]
    frames[0].save(
        OUTPUT,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        optimize=True,
        disposal=1,
    )
    print(f"wrote {OUTPUT} ({OUTPUT.stat().st_size / 1024:.1f} KiB, {FRAME_COUNT} frames)")


if __name__ == "__main__":
    main()

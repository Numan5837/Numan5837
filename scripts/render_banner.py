from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "profile-hero.gif"
WIDTH, HEIGHT = 1200, 320
FPS = 16
SECONDS = 16
FRAME_COUNT = FPS * SECONDS

BACKGROUND_LEFT = (5, 15, 26)
BACKGROUND_RIGHT = (9, 32, 48)
BORDER = (38, 72, 94)
TEAL = (105, 230, 207)
BLUE = (128, 181, 255)
TEXT = (242, 247, 250)
MUTED = (164, 182, 198)

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


FONT_NAME = font("segoeuib.ttf", 65)
FONT_LABEL = font("consolab.ttf", 17)
FONT_SUBTITLE = font("segoeui.ttf", 23)
FONT_TYPEWRITER = font("consolab.ttf", 26)


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
            vertical = 1.0 - 0.05 * (y / HEIGHT)
            pixels[x, y] = tuple(round(channel * vertical) for channel in base)
    return image.convert("RGBA")


def draw_static() -> Image.Image:
    image = make_background()
    draw = ImageDraw.Draw(image, "RGBA")

    # A quiet identity stack mirrors the simple hierarchy of the reference header.
    draw.text(
        (WIDTH // 2, 39),
        "NUMAN5837  /  README.md",
        font=FONT_LABEL,
        anchor="ma",
        fill=(*TEAL, 235),
    )
    draw.line((430, 48, 500, 48), fill=(*BORDER, 180), width=1)
    draw.line((700, 48, 770, 48), fill=(*BORDER, 180), width=1)

    draw.text(
        (WIDTH // 2, 71),
        "Numan S.",
        font=FONT_NAME,
        anchor="ma",
        fill=(*TEXT, 255),
    )
    draw.text(
        (WIDTH // 2, 151),
        "AI evaluation · verifier engineering · reproducible infrastructure",
        font=FONT_SUBTITLE,
        anchor="ma",
        fill=(*MUTED, 255),
    )

    draw.rounded_rectangle(
        (1, 1, WIDTH - 2, HEIGHT - 2),
        radius=22,
        outline=(*BORDER, 220),
        width=2,
    )
    return image


def draw_wave(image: Image.Image, elapsed: float) -> None:
    """Draw two slow background waves with enough contrast to survive GIF quantization."""
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")

    phase = elapsed * math.tau / 16.0
    first = []
    second = []
    for x in range(-20, WIDTH + 21, 12):
        first_y = 257 + 10 * math.sin((x / 255.0) + phase)
        second_y = 281 + 8 * math.sin((x / 295.0) + phase + 1.6)
        first.append((x, round(first_y)))
        second.append((x, round(second_y)))

    first.extend(((WIDTH + 20, HEIGHT + 20), (-20, HEIGHT + 20)))
    second.extend(((WIDTH + 20, HEIGHT + 20), (-20, HEIGHT + 20)))
    draw.polygon(first, fill=(36, 117, 130, 20))
    draw.polygon(second, fill=(65, 119, 178, 16))

    glow_alpha = round(8 + 4 * (0.5 + 0.5 * math.sin(phase)))
    draw.ellipse((780, -250, 1360, 285), fill=(68, 142, 193, glow_alpha))
    image.alpha_composite(overlay)


def typewriter_state(elapsed: float) -> tuple[str, str, float, str]:
    """Return visible text, phase, phase time, and its complete message."""
    cursor = elapsed % SECONDS
    for message in MESSAGES:
        type_duration = len(message) / TYPE_RATE
        erase_duration = len(message) / ERASE_RATE

        if cursor < type_duration:
            count = min(len(message), int(cursor * TYPE_RATE))
            return message[:count], "typing", cursor, message
        cursor -= type_duration

        if cursor < HOLD_DURATION:
            return message, "holding", cursor, message
        cursor -= HOLD_DURATION

        if cursor < erase_duration:
            count = max(0, len(message) - int(cursor * ERASE_RATE))
            return message[:count], "erasing", cursor, message
        cursor -= erase_duration

        if cursor < GAP_DURATION:
            return "", "gap", cursor, message
        cursor -= GAP_DURATION

    return "", "gap", 0.0, MESSAGES[0]


def make_frame(base: Image.Image, frame_number: int) -> Image.Image:
    elapsed = frame_number / FPS
    image = base.copy()
    draw_wave(image, elapsed)
    draw = ImageDraw.Draw(image, "RGBA")

    typed, phase, phase_time, complete_message = typewriter_state(elapsed)
    full_box = draw.textbbox((0, 0), complete_message, font=FONT_TYPEWRITER)
    full_width = full_box[2] - full_box[0]
    text_x = round((WIDTH - full_width) / 2)
    text_y = 215

    prompt_x = text_x - 30
    draw.text((prompt_x, text_y), ">", font=FONT_TYPEWRITER, fill=(*BLUE, 240))
    draw.text((text_x, text_y), typed, font=FONT_TYPEWRITER, fill=(*TEXT, 255))

    if phase != "gap":
        typed_box = draw.textbbox((text_x, text_y), typed, font=FONT_TYPEWRITER)
        cursor_x = max(text_x, typed_box[2] + 4)
        show_cursor = phase != "holding" or int(phase_time / 0.5) % 2 == 0
        if show_cursor:
            draw.rounded_rectangle(
                (cursor_x, 219, cursor_x + 3, 245),
                radius=1,
                fill=(*TEAL, 255),
            )

    return image.convert("RGB")


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    base = draw_static()
    raw_frames = [make_frame(base, index) for index in range(FRAME_COUNT)]
    palette = base.convert("RGB").quantize(colors=64, method=Image.Quantize.MEDIANCUT)
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

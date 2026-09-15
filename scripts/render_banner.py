from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "profile-graph-hero.gif"
WIDTH, HEIGHT = 1200, 420
FPS = 16
SECONDS = 16
FRAME_COUNT = FPS * SECONDS

BACKGROUND_LEFT = (4, 14, 25)
BACKGROUND_RIGHT = (7, 31, 47)
BORDER = (42, 86, 108)
TEAL = (103, 229, 207)
BLUE = (126, 183, 255)
TEXT = (242, 248, 250)
MUTED = (166, 187, 202)

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


FONT_NAME = font("segoeuib.ttf", 72)
FONT_LABEL = font("consolab.ttf", 17)
FONT_SUBTITLE = font("segoeui.ttf", 24)
FONT_TYPEWRITER = font("consolab.ttf", 29)


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
            vertical = 1.0 - 0.08 * (y / HEIGHT)
            pixels[x, y] = tuple(round(channel * vertical) for channel in base)

    glow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow, "RGBA")
    glow_draw.ellipse((260, -180, 940, 520), fill=(26, 108, 128, 32))
    glow = glow.filter(ImageFilter.GaussianBlur(72))
    return Image.alpha_composite(image.convert("RGBA"), glow)


def draw_static() -> Image.Image:
    image = make_background()
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")

    # A soft inner panel creates a clean reading plane while leaving the plot visible.
    draw.rounded_rectangle(
        (212, 30, 988, 370),
        radius=36,
        fill=(3, 16, 27, 78),
        outline=(88, 183, 195, 18),
        width=1,
    )
    draw.rounded_rectangle(
        (1, 1, WIDTH - 2, HEIGHT - 2),
        radius=24,
        outline=(*BORDER, 222),
        width=2,
    )
    image.alpha_composite(overlay)
    return image


def graph_y(x: float, elapsed: float, lane: int) -> float:
    """Return a looping, deterministic trace position for one graph lane."""
    phase = elapsed * math.tau / SECONDS
    if lane == 0:
        return (
            112
            + 17 * math.sin(x / 118 + phase)
            + 6 * math.sin(x / 43 - 2 * phase + 0.4)
            + 3 * math.sin(x / 21 + 3 * phase)
        )
    if lane == 1:
        return (
            235
            + 12 * math.sin(x / 145 + phase + 1.4)
            + 5 * math.sin(x / 54 - 2 * phase)
            + 3 * math.sin(x / 30 + 3 * phase + 0.3)
        )
    return (
        344
        + 15 * math.sin(x / 132 - phase + 1.1)
        + 6 * math.sin(x / 49 + 2 * phase)
        + 3 * math.sin(x / 25 - 3 * phase + 0.8)
    )


def draw_graph(image: Image.Image, elapsed: float) -> None:
    """Animate a quiet grid, three traces, a scan, and traveling highlights."""
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")
    progress = elapsed / SECONDS

    # The grid drifts by one cell per loop, making the wrap visually seamless.
    grid_size = 48
    grid_offset = progress * grid_size
    first_grid_x = -grid_size + grid_offset
    column = -1
    x = first_grid_x
    while x <= WIDTH + grid_size:
        major = column % 4 == 0
        draw.line(
            (round(x), 2, round(x), HEIGHT - 3),
            fill=(74, 152, 171, 23 if major else 12),
            width=1,
        )
        x += grid_size
        column += 1

    for row, y in enumerate(range(34, HEIGHT, grid_size)):
        draw.line(
            (2, y, WIDTH - 3, y),
            fill=(74, 152, 171, 21 if row % 4 == 0 else 11),
            width=1,
        )

    # One low-contrast scan adds depth without becoming a foreground element.
    scan_x = -90 + progress * (WIDTH + 180)
    for distance in range(-54, 55, 9):
        alpha = round(14 * (1 - abs(distance) / 63))
        draw.line(
            (round(scan_x + distance), 4, round(scan_x + distance), HEIGHT - 5),
            fill=(108, 226, 210, max(0, alpha)),
            width=2,
        )

    xs = list(range(-12, WIDTH + 13, 8))
    trace_colors = [(*TEAL, 45), (*BLUE, 29), (*BLUE, 41)]
    travel_offsets = ((0.08, 0.57), (0.24, 0.73), (0.41, 0.89))
    for lane in range(3):
        points = [(x, round(graph_y(x, elapsed, lane))) for x in xs]
        draw.line(points, fill=trace_colors[lane], width=2, joint="curve")

        # Six staggered highlights travel across the traces.
        for point_index, offset in enumerate(travel_offsets[lane]):
            point_progress = (progress + offset) % 1.0
            point_x = 28 + point_progress * (WIDTH - 56)
            point_y = graph_y(point_x, elapsed, lane)
            color = TEAL if lane == 0 else BLUE
            radius = 4 if point_index == 0 else 3
            draw.ellipse(
                (
                    point_x - radius * 3,
                    point_y - radius * 3,
                    point_x + radius * 3,
                    point_y + radius * 3,
                ),
                fill=(*color, 12),
            )
            draw.ellipse(
                (
                    point_x - radius,
                    point_y - radius,
                    point_x + radius,
                    point_y + radius,
                ),
                fill=(*color, 142),
            )

    image.alpha_composite(overlay)


def draw_identity(image: Image.Image) -> None:
    """Draw the stable foreground copy after all moving graph layers."""
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")

    draw.text(
        (WIDTH // 2, 57),
        "NUMAN5837  /  README.md",
        font=FONT_LABEL,
        anchor="ma",
        fill=(*TEAL, 238),
    )
    draw.line((410, 66, 486, 66), fill=(*BORDER, 150), width=1)
    draw.line((714, 66, 790, 66), fill=(*BORDER, 150), width=1)
    draw.text(
        (WIDTH // 2, 94),
        "Numan S.",
        font=FONT_NAME,
        anchor="ma",
        fill=(*TEXT, 255),
    )
    draw.text(
        (WIDTH // 2, 184),
        "AI evaluation · verifier engineering · reproducible infrastructure",
        font=FONT_SUBTITLE,
        anchor="ma",
        fill=(*MUTED, 255),
    )
    draw.line((390, 242, 810, 242), fill=(*BORDER, 100), width=1)
    draw.text(
        (WIDTH // 2, 362),
        "BENCHMARKS    ·    VERIFIERS    ·    REPRODUCIBLE SYSTEMS",
        font=FONT_LABEL,
        anchor="ma",
        fill=(*MUTED, 112),
    )
    draw.rounded_rectangle(
        (1, 1, WIDTH - 2, HEIGHT - 2),
        radius=24,
        outline=(*BORDER, 222),
        width=2,
    )
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
    draw_graph(image, elapsed)

    # A central vignette keeps the animated plot behind the content.
    veil = Image.new("RGBA", image.size, (0, 0, 0, 0))
    veil_draw = ImageDraw.Draw(veil, "RGBA")
    veil_draw.rounded_rectangle((248, 42, 952, 360), radius=30, fill=(3, 13, 23, 34))
    image.alpha_composite(veil)
    draw_identity(image)

    draw = ImageDraw.Draw(image, "RGBA")
    typed, phase, phase_time, _ = typewriter_state(elapsed)

    # All phrases share one fixed origin inside a centered 810-pixel row.
    row_left = 195
    text_x = row_left + 48
    text_y = 277
    draw.text((row_left + 10, text_y), ">", font=FONT_TYPEWRITER, fill=(*BLUE, 242))
    draw.text((text_x, text_y), typed, font=FONT_TYPEWRITER, fill=(*TEXT, 255))

    if phase != "gap":
        typed_box = draw.textbbox((text_x, text_y), typed, font=FONT_TYPEWRITER)
        cursor_x = max(text_x, typed_box[2] + 5)
        show_cursor = phase != "holding" or int(phase_time / 0.5) % 2 == 0
        if show_cursor:
            draw.rounded_rectangle(
                (cursor_x, 281, cursor_x + 3, 311),
                radius=1,
                fill=(*TEAL, 255),
            )

    return image.convert("RGB")


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    base = draw_static()

    # Quantize each frame as it is made so the taller canvas stays memory efficient.
    # Build the shared palette from a complete foreground frame so light text,
    # trace highlights, and the dark gradient retain their intended contrast.
    palette_sample = make_frame(base, round(13.68 * FPS))
    palette = palette_sample.quantize(colors=96, method=Image.Quantize.MEDIANCUT)
    frames = []
    for index in range(FRAME_COUNT):
        frame = make_frame(base, index)
        frames.append(frame.quantize(palette=palette, dither=Image.Dither.NONE))

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

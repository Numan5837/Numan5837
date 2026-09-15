from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = {
    "dark": ROOT / "assets" / "profile-typewriter-dark.gif",
    "light": ROOT / "assets" / "profile-typewriter-light.gif",
}

WIDTH, HEIGHT = 1200, 420
FPS = 16
SECONDS = 16
FRAME_COUNT = FPS * SECONDS

THEMES = {
    "dark": {
        "background": (13, 17, 23),
        "teal": (85, 230, 204),
        "blue": (126, 183, 255),
        "text": (240, 246, 252),
        "muted": (139, 148, 158),
    },
    "light": {
        "background": (255, 255, 255),
        "teal": (5, 112, 101),
        "blue": (9, 105, 218),
        "text": (31, 35, 40),
        "muted": (87, 96, 106),
    },
}

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


FONT_NAME = font("segoeuib.ttf", 78)
FONT_LABEL = font("consolab.ttf", 18)
FONT_SUBTITLE = font("segoeui.ttf", 25)
FONT_TYPEWRITER = font("consolab.ttf", 30)


def make_background(colors: dict[str, tuple[int, int, int]]) -> Image.Image:
    """Use GitHub's canvas color so the animation has no visible card."""
    return Image.new("RGBA", (WIDTH, HEIGHT), (*colors["background"], 255))


def draw_identity(
    image: Image.Image,
    colors: dict[str, tuple[int, int, int]],
) -> None:
    """Draw the centered, stable identity hierarchy."""
    draw = ImageDraw.Draw(image, "RGBA")
    center = WIDTH // 2

    draw.text(
        (center, 58),
        "NUMAN5837  /  README.md",
        font=FONT_LABEL,
        anchor="ma",
        fill=(*colors["teal"], 236),
    )
    draw.text(
        (center, 105),
        "Numan S.",
        font=FONT_NAME,
        anchor="ma",
        fill=(*colors["text"], 255),
    )
    draw.text(
        (center, 207),
        "AI evaluation  ·  verifier engineering  ·  reproducible infrastructure",
        font=FONT_SUBTITLE,
        anchor="ma",
        fill=(*colors["muted"], 255),
    )


def typewriter_state(elapsed: float) -> tuple[str, str, float]:
    """Return the visible copy, animation phase, and time within that phase."""
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


def make_frame(
    base: Image.Image,
    frame_number: int,
    colors: dict[str, tuple[int, int, int]],
) -> Image.Image:
    image = base.copy()
    draw = ImageDraw.Draw(image, "RGBA")
    typed, phase, phase_time = typewriter_state(frame_number / FPS)

    # Every sentence starts from this exact position. The longest sentence is
    # centered within the hero, while shorter sentences keep the same origin.
    prompt_x = 274
    text_x = 318
    text_y = 298
    draw.text(
        (prompt_x, text_y),
        ">",
        font=FONT_TYPEWRITER,
        fill=(*colors["blue"], 242),
    )
    draw.text(
        (text_x, text_y),
        typed,
        font=FONT_TYPEWRITER,
        fill=(*colors["text"], 255),
    )

    if phase != "gap":
        typed_box = draw.textbbox((text_x, text_y), typed, font=FONT_TYPEWRITER)
        cursor_x = max(text_x, typed_box[2] + 6)
        show_cursor = phase != "holding" or int(phase_time / 0.5) % 2 == 0
        if show_cursor:
            draw.rounded_rectangle(
                (cursor_x, text_y + 4, cursor_x + 3, text_y + 35),
                radius=1,
                fill=(*colors["teal"], 255),
            )

    return image.convert("RGB")


def build_palette(
    colors: dict[str, tuple[int, int, int]],
    source: Image.Image,
) -> Image.Image:
    """Reserve palette index zero for the exact GitHub canvas color."""
    reduced = source.quantize(colors=63, method=Image.Quantize.MEDIANCUT)
    reduced_palette = reduced.getpalette() or []
    used_indexes = sorted(index for _count, index in (reduced.getcolors() or []))
    palette_colors = [colors["background"]]
    for index in used_indexes:
        offset = index * 3
        color = tuple(reduced_palette[offset : offset + 3])
        if len(color) == 3 and color not in palette_colors:
            palette_colors.append(color)

    palette_values = [channel for color in palette_colors[:64] for channel in color]
    palette_values.extend([0] * (768 - len(palette_values)))
    palette = Image.new("P", (1, 1), 0)
    palette.putpalette(palette_values)
    return palette


def quantize_frame(
    colors: dict[str, tuple[int, int, int]],
    frame: Image.Image,
    palette: Image.Image,
) -> Image.Image:
    quantized = frame.quantize(palette=palette, dither=Image.Dither.NONE)
    background = Image.new("RGB", frame.size, colors["background"])
    difference = ImageChops.difference(frame, background)
    red, green, blue = difference.split()
    maximum_difference = ImageChops.lighter(ImageChops.lighter(red, green), blue)
    exact_background = maximum_difference.point(lambda value: 255 if value == 0 else 0)
    quantized.paste(0, mask=exact_background)
    return quantized


def main() -> None:
    durations = [70 if index % 4 == 3 else 60 for index in range(FRAME_COUNT)]
    for theme_name, colors in THEMES.items():
        output = OUTPUTS[theme_name]
        output.parent.mkdir(parents=True, exist_ok=True)
        base = make_background(colors)
        draw_identity(base, colors)

        # Use one palette per theme so only the typewriter appears to move.
        palette_sample = make_frame(base, round(13.68 * FPS), colors)
        palette = build_palette(colors, palette_sample.convert("RGB"))
        frames = [
            quantize_frame(
                colors,
                make_frame(base, index, colors).convert("RGB"),
                palette,
            )
            for index in range(FRAME_COUNT)
        ]

        frames[0].save(
            output,
            save_all=True,
            append_images=frames[1:],
            duration=durations,
            loop=0,
            optimize=True,
            disposal=1,
        )
        print(
            f"wrote {output} "
            f"({output.stat().st_size / 1024:.1f} KiB, {FRAME_COUNT} source frames)"
        )


if __name__ == "__main__":
    main()

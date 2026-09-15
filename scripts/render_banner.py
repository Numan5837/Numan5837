from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "profile-typewriter-hero.gif"

WIDTH, HEIGHT = 1200, 420
FPS = 16
SECONDS = 16
FRAME_COUNT = FPS * SECONDS

BACKGROUND_LEFT = (4, 13, 23)
BACKGROUND_RIGHT = (7, 29, 43)
TEAL = (103, 229, 207)
BLUE = (140, 196, 236)
TEXT = (242, 248, 250)
MUTED = (169, 191, 204)

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


def mix(
    first: tuple[int, int, int],
    second: tuple[int, int, int],
    amount: float,
) -> tuple[int, int, int]:
    return tuple(round(left + (right - left) * amount) for left, right in zip(first, second))


def make_background() -> Image.Image:
    """Create the complete static hero background."""
    image = Image.new("RGB", (WIDTH, HEIGHT))
    pixels = image.load()
    for x in range(WIDTH):
        horizontal = x / (WIDTH - 1)
        base = mix(BACKGROUND_LEFT, BACKGROUND_RIGHT, horizontal)
        for y in range(HEIGHT):
            center_lift = 1.0 + 0.035 * (1.0 - abs((y / HEIGHT) - 0.43) / 0.57)
            lower_falloff = 1.0 - 0.055 * (y / HEIGHT)
            pixels[x, y] = tuple(
                min(255, round(channel * center_lift * lower_falloff)) for channel in base
            )

    # A static, blurred color field gives the flat gradient some depth without
    # introducing a second animation or a visible inner panel.
    glow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow, "RGBA")
    glow_draw.ellipse((300, -260, 900, 500), fill=(28, 118, 126, 27))
    glow = glow.filter(ImageFilter.GaussianBlur(100))
    image = Image.alpha_composite(image.convert("RGBA"), glow)

    return image


def draw_identity(image: Image.Image) -> None:
    """Draw the centered, stable identity hierarchy."""
    draw = ImageDraw.Draw(image, "RGBA")
    center = WIDTH // 2

    draw.text(
        (center, 58),
        "NUMAN5837  /  README.md",
        font=FONT_LABEL,
        anchor="ma",
        fill=(*TEAL, 236),
    )
    draw.text(
        (center, 105),
        "Numan S.",
        font=FONT_NAME,
        anchor="ma",
        fill=(*TEXT, 255),
    )
    draw.text(
        (center, 207),
        "AI evaluation  ·  verifier engineering  ·  reproducible infrastructure",
        font=FONT_SUBTITLE,
        anchor="ma",
        fill=(*MUTED, 255),
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


def make_frame(base: Image.Image, frame_number: int) -> Image.Image:
    image = base.copy()
    draw = ImageDraw.Draw(image, "RGBA")
    typed, phase, phase_time = typewriter_state(frame_number / FPS)

    # Every sentence starts from this exact position. The longest sentence is
    # centered within the hero, while shorter sentences keep the same origin.
    prompt_x = 274
    text_x = 318
    text_y = 298
    draw.text((prompt_x, text_y), ">", font=FONT_TYPEWRITER, fill=(*BLUE, 242))
    draw.text((text_x, text_y), typed, font=FONT_TYPEWRITER, fill=(*TEXT, 255))

    if phase != "gap":
        typed_box = draw.textbbox((text_x, text_y), typed, font=FONT_TYPEWRITER)
        cursor_x = max(text_x, typed_box[2] + 6)
        show_cursor = phase != "holding" or int(phase_time / 0.5) % 2 == 0
        if show_cursor:
            draw.rounded_rectangle(
                (cursor_x, text_y + 4, cursor_x + 3, text_y + 35),
                radius=1,
                fill=(*TEAL, 255),
            )

    return image.convert("RGB")


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    base = make_background()
    draw_identity(base)

    # Use one shared palette so the static background does not shimmer between
    # frames and only the typewriter appears to move.
    palette_sample = make_frame(base, round(13.68 * FPS))
    palette = palette_sample.quantize(colors=80, method=Image.Quantize.MEDIANCUT)
    frames = [
        make_frame(base, index).quantize(palette=palette, dither=Image.Dither.NONE)
        for index in range(FRAME_COUNT)
    ]

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
    print(f"wrote {OUTPUT} ({OUTPUT.stat().st_size / 1024:.1f} KiB, {FRAME_COUNT} source frames)")


if __name__ == "__main__":
    main()

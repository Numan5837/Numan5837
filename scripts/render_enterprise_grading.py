from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "assets"
WIDTH, HEIGHT = 1200, 360
FPS, SECONDS = 12, 10
FRAME_COUNT = FPS * SECONDS


def load_font(name: str, size: int) -> ImageFont.FreeTypeFont:
    for path in (
        Path("C:/Windows/Fonts") / name,
        Path("/usr/share/fonts/truetype/dejavu") / name,
    ):
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


TITLE = load_font("segoeuib.ttf", 43)
SUBTITLE = load_font("segoeui.ttf", 20)
MONO_BOLD = load_font("consolab.ttf", 17)
MONO = load_font("consola.ttf", 18)
MONO_SMALL_BOLD = load_font("consolab.ttf", 14)
STAGE_LABEL = load_font("consolab.ttf", 17)


@dataclass(frozen=True)
class Theme:
    name: str
    background: tuple[int, int, int]
    text: tuple[int, int, int]
    muted: tuple[int, int, int]
    rail: tuple[int, int, int]
    teal: tuple[int, int, int]
    blue: tuple[int, int, int]
    green: tuple[int, int, int]
    idle_fill: tuple[int, int, int]
    complete_fill: tuple[int, int, int]


THEMES = (
    Theme(
        name="dark",
        background=(13, 17, 23),  # GitHub dark canvas: #0d1117
        text=(240, 246, 252),
        muted=(139, 148, 158),
        rail=(48, 54, 61),
        teal=(45, 212, 191),
        blue=(88, 166, 255),
        green=(63, 185, 80),
        idle_fill=(13, 17, 23),
        complete_fill=(15, 45, 36),
    ),
    Theme(
        name="light",
        background=(255, 255, 255),  # GitHub light canvas: #ffffff
        text=(31, 35, 40),
        muted=(89, 99, 110),
        rail=(208, 215, 222),
        teal=(5, 125, 117),
        blue=(9, 105, 218),
        green=(26, 127, 55),
        idle_fill=(255, 255, 255),
        complete_fill=(218, 251, 225),
    ),
)


CONTENT_LEFT = 58
NODE_X = [112, 356, 600, 844, 1088]
NODE_Y = 219
NODE_RADIUS = 18
STAGES = ["TASK", "AUDIT", "CALIBRATE", "GRADE", "EVIDENCE"]
CAPTIONS = [
    "Load rubric and artifact",
    "Inspect verifier behavior",
    "Run oracle · no-op · mutations",
    "Execute repeatable Pass@k trials",
    "Package scores and failure traces",
]
ARRIVALS = [0.40, 1.75, 3.10, 4.45, 5.80]
TRAVEL_STARTS = [1.20, 2.55, 3.90, 5.25]
COMPLETE_AT = 6.70


def clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def ease(value: float) -> float:
    value = clamp(value)
    return value * value * (3.0 - 2.0 * value)


def alpha_color(color: tuple[int, int, int], opacity: float) -> tuple[int, int, int, int]:
    return (*color, round(255 * clamp(opacity)))


def draw_centered_text(
    draw: ImageDraw.ImageDraw,
    center_x: int,
    y: int,
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int, int],
) -> None:
    bounds = draw.textbbox((0, 0), text, font=font)
    text_width = bounds[2] - bounds[0]
    draw.text((center_x - text_width / 2, y), text, font=font, fill=fill)


def draw_infinity_mark(
    draw: ImageDraw.ImageDraw,
    theme: Theme,
    opacity: float = 1.0,
) -> None:
    points = []
    for point_index in range(121):
        angle = point_index / 120 * math.tau
        points.append(
            (
                1083 + 48 * math.cos(angle),
                71 + 18 * math.sin(2 * angle),
            )
        )
    draw.line(
        points,
        fill=alpha_color(theme.muted, 0.72 * opacity),
        width=2,
        joint="curve",
    )


def draw_static(theme: Theme) -> Image.Image:
    # A flat theme-matched canvas makes the animation visually merge into the
    # README, just like GitHub's contribution-snake assets.
    image = Image.new("RGBA", (WIDTH, HEIGHT), (*theme.background, 255))
    draw = ImageDraw.Draw(image, "RGBA")

    draw.text(
        (CONTENT_LEFT, 27),
        "INFINITY MEGATRON  ·  PRIVATE R&D",
        font=MONO_SMALL_BOLD,
        fill=alpha_color(theme.teal, 1.0),
    )
    draw.text(
        (CONTENT_LEFT, 54),
        "Enterprise grading",
        font=TITLE,
        fill=alpha_color(theme.text, 1.0),
    )
    draw.text(
        (CONTENT_LEFT, 109),
        "Auditable evaluation from task intake to evidence",
        font=SUBTITLE,
        fill=alpha_color(theme.muted, 1.0),
    )
    draw_infinity_mark(draw, theme)

    # The rail belongs to the workflow itself; there is no surrounding panel,
    # strip, frame, grid, or decorative divider.
    draw.line((NODE_X[0], NODE_Y, NODE_X[-1], NODE_Y), fill=(*theme.rail, 255), width=3)
    for index, (center_x, label) in enumerate(zip(NODE_X, STAGES), start=1):
        draw.ellipse(
            (
                center_x - NODE_RADIUS,
                NODE_Y - NODE_RADIUS,
                center_x + NODE_RADIUS,
                NODE_Y + NODE_RADIUS,
            ),
            fill=(*theme.idle_fill, 255),
            outline=(*theme.rail, 255),
            width=3,
        )
        draw_centered_text(
            draw,
            center_x,
            251,
            label,
            STAGE_LABEL,
            alpha_color(theme.muted, 1.0),
        )
        draw_centered_text(
            draw,
            center_x,
            181,
            f"0{index}",
            MONO_SMALL_BOLD,
            alpha_color(theme.muted, 0.78),
        )
    return image


def current_stage(elapsed: float) -> int:
    stage_index = 0
    for index, arrival in enumerate(ARRIVALS):
        if elapsed >= arrival:
            stage_index = index
    return stage_index


def packet_position(elapsed: float) -> float:
    if elapsed < TRAVEL_STARTS[0]:
        return float(NODE_X[0])
    for index, travel_start in enumerate(TRAVEL_STARTS):
        travel_end = ARRIVALS[index + 1]
        if elapsed < travel_end:
            progress = ease((elapsed - travel_start) / (travel_end - travel_start))
            return NODE_X[index] + (NODE_X[index + 1] - NODE_X[index]) * progress
        if index + 1 < len(TRAVEL_STARTS) and elapsed < TRAVEL_STARTS[index + 1]:
            return float(NODE_X[index + 1])
    return float(NODE_X[-1])


def detail_alpha(elapsed: float, stage_index: int) -> float:
    fade = ease((elapsed - ARRIVALS[stage_index]) / 0.18)
    if stage_index < len(STAGES) - 1:
        fade *= ease((ARRIVALS[stage_index + 1] - elapsed) / 0.18)
    else:
        fade *= ease((COMPLETE_AT - elapsed) / 0.18)
    return fade


def glow_dot(
    image: Image.Image,
    center_x: int,
    center_y: int,
    theme: Theme,
    opacity: float,
) -> None:
    glow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow, "RGBA")
    glow_draw.ellipse(
        (center_x - 11, center_y - 11, center_x + 11, center_y + 11),
        fill=alpha_color(theme.blue, 0.32 * opacity),
    )
    image.alpha_composite(glow.filter(ImageFilter.GaussianBlur(6)))
    draw = ImageDraw.Draw(image, "RGBA")
    draw.ellipse(
        (center_x - 4, center_y - 4, center_x + 4, center_y + 4),
        fill=alpha_color(theme.blue, 0.98 * opacity),
    )


def draw_current_detail(
    draw: ImageDraw.ImageDraw,
    theme: Theme,
    stage_index: int,
    opacity: float,
) -> None:
    step = f"STEP {stage_index + 1} / 5"
    caption = CAPTIONS[stage_index]
    step_bounds = draw.textbbox((0, 0), step, font=MONO_SMALL_BOLD)
    caption_bounds = draw.textbbox((0, 0), caption, font=MONO)
    gap = 18
    total_width = (step_bounds[2] - step_bounds[0]) + gap + (caption_bounds[2] - caption_bounds[0])
    start_x = (WIDTH - total_width) / 2
    draw.text(
        (start_x, 310),
        step,
        font=MONO_SMALL_BOLD,
        fill=alpha_color(theme.teal, opacity),
    )
    draw.text(
        (start_x + (step_bounds[2] - step_bounds[0]) + gap, 306),
        caption,
        font=MONO,
        fill=alpha_color(theme.text, opacity),
    )


def render_frame(base: Image.Image, theme: Theme, frame_index: int) -> Image.Image:
    elapsed = frame_index / FPS
    image = base.copy()
    motion = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(motion, "RGBA")

    loop_opacity = min(ease(elapsed / 0.42), ease((SECONDS - elapsed) / 0.42))
    stage_index = current_stage(elapsed)
    packet_x = packet_position(elapsed)
    progress_color = theme.green if elapsed >= COMPLETE_AT else theme.teal

    draw.line(
        (NODE_X[0], NODE_Y, round(packet_x), NODE_Y),
        fill=alpha_color(progress_color, 0.98 * loop_opacity),
        width=3,
    )

    for index, center_x in enumerate(NODE_X):
        completed_at = TRAVEL_STARTS[index] if index < len(TRAVEL_STARTS) else COMPLETE_AT
        is_complete = elapsed >= completed_at
        is_active = index == stage_index and not is_complete

        if is_complete:
            draw.ellipse(
                (
                    center_x - NODE_RADIUS,
                    NODE_Y - NODE_RADIUS,
                    center_x + NODE_RADIUS,
                    NODE_Y + NODE_RADIUS,
                ),
                fill=alpha_color(theme.complete_fill, loop_opacity),
                outline=alpha_color(theme.green, loop_opacity),
                width=3,
            )
            draw.line(
                (
                    center_x - 7,
                    NODE_Y,
                    center_x - 1,
                    NODE_Y + 6,
                    center_x + 9,
                    NODE_Y - 7,
                ),
                fill=alpha_color(theme.green, loop_opacity),
                width=3,
                joint="curve",
            )
        elif is_active:
            pulse = 0.5 + 0.5 * math.sin((elapsed - ARRIVALS[index]) * math.tau / 0.85)
            pulse_radius = NODE_RADIUS + 2 + round(3 * pulse)
            draw.ellipse(
                (
                    center_x - pulse_radius,
                    NODE_Y - pulse_radius,
                    center_x + pulse_radius,
                    NODE_Y + pulse_radius,
                ),
                outline=alpha_color(theme.blue, (0.42 + 0.35 * pulse) * loop_opacity),
                width=2,
            )
            draw.ellipse(
                (
                    center_x - NODE_RADIUS,
                    NODE_Y - NODE_RADIUS,
                    center_x + NODE_RADIUS,
                    NODE_Y + NODE_RADIUS,
                ),
                fill=alpha_color(theme.idle_fill, loop_opacity),
                outline=alpha_color(theme.teal, loop_opacity),
                width=3,
            )

        if is_complete:
            label_color = theme.green
        elif is_active:
            label_color = theme.teal
        else:
            label_color = theme.muted
        draw_centered_text(
            draw,
            center_x,
            251,
            STAGES[index],
            STAGE_LABEL,
            alpha_color(label_color, loop_opacity),
        )

    if elapsed < COMPLETE_AT:
        glow_dot(motion, round(packet_x), NODE_Y, theme, loop_opacity)
        draw_current_detail(
            draw,
            theme,
            stage_index,
            detail_alpha(elapsed, stage_index) * loop_opacity,
        )
    else:
        ready_opacity = ease((elapsed - COMPLETE_AT) / 0.22) * loop_opacity
        step = "5 / 5"
        caption = "Evidence ready  ·  scores · traces · audit metadata packaged"
        step_bounds = draw.textbbox((0, 0), step, font=MONO_SMALL_BOLD)
        caption_bounds = draw.textbbox((0, 0), caption, font=MONO)
        gap = 18
        total_width = (step_bounds[2] - step_bounds[0]) + gap + (caption_bounds[2] - caption_bounds[0])
        start_x = (WIDTH - total_width) / 2
        draw.text(
            (start_x, 310),
            step,
            font=MONO_SMALL_BOLD,
            fill=alpha_color(theme.green, ready_opacity),
        )
        draw.text(
            (start_x + (step_bounds[2] - step_bounds[0]) + gap, 306),
            caption,
            font=MONO,
            fill=alpha_color(theme.text, ready_opacity),
        )

    image.alpha_composite(motion)
    return image.convert("RGB")


def build_palette(theme: Theme, source: Image.Image) -> Image.Image:
    """Keep the README canvas color exact after GIF palette conversion."""
    reduced = source.quantize(colors=95, method=Image.Quantize.MEDIANCUT)
    reduced_palette = reduced.getpalette() or []
    used_indexes = sorted(index for _count, index in (reduced.getcolors() or []))
    colors = [theme.background]
    for index in used_indexes:
        offset = index * 3
        color = tuple(reduced_palette[offset : offset + 3])
        if len(color) == 3 and color not in colors:
            colors.append(color)

    palette_values = [channel for color in colors[:96] for channel in color]
    palette_values.extend([0] * (768 - len(palette_values)))
    palette = Image.new("P", (1, 1), 0)
    palette.putpalette(palette_values)
    return palette


def quantize_frame(
    theme: Theme,
    frame: Image.Image,
    palette: Image.Image,
) -> Image.Image:
    quantized = frame.quantize(palette=palette, dither=Image.Dither.NONE)
    background = Image.new("RGB", frame.size, theme.background)
    difference = ImageChops.difference(frame, background)
    red, green, blue = difference.split()
    maximum_difference = ImageChops.lighter(ImageChops.lighter(red, green), blue)
    exact_background = maximum_difference.point(lambda value: 255 if value == 0 else 0)
    quantized.paste(0, mask=exact_background)
    return quantized


def encode_theme(theme: Theme) -> Path:
    output = ASSET_DIR / f"infinity-grading-flow-{theme.name}.gif"
    base = draw_static(theme)
    raw_frames = [render_frame(base, theme, index) for index in range(FRAME_COUNT)]
    palette_source = build_palette(theme, raw_frames[round(COMPLETE_AT * FPS)])
    frames = [quantize_frame(theme, frame, palette_source) for frame in raw_frames]
    frames[0].save(
        output,
        save_all=True,
        append_images=frames[1:],
        duration=[80 if index % 3 != 2 else 90 for index in range(FRAME_COUNT)],
        loop=0,
        optimize=True,
        disposal=1,
    )
    print(
        f"wrote {output} "
        f"({output.stat().st_size / 1024:.1f} KiB, {FRAME_COUNT} frames)"
    )
    return output


def main() -> None:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        encode_theme(theme)


if __name__ == "__main__":
    main()

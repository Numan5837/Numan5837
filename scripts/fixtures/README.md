# Offline arcade fixture

`contribution-calendar.json` contains synthetic test data, not a person's GitHub activity. It has 14 calendar days, 19 contributions, and 8 active days. The three pull requests and two repositories are synthetic too.

The fixture uses the nested input format expected by `render_arcade.py`, rather than the flat `contribution-data.json` website output. From the repository root, render into a scratch directory:

```sh
python scripts/render_arcade.py --calendar-json scripts/fixtures/contribution-calendar.json --output .arcade-preview/contribution-pacman.svg
```

This writes an animated SVG, a static SVG, and the JSON snapshot into `.arcade-preview/`. No token or GitHub request is needed. Do not publish these synthetic outputs as real profile activity.

Run the renderer's offline regression checks with:

```sh
python -m unittest discover -s scripts -p "test_*.py"
```

The initial tests exercise the three-output contract and the static fallback. Zero-activity calendars, absent optional public counts, and invalid-count failure behavior are useful follow-up cases for the collaboration.

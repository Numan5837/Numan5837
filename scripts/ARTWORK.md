# Profile motion system

The README uses repository-hosted SVG and GIF assets. Core artwork does not depend on an external rendering service. SVGs contain no JavaScript, remote fonts, or `foreignObject` elements.

## Regenerate the new artwork

```sh
python scripts/render_profile_v2.py
```

Requires Python 3.10 or later and only the standard library. It generates the animated hero, navigation, founder card, experience cards, domain grid, verifier graph, and section titles. Mobile artwork is selected below 600 CSS pixels. Static SVGs are selected for reduced-motion preferences. The hero contains the animated knot and orbiting particles, with no center badge.

## Contribution arcade

The Pac-Man workflow (retaining its existing `contribution-snake.yml` filename for workflow continuity) maintains the arcade assets on the `output` branch. Pac-Man consumes the contribution squares, then reveals public activity counters before the replay resets. Calendar data comes from GitHub GraphQL; public pull-request and repository counts come from GitHub's public REST API. Snake is no longer displayed or generated.

The command below produces three files from the same snapshot:

- `contribution-pacman.svg`: animated calendar consumption and counter reveal.
- `contribution-pacman-static.svg`: full calendar and final counters for reduced motion.
- `contribution-data.json`: public calendar days and activity totals used by the playable website, with a UTC snapshot timestamp.

The README displays the replay. The linked companion website provides keyboard and touch controls because GitHub READMEs do not execute JavaScript.

```sh
python scripts/render_arcade.py --username Numan5837 --output dist/contribution-pacman.svg
```

The workflow supplies `GITHUB_TOKEN`. For offline checks, provide a saved contributionCalendar object using `--calendar-json`:

```sh
python scripts/render_arcade.py --calendar-json calendar.json --output dist/contribution-pacman.svg
```

Offline input must use the nested `contributionCalendar` shape: `totalContributions` plus `weeks[].contributionDays[]`, where each day has `date` and `contributionCount`. The generated `contribution-data.json` uses a flat `days` list and is not an offline input file.

Offline input can include `publicPullRequests` and `publicRepositories` alongside the calendar. Missing optional counts remain unavailable rather than becoming zero. A failed data request stops before publishing output.

## Preserved artwork

The original Infinity Megatron grading GIFs remain in the README, with separate light/dark variants and static PNG fallbacks. Their renderer is `render_enterprise_grading.py` (requires Pillow). The new verifier graph remains animated.

## Review before publishing

Inspect the rendered README at desktop and mobile widths, verify navigation targets, and check animated and static sources. Keep the Terminal-Bench PR marker pair exactly once; `update_harbor_contributions.py` updates only that block. SVG labels and demo graphs describe workflows, not measured performance claims.

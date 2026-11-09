# Profile motion system

The README uses repository-hosted SVG and GIF assets. Core artwork does not depend on an external rendering service. SVGs contain no JavaScript, remote fonts, or `foreignObject` elements.

## Regenerate the new artwork

```sh
python scripts/render_profile_v2.py
```

Requires Python 3.10 or later and only the standard library. It generates the animated hero, navigation, experience cards, domain grid, verifier graph, and section titles. Mobile artwork is selected below 600 CSS pixels. Static SVGs are selected for reduced-motion preferences.

## Contribution arcade

The Pac-Man workflow (retaining its existing `contribution-snake.yml` filename for workflow continuity) maintains the Pac-Man calendar on the `output` branch. Pac-Man uses actual calendar counts from GitHub GraphQL and creates a static calendar alongside the animation. The README asset is an animated replay; browser game controls require a companion website because GitHub READMEs do not run JavaScript. Snake is no longer displayed or generated.

```sh
python scripts/render_arcade.py --username Numan5837 --output dist/contribution-pacman.svg
```

The workflow supplies `GITHUB_TOKEN`. For offline checks, provide a saved contributionCalendar object using `--calendar-json`. A failed calendar request stops before publishing output.

## Preserved artwork

The original Infinity Megatron grading GIFs remain in the README, with separate light/dark variants and static PNG fallbacks. Their renderer is `render_enterprise_grading.py` (requires Pillow). The new verifier graph remains animated. The desktop and mobile hero marks are unlabeled terminal glyphs.

## Review before publishing

Inspect the rendered README at desktop and mobile widths, verify navigation targets, and check animated and static sources. Keep the Terminal-Bench PR marker pair exactly once; `update_harbor_contributions.py` updates only that block. SVG labels and demo graphs describe workflows, not measured performance claims.

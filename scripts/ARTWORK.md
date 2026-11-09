# Terminal profile artwork

The profile uses repository-hosted GIFs so its core visuals do not depend on an external card service.

To regenerate the artwork with Python 3.10 or newer:

```sh
python -m pip install "Pillow>=10,<13"
python scripts/render_console.py
```

The renderer uses Segoe UI and Consolas on Windows, or DejaVu Sans and DejaVu Sans Mono on Linux. Font changes can alter line widths; inspect the generated PNGs and GIFs before committing.

The README selects static PNGs for `prefers-reduced-motion: reduce`. Essential role information is also plain text. The contribution animation remains maintained by the existing workflow on the `output` branch; the Terminal-Bench PR refresh markers must each appear exactly once.

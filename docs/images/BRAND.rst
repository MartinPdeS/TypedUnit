TypedUnit visual assets
=======================

The selected "Dimensional type" mark frames a blue U with code brackets and
a mint plus. It connects Python type annotations with physical units. The
favicon uses pixel-aligned geometry on a light tile for contrast in browser tabs.

Assets
------

* ``logo.svg`` / ``logo.png``: horizontal logo for light backgrounds.
* ``logo-dark.svg`` / ``logo-dark.png``: horizontal logo for dark backgrounds.
* ``icon.svg`` / ``icon.png``: square icon with a transparent background.
* ``brand-preview.svg`` / ``brand-preview.png``: visual overview of the system.
* ``../source/_static/favicon.svg``: browser icon with simplified geometry.
* ``../source/_static/favicon.ico``: 16, 32, 48, 64, 128, and 256 pixel sizes.
* ``../source/_static/favicon-16x16.png`` and ``favicon-32x32.png``: PNG fallbacks.
* ``../source/_static/apple-touch-icon.png``: 180 pixel touch icon.
* ``../source/_static/thumbnail.png``: 512 pixel gallery thumbnail.

The SVG files are editable vector masters. Wordmark lettering is outlined,
so viewers do not need fonts installed. The PNG logos are 1600 by 480 pixels;
the PNG icon is 1024 by 1024 pixels. All exports use sRGB colors and preserve
transparency outside the artwork.

Palette and usage
-----------------

* Navy: ``#122B46``.
* Blue: ``#246BFD``.
* Mint: ``#43E0C0``.
* Soft white: ``#F7FAFF``.

Use the complete logo where the name needs to be readable; use the square icon
for avatars and compact navigation. Below 32 pixels, use the favicon artwork.
Preserve the aspect ratio and leave clear space around the mark. Avoid adding
shadows, gradients, or color filters.

For example, with librsvg installed, regenerate a raster export from its master::

    rsvg-convert -w 1600 -o docs/images/logo.png docs/images/logo.svg

Wordmark lettering uses outlined DejaVu Sans glyphs. Its font license and
attribution are preserved in ``LICENSE-DejaVu.txt``; no font installation is
required to display these assets.

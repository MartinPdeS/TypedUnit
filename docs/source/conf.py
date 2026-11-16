#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path

from martinpdes_docs import configure


package_name = "TypedUnit"
logo = "../images/logo.svg"
favicon = "_static/favicon.svg"
thumbnail = str(Path(__file__).parent.parent / "images" / "icon.png")

globals().update(
    configure(
        project="TypedUnit",
        package=package_name,
        version="auto",
        repository="MartinPdeS/TypedUnit",
        logo=logo,
        favicon=favicon,
        gallery_default_thumb=thumbnail,
        html_theme_options={
            "logo": {
                "text": "",
                "image_light": "../images/logo.svg",
                "image_dark": "../images/logo-dark.svg",
                "alt_text": "TypedUnit home",
            },
        },
    )
)

html_css_files.append("brand.css")

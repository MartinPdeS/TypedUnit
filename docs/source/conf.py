#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path

from martinpdes_docs import configure


package_name = "TypedUnit"
logo = "../images/logo.png"
favicon = "_static/favicon.svg"
thumbnail = str(Path(__file__).parent.parent / "images" / "logo.png")

globals().update(
    configure(
        project="TypedUnits",
        package=package_name,
        repository="MartinPdeS/TypedUnit",
        logo=logo,
        favicon=favicon,
        gallery_default_thumb=thumbnail,
        html_theme_options={"show_nav_level": 1},
    )
)

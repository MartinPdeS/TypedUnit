#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from pathlib import Path

from sphinx_gallery.sorting import FileNameSortKey

from martinpdes_docs import configure


package_name = "TypedUnit"
version = os.getenv("tag", "latest")
logo = "../images/logo.png"
thumbnail = str(Path(__file__).parent.parent / "images" / "logo.png")

globals().update(
    configure(
        project="TypedUnits",
        package=package_name,
        repository="MartinPdeS/TypedUnit",
        version=version,
        logo=logo,
        favicon=logo,
        sphinx_gallery_conf={
            "default_thumb_file": thumbnail,
            "within_subsection_order": FileNameSortKey,
        },
    )
)

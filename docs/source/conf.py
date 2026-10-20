#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from pathlib import Path

from sphinx_gallery.sorting import FileNameSortKey

from martinpdes_docs import configure


package_name = "TypedUnit"
version = os.getenv("tag", "latest")
thumbnail = str(Path(__file__).parent / "_static" / "thumbnail.png")

globals().update(
    configure(
        project="TypedUnits",
        package=package_name,
        repository="MartinPdeS/TypedUnit",
        version=version,
        logo="_static/logo.svg",
        favicon="_static/favicon.svg",
        sphinx_gallery_conf={
            "default_thumb_file": thumbnail,
            "within_subsection_order": FileNameSortKey,
        },
    )
)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from sphinx_gallery.sorting import FileNameSortKey

from martinpdes_docs import configure


package_name = "TypedUnit"
version = os.getenv("tag", "latest")

globals().update(
    configure(
        project="TypedUnits",
        package=package_name,
        repository="MartinPdeS/TypedUnit",
        version=version,
        logo="_static/logo.svg",
        favicon="_static/favicon.svg",
        sphinx_gallery_conf={
            "default_thumb_file": "_static/thumbnail.png",
            "within_subsection_order": FileNameSortKey,
        },
    )
)

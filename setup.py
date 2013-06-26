#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.
"""

from setuptools import setup, find_packages
import os.path as path
import re


def version():
    init = path.join(path.dirname(path.abspath(__file__)),
                     'burger_vitrine_server', '__init__.py')
    with open(init, "r") as f:
        return re.search(r"__version__ = \"([^\"]+)\"", f.read()).group(1)


setup(
    name="burger_vitrine_server",
    version=version(),
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    author="Simon Marti",
    author_email="simon@ceilingcat.ch",
    description=("A HTTP Server which generates and serves "
                 "BurgerVitrine output."),
    keywords="minecraft burger vitrine hamburglar",
    dependency_links=('http://github.com/TkTech/Solum/'
                      'tarball/master#egg=S-lum-1.0',
                      'http://github.com/zacharyvoase/cssmin/'
                      'tarball/master#egg=cssmin-0.1.4',),
    install_requires=("flask", "Flask-Assets", "jsmin", "cssmin", "S-lum",
                      "closure")
)

#!/usr/bin/env python
# -*- coding: utf8 -*-

from setuptools import setup, find_packages


setup(
    name="burger_vitrine_server",
    version="0.1",
    packages=find_packages(),
    author="Simon Marti",
    author_email="simon@ceilingcat.ch",
    description=("A HTTP Server which generates and serves "
                 "BurgerVitrine output."),
    keywords="minecraft burger vitrine hamburglar",
    dependency_links=('http://github.com/TkTech/Solum/'
                      'tarball/master#egg=S-lum-1.0',),
    install_requires=("flask", "S-lum")
)

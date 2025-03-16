#!/usr/bin/env python3
"""Setup script for packaging and distributing Moinsy."""

from setuptools import setup, find_packages
import os

# Read the contents of the README file
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

# Read requirements from requirements.txt
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="moinsy",
    version="1.0.0",
    author="Moinsy Team",
    author_email="info@moinsy.org",
    description="Modular Installation System for Linux",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/moinsy/moinsy",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Environment :: X11 Applications :: Qt",
        "Topic :: System :: Installation/Setup",
        "Development Status :: 4 - Beta",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'moinsy=moinsy.src.moinsy:main',
        ],
    },
    include_package_data=True,
    package_data={
        'moinsy': [
            'src/resources/**/*',
            'src/core/tools/resources/**/*',
        ],
    },
)

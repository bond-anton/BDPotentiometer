# Configuration file for the Sphinx documentation builder.

import pathlib
import re

# -- Project information

project = "BDPotentiometer"
copyright = "2024-2026, Anton Bondarenko"
author = "Anton Bondarenko"


def _read_version():
    """Read __version__ from the package source without importing the package."""
    init_path = (
        pathlib.Path(__file__).resolve().parents[2]
        / "src"
        / "BDPotentiometer"
        / "__init__.py"
    )
    match = re.search(r'^__version__ = "([^"]+)"', init_path.read_text(), re.MULTILINE)
    if match is None:
        raise RuntimeError(f"Cannot find __version__ in {init_path}")
    return match.group(1)


release = _read_version()
version = release

# -- General configuration

extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx_rtd_theme",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
}
intersphinx_disabled_domains = ["std"]

# -- Options for HTML output

html_theme = "sphinx_rtd_theme"

# -- Options for EPUB output
epub_show_urls = "footnote"

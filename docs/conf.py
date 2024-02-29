# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

import datetime

# import os
import sys
from pathlib import Path

if sys.version_info < (3, 11):
    import tomli as tomllib
else:
    import tomllib

# import radionets

pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
pyproject = tomllib.loads(pyproject_path.read_text())


# -- Project information -----------------------------------------------------

project = pyproject["project"]["name"]
author = pyproject["project"]["authors"][0]["name"]
copyright = "{}.  Last updated {}".format(
    author, datetime.datetime.now().strftime("%d %b %Y %H:%M")
)
python_requires = pyproject["project"]["requires-python"]

# make some variables available to each page
rst_epilog = f"""
.. |python_requires| replace:: {python_requires}
"""

# The full version, including alpha/beta/rc tags.
version = "0.3.0"  # radionets.__version__
release = version


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.viewcode",
    "sphinx.ext.githubpages",
    "sphinx.ext.mathjax",
    "sphinx_automodapi.automodapi",
    "sphinx_automodapi.smart_resolver",
    "matplotlib.sphinxext.plot_directive",
    "numpydoc",
    "sphinx_design",
    "IPython.sphinxext.ipython_console_highlighting",
]


numpydoc_show_class_members = False
numpydoc_class_members_toctree = False
nbsphinx_timeout = 200  # allow max 2 minutes to build each notebook


# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "changes"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "pydata_sphinx_theme"
html_favicon = "_static/favicon.ico"

html_theme_options = {
    "logo": {
        "image_light": "_static/logo.svg",
        "image_dark": "_static/logo_dark.svg",
        "alt_text": "radionets",
    },
    "github_url": "https://github.com/radionets-project/radionets",
    "header_links_before_dropdown": 6,
    "navbar_start": ["navbar-logo"],
    "navigation_with_keys": False,
    "use_edit_page_button": True,
    "announcement": """
        <p>radionets is still in development, so expect large and rapid
        changes to structure and functionality as we explore various
        design choices before the 1.0 release.</p>
    """,
}


# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

html_context = {
    "default_mode": "light",
    "github_user": "radionets-project",
    "github_repo": "radionets",
    "github_version": "main",
    "doc_path": "docs",
}
html_css_files = ["radionets.css"]

html_title = f"{project} v{release}"

htmlhelp_basename = project + "doc"

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

# Sphinx gallery
from sphinx_gallery.sorting import FileNameSortKey

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
    "sphinx_copybutton",
    "matplotlib.sphinxext.plot_directive",
    "numpydoc",
    "sphinx_design",
    "IPython.sphinxext.ipython_console_highlighting",
    "sphinx_gallery.gen_gallery",
]

# graphviz/inheritance diagram settings
graphviz_output_format = "svg"
inheritance_node_attrs = dict(style="rounded", color="tan1")

# settings for copybutton
copybutton_exclude = ".linenos, .gp"
copybutton_selector = "div:not(.no-copybutton) > div.highlight > pre"

# settings for numpydoc
numpydoc_show_class_members = False
numpydoc_class_members_toctree = False

# settings for sphinx-gallery
sphinx_gallery_conf = {
    "examples_dirs": [
        "../examples",
    ],  # path to your example scripts
    "within_subsection_order": FileNameSortKey,
    "nested_sections": False,
    "filename_pattern": r".*\.py",
    "ignore_pattern": r"ipynb_to_gallery\.py",
    "copyfile_regex": r".*\.png",
    "promote_jupyter_magic": True,
    "line_numbers": True,
    "default_thumb_file": "_static/logo.svg",
    "pypandoc": True,
    "matplotlib_animations": True,
}

nbsphinx_timeout = 200  # allow max 2 minutes to build each notebook


# intersphinx
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/", None),
    "astropy": ("https://docs.astropy.org/en/latest/", None),
    # "pytorch": ("https://pytorch.org/doc/stable/", None),
    # "fastai": ("https://www.fast.ai/", None),
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "**.ipynb_checkpoints",
    "changes",
    "auto_examples/index.rst",
    "auto_examples/*/*.py.md5",
    "auto_examples/*/*.py",
    "auto_examples/*/*.ipynb",
]

# have all links automatically associated with the right domain.
default_role = "py:obj"

suppress_warnings = [
    "ref.citation",
    "undefined label: 'locally-disable-grad-doc'"
]

nitpick_ignore = [
    ("py:obj", "radionets.dl_framework.architectures.res_exp.GeneralELU"),
    ("py:obj", "radionets.dl_framework.architectures.res_exp.SRBlock"),
    ("py:obj", "radionets.dl_framework.architectures.unc_archs.GeneralELU"),
    ("py:obj", "radionets.dl_framework.architectures.unc_archs.LocallyConnected2d"),
    ("py:obj", "radionets.dl_framework.architectures.unc_archs.SRResNet_16"),
    ("py:obj", "radionets.dl_framework.callbacks.Callback"),
    ("py:obj", "radionets.dl_framework.callbacks.CancelBackwardException"),
    ("py:obj", "radionets.dl_framework.callbacks.Path"),
    ("py:obj", "train_inspection.py"),
    ("py:obj", "norm_path"),
    ("py:obj", "radionets"),
    ("py:obj", "Callback"),
    ("py:obj", "self.{event_name}"),
    ("py:class", "Dropout"),
    ("py:class", "BatchNorm"),
    ("py:class", "Module"),
    ("py:attr", "dst_type"),
    ("py:attr", "dtype"),
    ("py:attr", "device"),
    ("py:attr", "non_blocking"),
    ("py:attr", "requires_grad"),
    ("py:attr", "grad_input"),
    ("py:attr", "grad_output"),
    ("py:attr", "assign"),
    ("py:attr", "strict"),
    ("py:attr", "persistent"),
    ("py:func", "register_module_forward_hook"),
    ("py:func", "register_module_forward_pre_hook"),
    ("py:func", "register_module_full_backward_hook"),
    ("py:func", "register_module_full_backward_pre_hook"),
]

nitpick_ignore_regex = [
    ("py:class", r"torch.*"),
    ("py:meth", r"torch.*"),
    ("py:func", r"torch.*"),
    ("py:class", r"fastai.*"),
    ("py:class", r"fastcore.*"),
]

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
    "pygment_light_style": "default",
    "pygment_dark_style": "lightbulb",
    "github_url": "https://github.com/radionets-project/radionets",
    "icon_links": [
        {
            "name": "PyPI",
            "url": "https://pypi.org/project/radionets/",
            "icon": "fa-brands fa-python",
            "type": "fontawesome",
        },
    ],
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

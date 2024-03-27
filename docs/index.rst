:html_theme.sidebar_secondary.remove: true
:html_theme.sidebar_primary.remove: true

.. _radionets:

.. image:: _static/logo_text.svg
   :class: only-light no-scaled-link
   :align: center
   :width: 110%
   :alt: The radionets logo.

.. image:: _static/logo_text_dark.svg
   :class: only-dark no-scaled-link
   :align: center
   :width: 110%
   :alt: The radionets logo.


#######################
Radionets Documentation
#######################

.. currentmodule:: radionets

**Version**: |version| **Date**: |today|

**Useful links**:
`Source Repository <hhttps://github.com/radionets-project/radionets>`__ |
`Issue Tracker <https://github.com/radionets-project/radionets/issues>`__ |
`Pull Requests <https://github.com/radionets-project/radionets/pulls>`__

**License**: MIT

**Python**: |python_requires|


.. toctree::
  :maxdepth: 1
  :hidden:

  user-guide/index
  developer-guide/index
  api-reference/index
  changelog

  
Radionets is a deep-learning framework for the simulation and analysis of radio interferometric
data in Python. The goal is to reconstruct calibrated observations with convolutional Neural 
Networks to create high-resolution images. For further information, please have a look at our
`paper <https://www.aanda.org/component/article?access=doi&doi=10.1051/0004-6361/202142113>`_.

Analysis strategies leading to reproducible processing and evaluation of data recorded by radio interferometers:

* Simulation of datasets (see also `<https://github.com/radionets-project/radiosim>`_)
* Simulation of radio interferometer observations (see also `<https://github.com/radionets-project/pyvisgen>`_)
* Training of deep learning models
* Reconstruction of radio interferometric data

.. grid:: 1 2 2 3

    .. grid-item-card::

        :octicon:`book;40px`

        User Guide
        ^^^^^^^^^^

        Learn how to get started as a user. This guide
        will help you install radionets.

        +++

        .. button-ref:: user-guide/index
            :expand:
            :color: primary
            :click-parent:

            To the user guide


    .. grid-item-card::

        :octicon:`person-add;40px`

        Developer Guide
        ^^^^^^^^^^^^^^^

        Learn how to get started as a developer.
        This guide will help you install radionets for development
        and explains how to contribute.

        +++

        .. button-ref:: developer-guide/index
            :expand:
            :color: primary
            :click-parent:

            To the developer guide


    .. grid-item-card::

        :octicon:`code;40px`

        API Reference
        ^^^^^^^^^^^^^

        The API docs contain detailed descriptions of
        of the various modules, classes and functions
        included in radionets.

        +++

        .. button-ref:: api-reference/index
            :expand:
            :color: primary
            :click-parent:

            To the API docs

.. _getting_started_users:

*************************
Getting Started for Users
*************************


Installation
============

How To Get the Latest Version
-----------------------------

We recommend using the ``mamba`` package manager, which is a C++ reimplementation of ``conda``.
It can be found `here <https://github.com/mamba-org/mamba>`_.

To install ``radionets`` and it's dependencies from the environment file, use:

.. code-block:: console

  $ mamba env create -f environment.yml


Usage
=====

For each task, executables are installed to your ``PATH``. Each takes ``toml`` configuration
files as input to manage data paths and options. Simulated data is saved in ``hdf5``; trained
models are saved as ``pickle`` files.

* ``radionets_simulations <...>`` This script is used to simulate radio interferometric data
  sets for the training of deep learning models.
* ``radionets_training <...>`` This script is used to train a model on events with known truth
  values for the target variable, usually Monte Carlo simulations.
* ``radionets_evaluation <...>`` This script is used to evaluate the performance of the trained
  deep-learning models.

Default configuration files can be found in the examples directory. The examples directory
contains ``jupyter notebooks``, which show an example analysis pipeline and the corresponding
commands.

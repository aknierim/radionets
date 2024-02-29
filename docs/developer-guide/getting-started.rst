.. _getting_started_dev:

******************************
Getting Started for Developers
******************************

We strongly recommend using the lightweight `miniforge conda distribution <https://github.com/conda-forge/miniforge>`_
which ships with the ``mamba`` package manager, that is a C++ reimplementation of ``conda``.

.. warning::

   The following guide is used only if you want to *develop* the
   ``radionets`` package.


Cloning the Repository
======================

.. note::

   The examples below make use of SSH, and assume you already setup
   an SSH key to access GitHub. If you're unsure on how to setup an SSH
   key, see the `the GitHub documentation <https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account>`_
   for more information.


.. tab-set::

   .. tab-item:: Working in the main repository
      :sync: main

      Clone the repository:

      .. code-block:: console

          $ git clone git@github.com:radionets-project/radionets.git
          $ cd radionets


   .. tab-item:: Working a fork
      :sync: fork

      In order to checkout the software so that you can push changes to GitHub without
      having write access to the main repository at ``radionets-project/radionets``, you
      `need to fork <https://help.github.com/articles/fork-a-repo/>`_ it.

      After that, clone your fork of the repository and add the main reposiory as a second
      remote called ``upstream``, so that you can keep your fork synchronized with the main repository.

      .. code-block:: console

          $ git clone https://github.com/[YOUR-GITHUB-USERNAME]/radionets.git
          $ cd ctapipe
          $ git remote add upstream https://github.com/radionets-project/radionets.git


Setting Up the Development Environment
======================================

This repository is built as a python package. We recommend creating a mamba environment to handle
the dependencies of all packages. You can create one by running the following command in this
repository:

.. code-block:: console

   $ mamba env create -f environment.yml

Depending on your ``cuda`` version you have to specify the ``cudatoolkit`` version used by ``pytorch``.
If you are working on machines with ``cuda`` versions ``< 10.2``, please change the version number in the
``environment.yml`` file. Activate the environment via

.. code-block:: console

   $ mamba activate radionets

You will need to run that last command any time you open a new terminal to activate the conda environment.

Additionally, since the package ``pre-commit`` is used to ensure code quality, you will need to setup the
`pre-commit hook <https://pre-commit.com/>`_

.. code-block:: console

   $ pre-commit install

after the installation of the environment. The pre-commit hook will then execute the auto-formatter tools ``isort``, 
``black``, and the linting tool ``flake8`` with the same settings as if a pull request is checked on github.
If any problems are reported the commit will be rejected and you will need to fix the issues before trying to
commit again.



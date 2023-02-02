from setuptools import setup, find_packages

setup(
    name="radionets",
    version="0.2.0",
    description="Imaging radio interferometric data with neural networks",
    url="https://github.com/radionets-project/radionets",
    author="Kevin Schmidt, Felix Geyer",
    author_email="kevin3.schmidt@tu-dortmund.de, felix.geyer@tu-dortmund.de",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "fastai",
        "kornia",
        "pytorch-msssim",
        "numpy",
        "astropy",
        "tqdm",
        "click",
        "numba",
        "jupyter",
        "h5py",
        "scikit-image",
        "pandas",
        "toml",
        "pytest",
        "pytest-cov",
        "pytest-order",
        "comet_ml",
        "pre-commit",
    ],
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "radionets_simulations = radionets.simulations.scripts.simulate_images\
            :main",
            "radionets_training = radionets.dl_training.scripts.start_training:main",
            "radionets_evaluation = radionets.evaluation.scripts.start_evaluation:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Scientific/Engineering :: Astronomy",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
)

from setuptools import setup, find_packages

setup(
    name="radionets",
    version="0.1.4",
    description="Imaging radio interferometric data with neural networks",
    url="https://github.com/Kevin2/radionets",
    author="Kevin Schmidt, Felix Geyer, Kevin Laudamus",
    author_email="kevin3.schmidt@tu-dortmund.de",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "fastai",
        "fastcore",
        "kornia",
        "pytorch-msssim",
        "numpy",
        "astropy",
        "tqdm",
        "click",
        "geos",
        "shapely",
        "proj",
        "cartopy",
        "ipython",
        "jupyter",
        "jupytext",
        "h5py",
        "scikit-image",
        "pandas",
        "requests",
        "toml",
        "pytest-cov",
    ],
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "radionets_simulations = radionets.simulations.scripts.simulate_images:main",
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

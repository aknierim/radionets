from setuptools import setup, find_packages

setup(
    name="radionets",
    version="0.1.14",
    description="Imaging radio interferometric data with neural networks",
    url="https://github.com/radionets-project/radionets",
    author="Kevin Schmidt, Felix Geyer",
    author_email="kevin3.schmidt@tu-dortmund.de, felix.geyer@tu-dortmund.de",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "fastai==2.7.10",
        "kornia==0.6.9",
        "pytorch-msssim==0.2.1",
        "numpy==1.22.3",
        "astropy==5.2.1",
        "tqdm==4.64.1",
        "click==8.1.3",
        "jupyter==1.0.0",
        "h5py==3.7.0",
        "scikit-image==0.19.3",
        "pandas==1.5.2",
        "toml==0.10.2",
        "pytest==7.2.0",
        "pytest-cov==4.0.0",
        "pytest-order==1.0.1",
        "comet_ml==3.31.22",
        "pre-commit==2.21.0",
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

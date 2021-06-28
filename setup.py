from setuptools import setup, find_packages


base_packages = [
    "rasa>=2.6.0",
    "pandas>=1.0.5",
]

dev_packages = [
    "flake8>=3.6.0",
    "black>=19.10b0",
    "pre-commit>=2.5.1",
    "pytype>=2020.0.0",
    "pytest>=4.0.2",
    "pytest-xdist==1.32.0",
    "mkdocs==1.1",
    "mkdocs-material==5.4.0",
    "mkdocstrings==0.8.0",
    "pymdown-extensions>=7.1",
]



setup(
    name="taipo",
    version="0.0.1",
    packages=find_packages(exclude=["notebooks", "data"]),
    install_requires=base_packages,
    extras_require={
        "dev": dev_packages,
    },
)
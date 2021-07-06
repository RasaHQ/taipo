from setuptools import setup, find_packages


base_packages = [
    "rasa>=2.6.0",
    "pandas>=1.0.5",
    "PyYAML>=5.4.1",
    "numpy>=1.18.5",
    "typer==0.3.2",
    "nlpaug>=1.1.4",
    "parse>=1.19.0",
    "clumper>=0.2.13",
    "transliterate>=1.10.2",
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
    version="0.0.2",
    packages=find_packages(exclude=["notebooks", "data"]),
    install_requires=base_packages,
    extras_require={
        "dev": dev_packages,
    },
)

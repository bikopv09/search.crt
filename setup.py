"""
Setup script for SearchCRT package installation
Install with: python setup.py install
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="search-crt",
    version="1.0.0",
    author="bikopv09",
    author_email="bkservicoss@gmail.com",
    description="Sistema profissional de busca, comparativo e rastreamento de dados",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bikopv09/search.crt",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Office/Business",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.3.0",
        "openpyxl>=3.6.0",
        "pymongo>=3.12.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.9",
        ],
    },
    entry_points={
        "console_scripts": [
            "searchcrt=searchcrt_integrated:main",
        ],
    },
)

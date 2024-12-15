import setuptools
from setuptools import setup
import os

# Read the contents of your README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Get version from git tag with fallback
def get_version():
    version = os.environ.get('GITHUB_REF_NAME')
    if version and version.startswith('v'):
        return version.lstrip('v')
    return '0.0.0'  # fallback version

setup(
    name="SummarizeGPT",
    version=get_version(),
    author="Matt Harrison",
    author_email="matt@harrison.consulting",
    description="Tool to summarize directories of code for prompting with LLMs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Maralai/SummarizeGPT",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    install_requires=[
        'gitignore_parser',
        'tiktoken'
    ],
    entry_points={
        'console_scripts': [
            'SummarizeGPT=summarizeGPT.summarizeGPT:main',
        ],
    },
    license="GPLv3",
)
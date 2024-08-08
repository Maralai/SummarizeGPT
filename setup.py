from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='SummarizeGPT',
    version='1.2',
    packages=find_packages(),
    description='Tool to summarize directories of code for prompting with ChatGPT',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Matt Harrison',
    author_email='matt@harrison.consulting',
    license='GPLv3',
    url='https://github.com/Maralai/SummarizeGPT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    install_requires=required,
    entry_points={
        'console_scripts': [
            'SummarizeGPT=summarizeGPT.summarizeGPT:main',
        ],
    },
)

from setuptools import setup, find_packages

setup(
    name="cryptocore",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'cryptocore=src.cli:main',
        ],
    },
    test_suite="tests",
)

from setuptools import setup, find_packages

setup(
    name="cryptocore",
    version="7.0.0",  # Updated for Sprint 7
    packages=find_packages(include=['src', 'src.*']),
    install_requires=[
        'pycryptodome>=3.20.0',
    ],
    entry_points={
        'console_scripts': [
            'cryptocore=src.cryptocore:main',
        ],
    },
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Security :: Cryptography',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)

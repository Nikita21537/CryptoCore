from setuptools import setup, find_packages

setup(
    name="cryptocore",
    version="1.0.0",
    description="CryptoCore - инструмент для криптографических операций",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pycryptodome>=3.10.1",
    ],
    entry_points={
        "console_scripts": [
            "cryptocore=cryptocore:main",
        ],
    },
    python_requires=">=3.6",
    author="CryptoCore Team",
    author_email="example@example.com",
)

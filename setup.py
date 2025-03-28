from setuptools import setup, find_packages

# This is a backup for older pip versions
# Most users will use pyproject.toml
setup(
    name="wclip",
    version="0.1.2",
    packages=find_packages(),
    install_requires=[
        "pyperclip>=1.8.0",
    ],
    entry_points={
        'console_scripts': [
            'clipserver=clipserver.__main__:main',
        ],
    },
    python_requires='>=3.6',
)

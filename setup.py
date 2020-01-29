""" setup.py is the build script for setuptools. It tells setuptools about your package
(such as the name and version) as well as which code files to include."""
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyOpenIgtLink-mariatirindelli", # Replace with your own username
    version="0.0.1",
    author="Maria Tirindelli",
    author_email="maria.tirindelli@hotmail.it",
    description="A package to handle basic openigtlink message with python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mariatirindelli/PyOpenIgtlink",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
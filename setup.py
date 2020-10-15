from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("LICENSE", "r") as fh:
    license = fh.read()

setup(
    name="ryantay232",
    version="0.0.1",
    author="Ryan Tay",
    author_email="ryantay232@gmail.com",
    description="A system for making online exams fair",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ryantay232/Making-Online-Exams-fair",
    license=license,
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

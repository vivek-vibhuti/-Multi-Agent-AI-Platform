from setuptools import setup,find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="multi ai agent  workflow",
    version="0.1",
    author="vivek vibhuti",
    packages=find_packages(),
    install_requires = requirements,
)
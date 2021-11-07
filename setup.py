import os
from typing import List
from typing import Optional

import pkg_resources
from setuptools import find_packages
from setuptools import setup


def get_long_description() -> str:
    readme_filepath = os.path.join(os.path.dirname(__file__), "README.md")
    with open(readme_filepath) as f:
        return f.read()


def get_install_requires() -> List[str]:
    requirements = [
        "cmake",
        "setuptools== 57.0.0",
        "pika==1.2.0",
        "pygame==2.0.0",
        "numpy== 1.21.2",
        "opencv-python==4.5.4.58",
        "dlib==19.22.1"
    ]
    return requirements


def find_any_distribution(pkgs: List[str]) -> Optional[pkg_resources.Distribution]:
    for pkg in pkgs:
        try:
            return pkg_resources.get_distribution(pkg)
        except pkg_resources.DistributionNotFound:
            pass
    return None


setup(
    name="nose_controled_snake_game",
    version="1.0.0",
    description="Nose Controled Snake Game",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Manuel Mourato",
    packages=find_packages(),
    python_requires=">=3.8",
    setup_requires=['cmake'],
    install_requires=get_install_requires(),
    classifiers=[
        "Development Status :: Development",
        "Intended Audience :: Developers",
        "License :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)

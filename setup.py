from pkg_resources.extern.packaging.version import Version
from setuptools import find_packages, setup

__version__ = Version("0.1.0")

try:
    with open("README.rst", "r", encoding="utf-8") as f:
        readme = f.read()
except IOError:
    readme = ""

setup(
    name="a-dheanamh",
    author="emily woods",
    author_email="hello@emilywoods.me",
    url="",
    description="",
    long_description=readme,
    version=str(__version__),
    entry_points='''
         [console_scripts]
         aw-yay=aw_yay.main:main
     ''',
    packages=find_packages(),
    install_requires=[
        "click",
        "requests",
        "configparser"
    ],
    extras_require={"testing": ["black==19.3b0"]},
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3.7",
    ],
)

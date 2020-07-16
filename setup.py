#!/usr/bin/env python

from setuptools import setup, find_packages
import sys

if not (sys.version_info.major == 3 and sys.version_info.minor >= 7):
    print("[!] DirScanner requires Python 3.7 or higher!")
    print(
        "[*] You are using Python {}.{}.".format(
            sys.version_info.major, sys.version_info.minor
        )
    )
    sys.exit(1)

with open("requirements.txt") as fp:
    required = [line.strip() for line in fp if line.strip() != ""]

setup(
   name='DirScanner',
   version='1.0',
   description='Directory brute-force tool. Enumerates directory, checks for specific words in the content of the html and checks for possible directory traversal vulnerabilities',
   long_description=open('README.md').read(),
   author='Roberto Reigada Rodríguez',
   url='https://github.com/roberreigada/dirscanner',
   license='apache 2.0',
   author_email='roberreigada@gmail.com',
   packages=find_packages(),
   install_requires=required,
   python_requires='>=3.7',
   entry_points={"console_scripts": ["dirscanner=dirscanner.__main__:main"]}
)

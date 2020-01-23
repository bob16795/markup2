from setuptools import setup
import os


setup(
    name="markup",
    version="0.1.0",
    keywords="markdown compiler python script",
    packages=['markup_new', "pdfer"],
    install_requires=[
        'click',
    ],
    entry_points={
        'console_scripts': ['markup_n = markup_new.compile:main',
                            'mu_n = markup_new.compile:main']
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ]
)

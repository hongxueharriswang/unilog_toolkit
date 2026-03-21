from setuptools import setup, find_packages

setup(
    name="unilog-toolkit",
    version="0.3.0",
    author="Harris Wang",
    author_email="harrisw@athabascau.ca",
    description="A Python toolkit for UniLog: a unified logic language with parser and inference engine.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/harriswang/unilog-toolkit",
    packages=find_packages(),
    install_requires=[
        "antlr4-python3-runtime>=4.9",
        "numpy>=1.19"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
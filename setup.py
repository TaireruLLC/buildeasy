from setuptools import setup, find_packages

setup(
    name="buildeasy",
    version="0.0.3",
    author="Taireru LLC",
    author_email="tairerullc@gmail.com",
    description="buildeasy is a Python package that enables users to seamlessly convert Python files into class-based instances, allowing for a more structured and object-oriented approach to module management.",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/TaireruLLC/buildeasy",
    packages=find_packages(),
    install_requires=[
        
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    license="MIT",
)

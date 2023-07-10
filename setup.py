import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PyQML",
    version="0.0.1",
    author="Gaétan Cabaret",
    author_email="serval7391@gmail.com",
    description="A small module to simplify my developer life",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    package_data={'PyQML': ['*.qml', "Components/*.qml", "Components/base/*.qml", "QQuickMpl/*.qml"]},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

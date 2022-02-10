import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="agilent-format",
    version="0.4.2",
    author="Stuart Read",
    author_email="stuart.read@lightsource.ca",
    description="File reader for Agilent Resolutions Pro FT-IR images",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/stuart-cls/python-agilent-file-formats",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'numpy',
    ],
    test_suite="agilent_format.tests.suite"
)

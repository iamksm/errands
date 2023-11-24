from setuptools import find_packages, setup

with open("README.md") as readme:
    README = readme.read()

setup(
    name="errands",
    version="0.0.1",
    description="Python package to help with running and scheduling tasks",
    long_description=README,
    author="Kossam Ouma",
    author_email="koss797@gmail.com",
    packages=find_packages(
        exclude=[
            "tests",
        ]
    ),
    install_requires=[
        "croniter>=2.0.1",
        "ipython",
    ],
    include_package_data=True,
)

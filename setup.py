from setuptools import find_packages, setup

setup(
    name="DSTrade",
    version="0.1.1",
    author="Daniel Sinkin",
    author_email="danielsinkin97@gmail.com",
    description="Full Alphavantage API python interface",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Daniel-Sinkin/DSTrade",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=open("requirements.txt").read().splitlines(),
    python_requires=">=3.10",
)

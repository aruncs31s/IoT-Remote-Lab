from setuptools import setup, find_packages

setup(
    name="iot_remote_lab",
    version="0.0.3",
    author="Arun CS",
    author_email="csarun@proton.com",
    description="Iot Remote Lab",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/aruncs31s/IoT-Remote-Lab",  # Add your repo URL
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "flask",
        "flask-cors",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
   
)
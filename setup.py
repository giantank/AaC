from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    readme_description = fh.read()

runtime_dependencies = [
    "attrs == 21.2.0",
    "coverage == 6.0",
    "jsonschema == 4.0.1",
    "pyrsistent == 0.18.0",
    "PyYAML == 5.4.1",
    "six == 1.16.0",
    "click == 8.0.1",
    "pathspec == 0.9.0",
    "platformdirs == 2.4.0",
    "pyrsistent == 0.18.0",
    "regex == 2021.9.30",
    "typing-extensions == 3.10.0.2",
    "pluggy == 1.0.0",
]

development_dependencies = [
    "wheel == 0.37.0",
    "black == 21.9b0",
    "mccabe == 0.6.1",
    "mypy-extensions == 0.4.3",
    "pycodestyle == 2.7.0",
    "pyflakes == 2.3.1",
    "build == 0.7.0",
    "twine == 3.4.2",
]

test_dependencies = [
    "tox >= 3.24",
    "nose2 >= 0.10.0",
    "coverage >= 6.0",
    "flake8 >= 3.9",
    "flake8-docstrings == 1.6.0",
    "flake8-fixme == 1.1.1",
    "flake8-eradicate == 1.1.0",
    "flake8-assertive == 1.3.0",
    "eradicate<3.0,>=2.0",
]

setup(
    name="aac",
    version="0.0.4",
    long_description=readme_description,
    long_description_content_type="text/markdown",
    packages=find_packages(where="aac", exclude="tests"),
    package_dir={"": "src"},
    install_requires=runtime_dependencies,
    setup_requires=development_dependencies,
    tests_require=test_dependencies,
    entry_points={
        "console_scripts": [
            "aac = aac:runCLI",
        ]
    },
    extras_require={
        "test": test_dependencies,
        "dev": development_dependencies,
        "all": test_dependencies + development_dependencies,
    },
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
    ],
    keywords=["MBSE"],
)
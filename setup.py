import subprocess

from setuptools import Command, setup

# -----------------------------------------------------------------------------


def system(command):
    class SystemCommand(Command):
        user_options = []

        def initialize_options(self):
            pass

        def finalize_options(self):
            pass

        def run(self):
            subprocess.check_call(command, shell=True)

    return SystemCommand


# -----------------------------------------------------------------------------

setup(
    name="Flask-Annex",
    version="0.5.0",
    description="Efficient integration of external storage services for Flask",
    url="https://github.com/4Catalyzer/flask-annex",
    author="Jimmy Jia",
    author_email="tesrin@gmail.com",
    license="MIT",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Framework :: Flask",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="storage s3 flask",
    packages=("flask_annex",),
    install_requires=("Flask >= 0.10",),
    extras_require={
        "s3": ("boto3 >= 1.4.0",),
        "tests": ("pytest", "pytest-cov"),
        "tests-s3": ("moto", "requests"),
    },
    cmdclass={
        "clean": system("rm -rf build dist *.egg-info"),
        "package": system("python setup.py sdist bdist_wheel"),
        "publish": system("twine upload dist/*"),
        "release": system("python setup.py clean package publish"),
        "test": system("tox"),
    },
)

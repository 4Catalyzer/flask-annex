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
    version="2.0.0",
    description="Efficient integration of external storage services for Flask",
    url="https://github.com/4Catalyzer/flask-annex",
    author="Jimmy Jia",
    author_email="tesrin@gmail.com",
    license="MIT",
    python_requires=">=3.10",
    classifiers=[
        "Framework :: Flask",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="storage s3 flask",
    packages=[
        "flask_annex",
    ],
    install_requires=("Flask >= 2.0", "packaging >= 17.0"),
    extras_require={
        "s3": ("boto3 >= 1.4.0",),
        "tests": ("pytest", "pytest-cov"),
        "tests-s3": ("moto", "requests"),
    },
    cmdclass={
        "clean": system("rm -rf build dist *.egg-info"),
        "package": system("python3 setup.py sdist bdist_wheel"),
        "publish": system("twine upload dist/*"),
        "release": system("python3 setup.py clean package publish"),
        "test": system("tox"),
    },
)

from setuptools import setup

setup(
    name="Flask-Annex",
    version='0.0.6',
    description="Efficient integration of external storage services for Flask",
    url='https://github.com/4Catalyzer/flask-annex',
    author="Jimmy Jia",
    author_email='tesrin@gmail.com',
    license='MIT',
    classifiers=(
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: Flask',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ),
    keywords='storage s3 flask',
    packages=('flask_annex',),
    install_requires=(
        'Flask',
        'six'
    ),
    extras_require={
        's3': ('boto',)
    }
)

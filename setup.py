
# Learn more: https://github.com/Ensembl/ols-client
import os

from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as f:
    readme = f.read()

with open(os.path.join(os.path.dirname(__file__), 'LICENSE')) as f:
    license_ct = f.read()

with open(os.path.join(os.path.dirname(__file__), 'VERSION')) as f:
    version = f.read()


def import_requirements():
    with open(os.path.join(os.path.dirname(__file__), 'requirements.txt')) as f:
        content = f.readlines()
        # you may also want to remove whitespace characters like `\n` at the end of each line
        content = [x.strip() for x in content]
        return content


setup(
    name='production_services',
    version=version,
    description='Ensembl Production Database Application',
    long_description=readme,
    author='Marc Chakiachvili,James Allen,Luca Da Rin Fioretto,Vinay Kaikala',
    author_email='mchakiachvili@ebi.ac.uk,jallen@ebi.ac.uk,ldrf@ebi.ac.uk,vkaikala@ebi.ac.uk',
    maintainer='Ensembl Production Team',
    maintainer_email='ensembl-production@ebi.ac.uk',
    url='https://github.com/Ensembl/production_services',
    license='APACHE 2.0',
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=import_requirements(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.6",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)

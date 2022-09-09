# -*- coding: utf-8 -*-
"""Installer for the gene.tumour package."""

from setuptools import find_packages
from setuptools import setup


long_description = ''


setup(
    name='gene.tumour',
    version='2.0',
    description="",
    long_description=long_description,
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords='',
    author='',
    author_email='',
    url='',
    license='GPL version 2',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['gene'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'plone.directives.form',
        'plone.api',
        'Products.GenericSetup',
        'setuptools',
        'plone.app.dexterity',
        'xlrd',
        'xlwt',
        'collective.z3cform.datagridfield',
        'collective.schedule',
        'gene.common',
        'gene.theme',
    ],
    extras_require={
        'test': [
            'plone.app.testing',
            # Plone KGS does not use this version, because it would break
            # Remove if your package shall be part of coredev.
            # plone_coredev tests as of 2016-04-01.
            'plone.testing>=5.0.0',
            'plone.app.contenttypes',
            'plone.app.robotframework[debug]',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)

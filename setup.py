from setuptools import setup, find_packages

setup(
    name='FlexTransform',
    version='1.1.0',
    description='Flexible Transform is a tool that enables dynamic translation between formats',
    url='https://github.com/anl-cyberscience/FlexTransform/',
    author='The CFM Team',
    author_email='fedhelp@anl.gov',
    classifiers=[
        # See: https://pypi.python.org/pypi?%3Aaction=list_classifiers

        # How mature is this project? Common values are
        # Development Status :: 1 - Planning
        # Development Status :: 2 - Pre-Alpha
        # Development Status :: 3 - Alpha
        # Development Status :: 4 - Beta
        # Development Status :: 5 - Production/Stable
        # Development Status :: 6 - Mature
        # Development Status :: 7 - Inactive
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Information Technology',
        'Topic :: Security',

        # Pick your license as you wish (should match 'license' above)
        'License :: Other/Proprietary License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='',
    packages=find_packages(exclude=['contrib', 'doc', 'tests*']),
    install_requires=[
        'python-dateutil',
        'lxml',
        'pytz',
        'dumper',
        'rdflib',
    ],
    entry_points={
        'console_scripts': [
            'flext = FlexTransform.FlexT:main'
        ]
    },
    test_suite='nose.collector',
    tests_require=['nose'],
    include_package_data=True,
    package_data={
        'FlexTransform': [
            'resources/*.xml',
            'resources/*.owl',
            'resources/*.zip',
            'resources/*.rdf',
            'resources/sampleConfigurations/*',
            'resources/schemaDefinitions/*',
            'resources/schemas/*'
        ]
    }
)

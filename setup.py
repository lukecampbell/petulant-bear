try:
    from setuptools import setup, find_packages
    packages = find_packages()
except ImportError:
    from distutils import setup

setup(
    name='Petulant Bear',
    version='0.1',
    description='Presents etree interface to netcdf4-python objects using NCML data model',
    author='David Stuebe',
    author_email='DStuebe@ASAScience.com',
    url='https://github.com/dstuebe/petulant-bear',
    classifiers=[
        'License :: GNU GPL',
        'Topic :: NetCDF :: Metadata',
        'Topic :: NetCDF :: NcML',
        'Topic :: XML :: Metadata'
        ],
    license='GNU GPL',
    keywords='netcdf lxml xml metadata ncml',
    packages= ['petulantbear'],
    install_requires = [
            'netCDF4>=1.0.0',
            'nose>=1.2.0',
            'numpy>=1.7.0',
            'lxml>=3.2.1',
            ],
)

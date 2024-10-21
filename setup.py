from distutils.core import setup

try:
    import pypandoc
    long_description = pypandoc.convert_file('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()

setup(name='mlmaid',
      version='0.1.2.3',
      description='ML-MAID : ML - Miniature Automatic Installer for Dependencies',
      long_description_content_type='text/markdown',
      long_description=long_description,
      author='Aakash Singh Bais',
      author_email='xbais@duck.com',
      url='https://github.com/xbais/ml-maid',
      package_dir = {'': 'src'},
      install_requires=['tqdm', 'setuptools', 'tabulate', 'tqdm', 'wheel'],
      packages=['mlmaid'],
     )

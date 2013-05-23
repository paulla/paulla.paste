import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'pyramid_debugtoolbar',
    'waitress',
    'pyramid_fanstatic',
    'rebecca.fanstatic',
    'couchdbkit',
    'pyramid_beaker',
    'Pygments',
    ]

setup(name='paulla.paste',
      version='0.0',
      description='paulla.paste',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web pyramid pylons',
      packages=find_packages(),
      include_package_data=True,
      namespace_packages=['paulla'],
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="paullapaste",
      entry_points = """\
      [paste.app_factory]
      main = paulla.paste:main
      """,
      )


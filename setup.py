import codecs
from setuptools import setup, find_packages

setup(name='pyJasper',
      maintainer='Maximillian Dornseif',
      maintainer_email='md@hudora.de',
      url='https://github.com/hudora/pyJasper',
      version='0.41',
      description='toolkit to access JasperReports from Python',
      long_description=codecs.open('README.textile', "r", "utf-8").read(),
      license='BSD',
      classifiers=['Intended Audience :: Developers',
                   'Programming Language :: Python'],
      
      packages = find_packages(),
      package_data = {
          # If any package contains *.txt or *.rst files, include them:
          '': ['*.xml', '*.jrxml', '*.jar', '*.py', '*.sh'],
          #backend/lib/
          #backend/webapps/
      },
      install_requires = ['httplib2'],
      zip_safe = False,
)

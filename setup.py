from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

setup(name='pyJasper',
      maintainer='Maximillian Dornseif',
      maintainer_email='md@hudora.de',
      url='https://cybernetics.hudora.biz/projects/wiki/pyJasper',
      version='0.3',
      description='toolkit to access JasperReports from Python',
      #long_description=long_description,
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

import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages

setup(name='pyJasper',
      maintainer='Maximillian Dornseif',
      maintainer_email='md@hudora.de',
      url='https://cybernetics.hudora.biz/projects/wiki/pyJasper',
      version='0.2',
      description='toolkit to access JasperReports from Python',
      license='BSD',
      classifiers=['Intended Audience :: Developers',
                   'Programming Language :: Python'],
      
        packages = find_packages(),
        package_data = {
            # If any package contains *.txt or *.rst files, include them:
            '': ['*.txt', '*.rst'],
        },
      
      zip_safe = False,
)

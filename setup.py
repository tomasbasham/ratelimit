from setuptools import setup
from ratelimit.version import Version

def readme():
  with open('README.rst') as file:
    return file.read()

setup(name='ratelimit',
      version=Version('1.1.0').number,
      description='API rate limit decorator',
      long_description=readme().strip(),
      author='Tomas Basham',
      author_email='me@tomasbasham.co.uk',
      url='https://github.com/tomasbasham/ratelimit',
      license='MIT',
      packages=['ratelimit'],
      install_requires=[],
      keywords='ratelimit api decorator',
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Topic :: Software Development'
      ],
      include_package_data=True,
      zip_safe=False)

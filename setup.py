from setuptools import setup

setup(name='pywebfontkit',
      version='0.1',
      description='a simple python based font bundle generator for web.',
      url='http://github.com/meyt/pywebfontkit',
      author='Mahdi Ghane.g',
      license='GPL',
      keywords='pywebfontkit svg woff ttf fontforge otf eot css html webfont webfontgenerator',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Build Tools'
      ],
      scripts=['pywebfontkit'],
      zip_safe=False)
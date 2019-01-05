from setuptools import setup


setup(
    name='pywebfontkit',
    version='0.4.0',
    description='a simple python based font bundle generator for web.',
    url='http://github.com/meyt/pywebfontkit',
    long_description=open('README.rst').read(),
    author='Mahdi Ghane.g',
    license='GPLv3',
    keywords='pywebfontkit svg woff ttf fontforge otf eot '
             'css html webfont webfontgenerator',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Build Tools'
    ],
    entry_points={
        'console_scripts': [
            'pywebfontkit = pywebfontkit.main'
        ]
    },
    zip_safe=False
)

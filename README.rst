PyWebFontKit
============

A simple python based font bundle generator for web.
collect multiple SVG files and convert to `woff`, `ttf`, `svg`, `otf`, `eof`, and create `CSS` with `HTML` map.
 
 
Requirements
------------

- fontforge
- python (obviously)


Instructions
------------

- Download

..  code-block:: bash

		git clone https://github.com/meyt/pywebfontkit.git
		cd ./pywebfontkit
		sudo python ./setup.py install

Or install from pypi

..  code-block:: bash

		sudo pip install pywebfontkit


- Put SVG files to your bundle path like this ``./bundles/myfontname/svg``
		
- Build

..  code-block:: bash

		pywebfontkit -f myfontname
		
Or

Run through fontforge

..  code-block:: bash

		fontforge -lang=py -script pywebfontkit.py -f myfontname


P.S: On some distribution like Ubuntu, doesn't work with python3,
so install ``python-fontforge`` and run it under python2.

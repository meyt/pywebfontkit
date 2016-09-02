# PyWebFontKit

a simple python based font bundle generator for web.
collect multiple SVG files and convert to `woff`, `ttf`, `svg`, `otf`, `eof`, and create `CSS` with `HTML` map.
 
 
## Requirements
- fontforge
- python 3 
 
## Instructions	

- Download
	
		git clone https://github.com/meyt/pywebfontkit.git
		cd ./pywebfontkit
		
- Put svg files to your bundle path like this `./bundles/myfontname/svg`
		
- Build

		python ./pywebfontkit  -f myfontname -p myprefix
		



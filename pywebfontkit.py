#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os
# noinspection PyUnresolvedReferences
import fontforge
import argparse

from tempfile import NamedTemporaryFile
from os.path import join
from hashlib import md5

try:
    import html
except ImportError:
    import cgi as html

if sys.version_info < (3, 0):
    import codecs
    # noinspection PyUnresolvedReferences
    # noinspection PyShadowingBuiltins
    chr = unichr
    # noinspection PyShadowingBuiltins
    open = codecs.open


empty_glyph = """<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" 
"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd" >
<svg xmlns="http://www.w3.org/2000/svg" 
xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" viewBox="0 0 512 512">
  <g transform="matrix(1 0 0 -1 0 512)">
   <path fill="currentColor"
d="M0 0z" />
  </g>
</svg>
"""

html_item_template = '''
<div class="item">
    <p class="glyph"><i class="@fontname@">@glyph_name@</i></p>
    <div class="char-info">
        <div class="htmlchar"><code>@glyph_name@</code></div>
    </div>
</div>'''

html_template = '''
<!DOCTYPE html>
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <link rel="stylesheet" type="text/css" 
              href="./css/@fontname@-woff.css" />
        <title>@fontname@ cheatsheet</title>
        <style>
            body{
                background: #FAFAFA;
                text-align: center;
            }
            .item{
                display: inline-block;
                margin: 5px 5px;
                width: 150px;
                height: 165px;
                vertical-align: top;
                text-align: center;
                background-color: #fff;
                box-shadow: 0 1px 2px 0px rgba(0, 0, 0, 0.16),
                            0 0px 0px 1px rgba(0, 0, 0, 0.02);
                border-radius: 2px;
                position: relative;
            }

            .item .glyph{
                font-size: 3em;
                color: #000;
                display: block;
                height: 80px;
                overflow: hidden;
                margin: 0;
                line-height: 2em;
                -moz-user-select: none;
                -webkit-user-select: none;
                user-select: none;
            }
            .item .glyph::selection { background: transparent; }

            i {
                font-size: 1em !important;
            }
            .item .char-info{
                position: absolute;
                bottom:0;
                left:0;
                right:0;
                height: 62px;
            }
            .item .char-info .char, .item .char-info .htmlchar{
                font-size: 18px;
                background-color: #ccc;
                display: inline-block;
                padding: 5px;
                margin: 1px;
                border-radius: 3px
            }

            .item .char-info .htmlchar{
                font-size: 12px;
            }
        </style>
    </head>
    <body>
        <h1>@fontname@ cheatsheet</h1>
        <div style="
            width: 100%;
            border-top: 1px solid rgb(237, 237, 237);
            display:inline-block;
            margin: 0 auto 25px auto;
            clear:both">
        </div>
        @content@
    </body>
</html>
'''

css_template = '''
@font-face {
  font-family: '@fontname@';
  font-style: normal;
  font-weight: 400;
  src: url('../fonts/@fontname@.@format@?@version@') format('@format@');
}
.@fontname@ {
  font-family: '@fontname@';
  font-weight: normal;
  font-style: normal;
  font-size: 24px;
  line-height: 1;
  letter-spacing: normal;
  text-transform: none;
  display: inline-block;
  white-space: nowrap;
  word-wrap: normal;
  direction: ltr;
  font-feature-settings: 'liga';
  text-rendering: optimizeLegibility;
  -webkit-font-feature-settings: 'liga';
  -webkit-font-smoothing: antialiased;
  -moz-font-feature-settings: 'liga';
  -moz-osx-font-smoothing: grayscale;
}'''


class PyWebFontKit:
    _lookup_name = '\'liga\' Standard Ligatures in Latin lookup 0'
    _lookup_subtable_name = \
        '\'liga\' Standard Ligatures in Latin lookup 0 subtable'

    def __init__(self, font_name, kerning=15):
        self.svg_dir = ''
        self.svg_files = []
        self.ttf_path = ''
        self.char_map = {}
        self.char_index = 0xf100
        self.fontforge = fontforge.font()
        self.fontforge.addLookup(
            self._lookup_name, 'gsub_ligature', (),
            (('liga', (('latn', ('dflt',)),)),))
        self.fontforge.addLookupSubtable(
            self._lookup_name,
            self._lookup_subtable_name)
        self.fontforge.encoding = 'UnicodeFull'
        self.fontforge.design_size = 16
        self.fontforge.em = 512
        self.fontforge.ascent = 448
        self.fontforge.descent = 64
        self.fontforge.fontname = font_name
        self.fontforge.familyname = font_name
        self.fontforge.fullname = font_name
        self.fontforge_cache = ''
        self.kerning = kerning
        self.generate_alphabet_glyphs()

    def generate_alphabet_glyphs(self):
        for x in '_abcdefghijklmnopqrstuvwxyz0123456789':
            temp_svg_file = NamedTemporaryFile(suffix='.svg', delete=False)
            temp_svg_file.file.write(str.encode(empty_glyph))
            temp_svg_file.file.close()
            code_point = ord(x)
            if code_point == '_':
                glyph = self.fontforge.createChar(-1, 'underscore')
            else:
                glyph = self.fontforge.createChar(code_point)
            glyph.importOutlines(temp_svg_file.name)
            os.unlink(temp_svg_file.name)

    def load_svg_dir(self, path):
        self.svg_dir = path
        for f in os.listdir(self.svg_dir):
            if os.path.isfile(join(self.svg_dir, f)):
                filename = os.path.splitext(f)[0]
                self.svg_files.append(filename)
        self.svg_files = sorted(self.svg_files)

    def char_add(self, svg_file, glyph_name):
        glyph = self.fontforge.createChar(-1, glyph_name)
        glyph.addPosSub(
            self._lookup_subtable_name,
            tuple(map(
                lambda x: 'underscore' if x == '_' else x,
                glyph_name
            ))
        )
        # Hack removal of <switch> </switch> tags
        svg_file = open(svg_file, 'r+')
        temp_svg_file = NamedTemporaryFile(suffix='.svg', delete=False)
        svg_text = svg_file.read()
        svg_file.seek(0)

        # Replace the <switch> </switch> tags with 'nothing'
        svg_text = svg_text.replace('<switch>', '')
        svg_text = svg_text.replace('</switch>', '')

        temp_svg_file.file.write(str.encode(svg_text))

        svg_file.close()
        temp_svg_file.file.close()

        svg_file = temp_svg_file.name
        # End hack

        # Import the svg file
        glyph.importOutlines(svg_file)

        # Remove temp
        os.unlink(temp_svg_file.name)

        # Set the margins to the vector image
        # glyph.left_side_bearing = self.kerning
        # glyph.right_side_bearing = self.kerning

        # Set glyph size explicitly or automatically depending on autowidth
        glyph.left_side_bearing = 0
        glyph.right_side_bearing = 0
        glyph.round()

        self.char_map[self.char_index] = glyph_name
        self.char_index += 1

    def char_collect(self):
        print("Start collecting glyphs...")
        for idx, glyph in enumerate(self.svg_files):
            print("Add %s glyph..." % glyph)
            svg_path = os.path.join(self.svg_dir, glyph + '.svg')
            self.char_add(svg_path, glyph.replace('-', '_'))
        # resize glyphs [autowidth]
        self.fontforge.autoWidth(0, 0, 512)

    def save_html(self, html_path, font_name):
        print("Build HTML...")
        html_path = html_path
        fonts_list = ''.join(map(lambda x: html_item_template.replace(
            "@glyph_name@", self.char_map[x]
        ), self.char_map))

        template_res = html_template.replace("@content@", fonts_list)
        res = template_res.replace("@fontname@", font_name)
        file = codecs.open(html_path, encoding='utf-8', mode="w")
        file.write(res)
        file.close()

    @staticmethod
    def save_css(css_path, format_, version, font_name):
        print("Build CSS...")
        res = css_template.replace("@version@", version)
        res = res.replace("@format@", format_)
        res = res.replace("@fontname@", font_name)
        file = open(css_path, encoding='utf-8', mode="w")
        file.write(res)
        file.close()

    def save_ttf(self, ttf_path):
        print("Build TTF...")
        self.fontforge.generate(ttf_path)
        self.fontforge_cache = fontforge.open(ttf_path)
        self.optimize_glyphs(self.fontforge_cache)

    def save_otf(self, otf_path):
        print("Build OTF...")
        # noinspection PyUnresolvedReferences
        self.fontforge_cache.generate(otf_path)

    def save_svg(self, svg_path):
        print("Build SVG...")
        # noinspection PyUnresolvedReferences
        self.fontforge_cache.generate(svg_path)
        # Fix SVG header for webkit
        # from: https://github.com/fontello/font-builder
        # /blob/master/bin/fontconvert.py
        svgfile = open(svg_path, 'r+')
        svgtext = svgfile.read()
        svgfile.seek(0)
        svgfile.write(svgtext.replace(
            '<svg>', '<svg xmlns="http://www.w3.org/2000/svg">'
        ))
        svgfile.close()

    def save_eot(self, eot_path):
        print("Build EOT...")
        # noinspection PyUnresolvedReferences
        self.fontforge_cache.generate(eot_path)

    def save_woff(self, woff_path):
        print("Build WOFF...")
        # noinspection PyUnresolvedReferences
        self.fontforge_cache.generate(woff_path)

    @staticmethod
    def optimize_glyphs(fontforge_obj):
        print("+ Unlink references...")
        for glyph in fontforge_obj.glyphs():
            glyph.unlinkRef()

        print("+ Rounding points to int values...")
        for glyph in fontforge_obj.glyphs():
            glyph.round()

        print("+ Removing overlaps...")
        for glyph in fontforge_obj.glyphs():
            # if glyph.unicode in self.char_map:
            #     print("Working %s ..." % self.char_map[glyph.unicode])
            # else:
            #     print("Working unicode(%s) ..." % glyph.unicode)
            glyph.removeOverlap()

        print("+ Adding extrema...")
        for glyph in fontforge_obj.glyphs():
            glyph.addExtrema()

        print("+ Simplifying...")
        for glyph in fontforge_obj.glyphs():
            glyph.simplify()

        print("+ Correcting directions...")
        for glyph in fontforge_obj.glyphs():
            glyph.correctDirection()

    @staticmethod
    def main(font_name, working_dir=None):
        try:
            bundles_dir_path = join(working_dir, 'bundles')
            bundle_dir_path = join(bundles_dir_path, font_name)

            svg_dir_path = join(bundle_dir_path, 'svg')
            html_path = join(bundle_dir_path, font_name + '.html')
            css_dir_path = join(bundle_dir_path, 'css')
            font_dir_path = join(bundle_dir_path, 'fonts')

            # Make directories
            for dir_path in (bundles_dir_path, bundle_dir_path, svg_dir_path,
                             css_dir_path, font_dir_path):
                try:
                    os.makedirs(dir_path)
                except OSError:
                    pass

            # Main
            app = PyWebFontKit(font_name=font_name)
            app.load_svg_dir(svg_dir_path)
            app.char_collect()
            for format_ in ('ttf', 'woff', 'otf', 'svg', 'eot'):
                file_path = join(font_dir_path, '%s.%s' % (font_name, format_))
                getattr(app, 'save_%s' % format_)(file_path)
                with open(file_path) as file_to_check:
                    version = md5(file_to_check.read()).hexdigest()
                css_file_path = join(
                    css_dir_path,
                    '%s-%s.css' % (font_name, format_)
                )
                app.save_css(css_file_path, format_, version, font_name)

            app.save_html(html_path, font_name)

        except KeyboardInterrupt:
            print('Force exit, Keyboard interrupt!')


def main():
    # Define options
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', help='Font name', nargs='*')

    args = parser.parse_args()
    if args.f is not None:
        PyWebFontKit.main(
            font_name=args.f[0],
            working_dir=os.getcwd()
        )
    else:
        parser.print_help()


if __name__ == '__main__':
    main()

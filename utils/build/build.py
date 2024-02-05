#!/usr/bin/env python3

import os
import tempfile
import sys
import subprocess

HTML = [
'standalone/pannellum.htm'
]

def merge(files):
    buffer = []
    for filename in files:
        with open(os.path.join('../..', 'src', filename), 'r') as f:
            buffer.append(f.read())
    return "".join(buffer)

def read(filename):
    with open(os.path.join('../..','src',filename), 'r') as f:
        return f.read()

def output(text, filename):
    with open(os.path.join('../..', 'build', filename), 'w') as f:
        f.write(text)

def JScompress(path):
    out_tuple = tempfile.mkstemp()
    os.system("pnpm esbuild --bundle --minify %s > %s" % (path, out_tuple[1]))
    with os.fdopen(out_tuple[0], 'r') as handle:
        compressed = handle.read()
    os.unlink(out_tuple[1])
    return compressed

def cssCompress(path):
    out_tuple = tempfile.mkstemp()
    os.system("pnpm esbuild %s --minify > %s" % (path, out_tuple[1]))
    with os.fdopen(out_tuple[0], 'r') as handle:
        compressed = handle.read()
    os.unlink(out_tuple[1])
    return compressed

def addHeaderHTML(text, version):
    text = text.replace('<!DOCTYPE HTML>','');
    header = '<!DOCTYPE HTML>\n<!-- Pannellum ' + version + ', https://github.com/mpetroff/pannellum -->\n'
    return header + text

def build(html, filename, release=False):
    folder = ''
    os.makedirs('./build', exist_ok=True)

    htmlfilename = filename + '.htm'

    if release:
        version = read('./VERSION').strip()
    else:
        if os.path.exists('.git'):
            version = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('utf-8').strip()
        else:
            print('No .git folder detected, setting version to testing')
            version = "testing"

    standalone_js = JScompress('./src/standalone/standalone.js')
    standalone_css = cssCompress('./src/standalone/standalone.css')

    print('=' * 40)
    print('Compiling', htmlfilename)
    print('=' * 40)
    
    html = merge(html)
    html = html.replace('<link type="text/css" rel="Stylesheet" href="../css/pannellum.css"/>','<style type="text/css">' + standalone_css + '</style>')
    html = html.replace('<script type="text/javascript" src="../js/libpannellum.js"></script>','')
    html = html.replace('<script type="text/javascript" src="../js/pannellum.js"></script>','<script type="text/javascript">' + standalone_js + '</script>')
    html = html.replace('<script type="text/javascript" src="standalone.js"></script>','')
    html = html.replace('<link type="text/css" rel="Stylesheet" href="standalone.css"/>', '')
    
    output(addHeaderHTML(html, version), folder + htmlfilename)

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))  # cd to script dir
    if (len(sys.argv) > 1 and sys.argv[1] == 'release'):
        build(HTML, 'pannellum', True)
    else:
        build(HTML, 'pannellum')

if __name__ == "__main__":
    main()

"""Fast repo guardrail: Python lint, syntax, worker safety, JavaScript, and unit tests."""
import ast
import importlib.util
import re
import subprocess
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def worker_violations(tree):
    errors=[]
    for node in ast.walk(tree):
        if not isinstance(node,ast.Call): continue
        if ast.unparse(node.func)=='bpy.data.libraries.write':
            errors.append((node.lineno,'bpy.data.libraries.write is unsupported by the pinned Blender runtime'))
        if ast.unparse(node.func)=='subprocess.run' and node.args and isinstance(node.args[0],(ast.List,ast.Tuple)):
            values=[item.value if isinstance(item,ast.Constant) else None for item in node.args[0].elts]
            if '--python' in values and not any(values[i:i+2]==['--python-exit-code','1'] for i in range(len(values)-1)):
                errors.append((node.lineno,'Blender Python workers must fail with --python-exit-code 1'))
    return errors


class Scripts(HTMLParser):
    def __init__(self):
        super().__init__(); self.inline=False; self.scripts=[]

    def handle_starttag(self,tag,attrs):
        if tag=='script':
            attrs=dict(attrs)
            self.inline='src' not in attrs and attrs.get('type','') in ('','module','text/javascript')

    def handle_endtag(self,tag):
        if tag=='script': self.inline=False

    def handle_data(self,data):
        if self.inline: self.scripts.append(data)


def main():
    requirement=(ROOT/'requirements-checks.txt').read_text().strip()
    ruff=([sys.executable,'-m','ruff'] if importlib.util.find_spec('ruff')
          else ['uvx','--from',requirement,'ruff'])
    subprocess.run([*ruff,'check','tools'],cwd=ROOT,check=True)
    scripts=[]
    for path in sorted((ROOT/'tools').rglob('*.py')):
        source=path.read_text(); tree=ast.parse(source,filename=str(path))
        compile(tree,str(path),'exec')
        errors=worker_violations(tree)
        if errors: raise RuntimeError(f'{path.relative_to(ROOT)}: {errors}')
        for node in ast.walk(tree):
            if isinstance(node,ast.Assign) and isinstance(node.value,ast.Constant) and isinstance(node.value.value,str):
                html=node.value.value
                if '<script' not in html: continue
                parser=Scripts(); parser.feed(html)
                scripts.extend((str(path.relative_to(ROOT)),script) for script in parser.scripts)
    for path in [ROOT/'catalog/catalog.js',ROOT/'tools/asset_catalog/browser_checks.js']:
        subprocess.run(['node','--check',str(path)],check=True,capture_output=True,text=True)
    with tempfile.TemporaryDirectory() as directory:
        for index,(source,script) in enumerate(scripts):
            script=re.sub(r'__(?:ASSETS|ASSET_DATA)__','[]',script).replace('__VALIDATION__','false')
            path=Path(directory)/f'inline-{index}.js';path.write_text(script)
            result=subprocess.run(['node','--check',str(path)],capture_output=True,text=True)
            if result.returncode: raise RuntimeError(f'{source}: {result.stderr}')
    modules=['.'.join(path.relative_to(ROOT).with_suffix('').parts)
             for path in sorted((ROOT/'tools').rglob('test_*.py')) if not path.name.endswith('_blender.py')]
    result=unittest.TextTestRunner(verbosity=1).run(unittest.defaultTestLoader.loadTestsFromNames(modules))
    if not result.wasSuccessful(): raise RuntimeError('Unit tests failed')
    print(f'Fast checks passed; {result.testsRun} tests and {len(scripts)} inline JavaScript programs')


if __name__=='__main__': main()

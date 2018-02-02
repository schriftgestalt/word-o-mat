import re
import sys

def _run(script):
    global __file__
    import os
    import site  # noqa: F401
    sys.frozen = 'macosx_plugin'
    base = os.environ['RESOURCEPATH']

    __file__ = path = os.path.join(base, script)
    if sys.version_info[0] == 2:
        with open(path, 'rU') as fp:
            source = fp.read() + "\n"
    else:
        with open(path, 'r', encoding='utf-8') as fp:
            source = fp.read() + '\n'

        BOM = b'\xef\xbb\xbf'.decode('utf-8')

        if source.startswith(BOM):
            source = source[1:]

    exec(compile(source, script, 'exec'), globals(), globals())

try:
    _run('plugin.py')
except KeyboardInterrupt:
    pass

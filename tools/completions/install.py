#!/usr/bin/env python3
"""Install only publish-writeup completion, preserving existing compinit setup."""
import os
from pathlib import Path
import shutil
from datetime import datetime

home = Path.home()
rc = home / '.zshrc'
source = Path(__file__).resolve().with_name('_publish-writeup')
target = home / '.local/share/zsh/site-functions/_publish-writeup'
marker = '# BEGIN publish-writeup completion'
block = '''# BEGIN publish-writeup completion
fpath=("$HOME/.local/share/zsh/site-functions" $fpath)
autoload -Uz _publish-writeup
# Explicit registration also works with an existing cached compinit dump.
compdef _publish-writeup publish-writeup
# END publish-writeup completion
'''
if rc.is_symlink() or target.is_symlink():
    raise SystemExit('Refusing to replace a symlink; review installation manually.')
text = rc.read_text()
if marker in text:
    if text.count(block) != 1:
        raise SystemExit('Existing completion block differs; review it manually.')
elif '\ncompinit ' not in text and '\ncompinit\n' not in text:
    raise SystemExit('No existing compinit found; initialize Zsh completion first.')
else:
    backup = rc.with_name('.zshrc.publish-writeup.' + datetime.now().strftime('%Y%m%d-%H%M%S-%f') + '.bak')
    shutil.copy2(rc, backup)
    print(f'Backup: {backup}')
    with rc.open('a') as stream:
        stream.write('\n' + block)
target.parent.mkdir(parents=True, exist_ok=True)
shutil.copyfile(source, target)
os.chmod(target, 0o644)
print(f'Installed: {target}')

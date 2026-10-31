#!/usr/bin/env python3
"""Exercise real ZLE Tab completion in an isolated PTY; never execute input."""
import os
from pathlib import Path
import pty
import select
import shlex
import subprocess
import tempfile
import time

source = Path(__file__).resolve().with_name('_publish-writeup')
with tempfile.TemporaryDirectory(prefix='publish-completion-') as tmp:
    root = Path(tmp)
    vault = root / 'Custom Vault [test]'
    notes = ['TryHackMe/Challenge/Dead Drop.md',
             'TryHackMe/Challenge/Question?.md',
             "TryHackMe/Challenge/O'Brien [1].md",
             'TryHackMe/Holiday Challenge/Other.md']
    for note in notes:
        path = vault / note
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
    (vault / 'TryHackMe/Challenge/ignore.txt').touch()
    repo = vault / 'Site'
    repo.mkdir()
    (repo / 'private.md').touch()
    result = root / 'buffer'
    setup = root / 'setup.zsh'
    setup.write_text(f'''autoload -Uz compinit
compinit -D
fpath=({shlex.quote(str(source.parent))} $fpath)
autoload -Uz _publish-writeup
compdef _publish-writeup publish-writeup
zstyle ':completion:*' completer _complete
bindkey -e
bindkey '^I' complete-word
capture() {{ print -r -- "$BUFFER" > {shlex.quote(str(result))}; BUFFER=''; zle reset-prompt }}
zle -N capture
bindkey '^X^X' capture
PS1='READY> '
''')
    master, slave = pty.openpty()
    env = dict(os.environ, TERM='xterm', OBSIDIAN_VAULT=str(vault), CHIRPY_REPO=str(repo))
    child = subprocess.Popen(['zsh', '-f'], stdin=slave, stdout=slave, stderr=slave, env=env)
    os.close(slave)
    def drain(seconds=0.2):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            if select.select([master], [], [], 0.02)[0]:
                os.read(master, 65536)
    try:
        os.write(master, ('source ' + shlex.quote(str(setup)) + '\n').encode())
        drain(1)
        cases = [
            ('--de', '--deploy'), ('--wr', '--write'),
            ('TryHackMe/Chal', 'TryHackMe/Challenge/'),
            ('TryHackMe/Challenge/Dea', notes[0]),
            ('TryHackMe/Challenge/Que', notes[1]),
            ('TryHackMe/Challenge/O', notes[2]),
            ('--folder TryHackMe/Hol', 'TryHackMe/Holiday Challenge/'),
            ('--folder TryHackMe/Challenge/ig', 'TryHackMe/Challenge/ig'),
            ('--batch TryHackMe/Challenge/Dea', notes[0]),
            ('--batch "' + notes[0] + '" TryHackMe/Challenge/Que', notes[1]),
            ('"TryHackMe/Challenge/Dea', notes[0]),
            ("'TryHackMe/Challenge/Que", notes[1]),
            ('TryHackMe/Holiday\\ Ch', 'TryHackMe/Holiday Challenge/'),
        ]
        for text, expected in cases:
            result.unlink(missing_ok=True)
            os.write(master, ('publish-writeup ' + text + '\t').encode())
            drain()
            os.write(master, b'\x18\x18')
            drain()
            buffer = result.read_text().rstrip('\n')
            try:
                actual = shlex.split(buffer)[-1]
            except ValueError:
                quote = text[0]
                actual = shlex.split(buffer + quote)[-1]
            assert actual == expected, (text, actual, expected)
            print('PASS:', text)
    finally:
        child.kill()
        child.wait(timeout=5)
        os.close(master)

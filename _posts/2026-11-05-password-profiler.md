---
title: "Password Profiler"
date: 2026-11-05 14:04:41 +0700
categories: ["CyLab(picoCTF)", "General Skill"]
tags: ["easy", "general-skills"]
description: "We intercepted a suspicious file from a system, but instead of the password itself, it only contains its SHA-1 hash. Using OSINT techniques, you are provided with personal details about the target. Your task is to leverage this information to generate a custom password list and recover the original password by matching its hash.\n\nDownload the following files:\n\nuserinfo: Contains the personal details.\n\nhash: Contains the SHA-1 hash of the password.\n\ncheck_password: Script to test passwords against the hash."
toc: true
comments: false
---

![image-775](/assets/img/obsidian/password-profiler/image-775.png)

Download all the files.

![image-1715](/assets/img/obsidian/password-profiler/image-1715.png)

![image-1716](/assets/img/obsidian/password-profiler/image-1716.png)

![image-1718](/assets/img/obsidian/password-profiler/image-1718.png)

```python
#!/usr/bin/env python3

import hashlib

  

HASH_FILE = "hash.txt"

WORDLIST_FILE = "passwords.txt" # wordlist that was generated using CUPP

  

def load_hash():

with open(HASH_FILE, "r") as f:

return f.read().strip()

  

def crack_password(target_hash):

with open(WORDLIST_FILE, "r", encoding="utf-8", errors="ignore") as f:

for password in f:

password = password.strip()

if hashlib.sha1(password.encode()).hexdigest() == target_hash:

return password

return None

  

if __name__ == "__main__":

target_hash = load_hash()

result = crack_password(target_hash)

if result:

print(f"Password found: picoCTF{% raw %}{{{result}}}{% endraw %}")

else:

print("No match found.")
```

The challenge required a custom password wordlist based on the user's information.

Use `cupp` to create a custom wordlist from the available information.

CUPP combines the supplied personal details into likely password candidates. The Python script hashes each candidate with SHA-1 and compares it with `hash.txt`; a matching hash identifies the password.

`cupp -i`

![image-1721](/assets/img/obsidian/password-profiler/image-1721.png)
Enter the available information.

![image-1722](/assets/img/obsidian/password-profiler/image-1722.png)

After generating the wordlist, rename it to `passwords.txt` and run `check_password.py` to get the flag!

---

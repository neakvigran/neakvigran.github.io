---
title: "SUDO MAKE ME A SANDWICH"
date: 2026-08-22
categories: ["CyLab(picoCTF)", "General Skill"]
tags: ["easy", "general-skills"]
description: "Can you read the flag? I think you can!\n\nssh -p 59861 ctf-player@green-hill.picoctf.net using password f7e73aca"
toc: true
comments: false
---

![image-1706](/assets/img/obsidian/sudo-make-me-a-sandwich/image-1706.png)

Connect with `ssh -p 59861 ctf-player@green-hill.picoctf.net` and use the password `f7e73aca`.


![image-1707](/assets/img/obsidian/sudo-make-me-a-sandwich/image-1707.png)

![image-1708](/assets/img/obsidian/sudo-make-me-a-sandwich/image-1708.png)

Only root can read `flag.txt`. Use `sudo -l` to check which commands your user can run with elevated privileges.
![image-1710](/assets/img/obsidian/sudo-make-me-a-sandwich/image-1710.png)

The sudo rules allow you to run the text editor `emacs` without a password (`NOPASSWD`). Run `sudo emacs flag.txt` to read the flag!

![image-1711](/assets/img/obsidian/sudo-make-me-a-sandwich/image-1711.png)

---

---
title: "Magikarp Ground Mission"
date: 2026-11-05 14:04:40 +0700
categories: ["CyLab(picoCTF)", "General Skill"]
tags: ["easy", "general-skills"]
description: "Do you know how to move between directories and read files in the shell? Start the container, ssh to it, and then ls once connected to begin.\n\nLogin via ssh as ctf-player with the password, 8c606eb1 on the host wily-courier.picoctf.net and port 49770."
toc: true
comments: false
---

![image-1595](/assets/img/obsidian/magikarp-ground-mission/image-1595.png)

Connect with `ssh ctf-player@wily-courier.picoctf.net -p 49770`.


![image-1596](/assets/img/obsidian/magikarp-ground-mission/image-1596.png)

This reveals the first third of the flag.

Read the instruction files to locate the remaining pieces. `cd /` moves to the filesystem root, while `cd ~` returns to your home directory; read the numbered flag files in those locations and combine their contents in order.

![image-1597](/assets/img/obsidian/magikarp-ground-mission/image-1597.png)

![image-1598](/assets/img/obsidian/magikarp-ground-mission/image-1598.png)

These are the second and third parts. Combine all three to complete the flag!

`picoCTF{xxsh_0ut_0f_//4t3r_0b24fc4f}`

---


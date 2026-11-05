---
title: "First Find"
date: 2026-11-05 14:04:40 +0700
categories: ["CyLab(picoCTF)", "General Skill"]
tags: ["easy", "general-skills"]
description: "Unzip this archive and find the file named 'uber-secret.txt'"
toc: true
comments: false
---

![image-1599](/assets/img/obsidian/first-find/image-1599.png)

Download the file.

Extract the archive, then run `find . -type f -name "uber-secret.txt"` from the extracted directory. Here, `.` starts a recursive search, `-type f` restricts matches to files, and `-name` selects the target filename. Use `cat` on the returned path to read the flag.

![image-1601](/assets/img/obsidian/first-find/image-1601.png)

---

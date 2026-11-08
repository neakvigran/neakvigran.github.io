---
title: "First Grep"
date: 2026-08-14
categories: ["CyLab(picoCTF)", "General Skill"]
tags: ["easy", "general-skills"]
description: "Can you find the flag in the file? This would be really tedious to look through manually, something tells me there is a better way.\n\nThe flag is in this file."
toc: true
comments: false
---

![image-1534](/assets/img/obsidian/first-grep/image-1534.png)

Use `cat file | grep picoCTF` to find the flag.

The pipe (`|`) passes the file contents to `grep`, which prints lines containing `picoCTF`. This isolates the flag from the surrounding text.

![image-1535](/assets/img/obsidian/first-grep/image-1535.png)

---

---
title: "strings it"
date: 2026-07-18
categories: ["CyLab(picoCTF)", "General Skill"]
tags: ["easy", "general-skills"]
description: "Can you find the flag in file without running it?"
toc: true
comments: false
---

![image-1532](/assets/img/obsidian/strings-it/image-1532.png)

Try the `strings` command.

`strings` extracts printable character sequences from a binary file. Pipe the result to `grep -i picoCTF` to find the flag prefix; `-i` makes the search case-insensitive.

![image-1533](/assets/img/obsidian/strings-it/image-1533.png)

---

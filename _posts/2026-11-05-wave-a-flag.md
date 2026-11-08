---
title: "Wave a flag"
date: 2026-07-06
categories: ["CyLab(picoCTF)", "General Skill"]
tags: ["easy", "general-skills"]
description: "Can you invoke help flags for a tool or binary? This program has extraordinarily helpful information..."
toc: true
comments: false
---

![image-1518](/assets/img/obsidian/wave-a-flag/image-1518.png)

![image-1519](/assets/img/obsidian/wave-a-flag/image-1519.png)

Grant execute permission before running the file.

![image-1520](/assets/img/obsidian/wave-a-flag/image-1520.png)

Use `chmod +x warm` and run it with `./warm`.

![image-1521](/assets/img/obsidian/wave-a-flag/image-1521.png)

The output asks for `-h`, a common help option. Run `./warm -h` to display the help message, which contains the flag in this challenge.

![image-1522](/assets/img/obsidian/wave-a-flag/image-1522.png)

---

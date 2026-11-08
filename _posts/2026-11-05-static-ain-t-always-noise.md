---
title: "Static ain't always noise"
date: 2026-07-02
categories: ["CyLab(picoCTF)", "General Skill"]
tags: ["easy", "general-skills"]
description: "Can you look at the data in this binary? The bash script might help!"
toc: true
comments: false
---

![image-1602](/assets/img/obsidian/static-ain-t-always-noise/image-1602.png)

Download all the files.

![image-1604](/assets/img/obsidian/static-ain-t-always-noise/image-1604.png)

Find the flag with `strings static | grep "picoCTF"`.

`strings` extracts printable text from the executable, while `grep` selects lines containing the flag prefix. This examines data stored in the binary without running it.

![image-1605](/assets/img/obsidian/static-ain-t-always-noise/image-1605.png)

Alternatively, use the `ltdis.sh` script with the `static` file.

This produced the following output:
![image-1606](/assets/img/obsidian/static-ain-t-always-noise/image-1606.png)

![image-1607](/assets/img/obsidian/static-ain-t-always-noise/image-1607.png)

The output reveals the flag!

---



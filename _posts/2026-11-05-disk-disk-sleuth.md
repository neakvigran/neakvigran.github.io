---
title: "Disk,disk,sleuth!"
date: 2026-07-19
categories: ["CyLab(picoCTF)", "Forensics"]
tags: ["medium", "forensics"]
description: "Use srch_strings from the sleuthkit and some terminal-fu to find a flag in this disk image."
toc: true
comments: false
---

![image-1643](/assets/img/obsidian/disk-disk-sleuth/image-1643.png)

Download the file and decompress it with `gunzip`.
Then use `srch_strings` with `grep picoCTF` to find the flag.

`srch_strings` extracts readable text from the disk image, and `grep` keeps lines containing the flag prefix. This can reveal plaintext stored in the image without mounting its filesystem.

![image-1644](/assets/img/obsidian/disk-disk-sleuth/image-1644.png)

---

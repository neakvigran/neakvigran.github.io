---
title: "Information"
date: 2026-11-05 14:04:39 +0700
categories: ["CyLab(picoCTF)", "Forensics"]
tags: ["easy", "forensics"]
description: "Files can always be changed in a secret way. Can you find the flag?"
toc: true
comments: false
---

![image-1638](/assets/img/obsidian/information/image-1638.png)

Download `cat.jpg`.

![image-1637](/assets/img/obsidian/information/image-1637.png)

Use `exiftool` to inspect the file's metadata.

The **License** field appeared to be Base64-encoded.

Use `base64 -d` to decode it and get the flag!

---

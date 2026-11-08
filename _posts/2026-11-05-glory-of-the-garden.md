---
title: "Glory of the Garden"
date: 2026-07-23
categories: ["CyLab(picoCTF)", "Forensics"]
tags: ["easy", "forensics"]
description: "This file contains more than it seems.\n\nGet the flag from garden.jpg."
toc: true
comments: false
---

![image-1639](/assets/img/obsidian/glory-of-the-garden/image-1639.png)

Download `garden.jpg`.

Use the `strings` command to reveal the flag!

An image file can contain readable text alongside its image data. `strings` extracts printable character sequences, exposing the flag without needing to interpret the pixels.

![image-1640](/assets/img/obsidian/glory-of-the-garden/image-1640.png)

---
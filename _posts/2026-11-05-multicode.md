---
title: "Multicode"
date: 2026-08-05
categories: ["CyLab(picoCTF)", "General Skill"]
tags: ["easy", "general-skills"]
description: "We intercepted a suspiciously encoded message, but it’s clearly hiding a flag. No encryption, just multiple layers of obfuscation. Can you peel back the layers and reveal the truth?\n\nDownload the message."
toc: true
comments: false
---

![image-1777](/assets/img/obsidian/multicode/image-1777.png)

Download `message.txt`.

![image-1778](/assets/img/obsidian/multicode/image-1778.png)

The text looks like Base64, so decode it with CyberChef.

![image-1779](/assets/img/obsidian/multicode/image-1779.png)

The result looks like hexadecimal values, so decode it from hexadecimal.

![image-1780](/assets/img/obsidian/multicode/image-1780.png)

The decoded text contains percent-encoded sequences, so apply URL decoding next.

![image-1781](/assets/img/obsidian/multicode/image-1781.png)

The result resembles a flag, but the letters are shifted. Try different rotation values to recover the flag.

![image-1782](/assets/img/obsidian/multicode/image-1782.png)


A rotation of 13 (ROT13) reveals the flag.

---

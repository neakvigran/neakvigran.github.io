---
title: "interencdec"
date: 2026-08-08
categories: ["CyLab(picoCTF)", "Cryptography"]
tags: ["easy", "cryptography"]
description: "Can you get the real meaning from this file.\n\nDownload the file here."
toc: true
comments: false
---

![image-1614](/assets/img/obsidian/interencdec/image-1614.png)

Download the file.
![image-1616](/assets/img/obsidian/interencdec/image-1616.png)

The text in the file ends with `=`, which suggests Base64 padding. Use `base64 -d` to decode it.

![image-1615](/assets/img/obsidian/interencdec/image-1615.png)

The result looks like Base64 again, so run `base64 -d` a second time.

![image-1617](/assets/img/obsidian/interencdec/image-1617.png)

The result now resembled a flag, but it appeared to need Caesar cipher decryption.

Enter it into `https://www.dcode.fr/caesar-cipher`.

![image-1618](/assets/img/obsidian/interencdec/image-1618.png)

to get the flag!

`picoCTF{caesar_d3cr9pt3d_f0212758}`

---

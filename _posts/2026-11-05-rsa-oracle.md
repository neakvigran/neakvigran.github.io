---
title: "rsa_oracle"
date: 2026-07-26
categories: ["CyLab(picoCTF)", "Cryptography"]
tags: ["medium", "cryptography"]
description: "Can you abuse the oracle?\n\nAn attacker was able to intercept communications between a bank and a fintech company. They managed to get the message (ciphertext) and the password that was used to encrypt the message."
toc: true
comments: false
---

![image-1631](/assets/img/obsidian/rsa-oracle/image-1631.png)

![image-1632](/assets/img/obsidian/rsa-oracle/image-1632.png)

The files serve different purposes: `password.enc` contains an RSA-encrypted password, while `secret.enc` contains the encrypted message. The oracle offers encryption and decryption operations, as the sample round trip with `a` shows.

`nc titan.picoctf.net 59179`

![image-1634](/assets/img/obsidian/rsa-oracle/image-1634.png)![image-1633](/assets/img/obsidian/rsa-oracle/image-1633.png)

![image-1635](/assets/img/obsidian/rsa-oracle/image-1635.png)

The script output shows the recovered password as `60f50`. Use it with the OpenSSL AES-256-CBC decryption command shown below to read `secret.enc`. The recovery script itself is not included in this note, so the intermediate RSA manipulation is not documented here.

![image-1636](/assets/img/obsidian/rsa-oracle/image-1636.png)
Got the flag!

---
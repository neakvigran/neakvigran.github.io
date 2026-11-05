---
title: "where are the robots"
date: 2026-11-05 14:04:44 +0700
categories: ["CyLab(picoCTF)", "Web Exploitation"]
tags: ["easy", "web-exploitation"]
description: "Can you find the robots?\n\nhttp://fickle-tempest.picoctf.net:52070"
toc: true
comments: false
---

![image-1536](/assets/img/obsidian/where-are-the-robots/image-1536.png)

Open the website.
![image-1537](/assets/img/obsidian/where-are-the-robots/image-1537.png)

Navigate to `/robots.txt`.

`robots.txt` tells web crawlers which paths they should avoid. Its entries are publicly readable, so a `Disallow` entry can reveal a path worth checking; it does not prevent direct access to that path.

![image-1538](/assets/img/obsidian/where-are-the-robots/image-1538.png)

The file reveals a hidden directory.

![image-1539](/assets/img/obsidian/where-are-the-robots/image-1539.png)

Here is the flag!

---

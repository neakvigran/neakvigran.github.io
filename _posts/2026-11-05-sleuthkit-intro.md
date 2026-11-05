---
title: "Sleuthkit Intro"
date: 2026-11-05 14:04:39 +0700
categories: ["CyLab(picoCTF)", "Forensics"]
tags: ["medium", "forensics"]
description: "Download the disk image and use mmls on it to find the size of the Linux partition. Connect to the remote checker service to check your answer and get the flag.\n\nNote: if you are using the webshell, download and extract the disk image into /tmp not your home directory.\n\nAccess checker program: nc saturn.picoctf.net 53218"
toc: true
comments: false
---

![image-1642](/assets/img/obsidian/sleuthkit-intro/image-1642.png)

![image-1641](/assets/img/obsidian/sleuthkit-intro/image-1641.png)

Run `mmls disk.img` to inspect the partition table. The Linux partition has a **Length** of `202752` sectors in the screenshot; submit that value to the checker. Use the Length column rather than the Start or End column, since the question asks for the partition size in sectors. See the [mmls manual](https://www.sleuthkit.org/sleuthkit/man/mmls.html)

---
---
title: "Disk,disk,sleuth2"
date: 2026-11-05 14:04:38 +0700
categories: ["CyLab(picoCTF)", "Forensics"]
tags: ["medium", "forensics"]
description: "All we know is the file with the flag is named down-at-the-bottom.txt..."
toc: true
comments: false
---

![image-1646](/assets/img/obsidian/disk-disk-sleuth2/image-1646.png)

Download and extract the file.

![image-1647](/assets/img/obsidian/disk-disk-sleuth2/image-1647.png)

Use `mmls` to check the partition start offsets.

Then use `fls` to find `down-at-the-bottom.txt`.

![image-1649](/assets/img/obsidian/disk-disk-sleuth2/image-1649.png)

After finding the file, use `icat` to extract its contents.

`fls` lists filenames and their metadata addresses; `icat` uses the selected address to read the file. Supply the partition start sector with `-o` so the tools inspect the correct filesystem. See the [icat manual](https://www.sleuthkit.org/sleuthkit/man/icat.html).

![image-1650](/assets/img/obsidian/disk-disk-sleuth2/image-1650.png)

Here is the flag!

`picoCTF{f0r3ns1c4t0r_n0v1c3_4bd721f2}`

---
---
title: "Sleuthkit Apprentice"
date: 2026-07-07
categories: ["CyLab(picoCTF)", "Forensics"]
tags: ["medium", "forensics"]
description: "Download this disk image and find the flag.\n\nNote: if you are using the webshell, download and extract the disk image into /tmp not your home directory."
toc: true
comments: false
---

![image-1651](/assets/img/obsidian/sleuthkit-apprentice/image-1651.png)

Download and extract the file.

![image-1652](/assets/img/obsidian/sleuthkit-apprentice/image-1652.png)

Use `mmls` to inspect the partitions.

There are two partitions to investigate further, starting at offsets 2048 and 360448.

Use the following `fls` command to look for the flag in both partitions. The second partition contains `flag.txt`:

```bash
fls -o 360448 -r -d disk.flag.img 
```

This command recursively lists deleted files.

![image-1653](/assets/img/obsidian/sleuthkit-apprentice/image-1653.png)

Trying `icat` on this entry returned no content.

![image-1654](/assets/img/obsidian/sleuthkit-apprentice/image-1654.png)

The `realloc` marker suggests that the file's metadata entry has been reallocated. Continue searching for other flag files.

![image-1655](/assets/img/obsidian/sleuthkit-apprentice/image-1655.png)

Search for the pattern `flag`. The results include a promising file named `flag.uni.txt`.

![image-1656](/assets/img/obsidian/sleuthkit-apprentice/image-1656.png)

Use `icat` to extract this file's contents to get the flag!

---

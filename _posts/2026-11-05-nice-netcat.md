---
title: "Nice netcat..."
date: 2026-08-28
categories: ["CyLab(picoCTF)", "General Skill"]
tags: ["easy", "general-skills"]
description: "There is a nice program that you can talk to by using this command in a shell:\n$ nc wily-courier.picoctf.net 53695, but it doesn't speak English..."
toc: true
comments: false
---

![image-1591](/assets/img/obsidian/nice-netcat/image-1591.png)

Connect with `nc wily-courier.picoctf.net 53695`.

![image-1592](/assets/img/obsidian/nice-netcat/image-1592.png)

The service returned decimal numbers.

These numbers appear to represent ASCII characters. Convert them to text.

Save the decimal values in `to_ascii.txt`, one per line, for the script below. The inner `printf` converts each number to octal, and the outer `printf` interprets that octal escape as a character.

```bash
#!/bin/bash

  

while read -r n; do

printf "\\$(printf '%03o' "$n")"

done < to_ascii.txt

echo
```

Run this script to get the flag!

![image-1593](/assets/img/obsidian/nice-netcat/image-1593.png)

---

---
title: "IntroToBurp"
date: 2026-07-24
categories: ["CyLab(picoCTF)", "Web Exploitation"]
tags: ["easy", "web-exploitation"]
description: "Try here to find the flag"
toc: true
comments: false
---

![image-1739](/assets/img/obsidian/introtoburp/image-1739.png)

![image-1740](/assets/img/obsidian/introtoburp/image-1740.png)

Use Burp Suite to intercept the request. The POST request includes an OTP in its body. Removing the OTP from the request body bypassed the check in this challenge.

![image-1742](/assets/img/obsidian/introtoburp/image-1742.png)


This gives you access to `/dashboard`.

![image-1741](/assets/img/obsidian/introtoburp/image-1741.png)

*DONE!!*

---

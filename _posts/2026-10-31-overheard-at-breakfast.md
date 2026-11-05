---
title: "Overheard at Breakfast"
date: 2026-10-31 20:49:22 +0700
categories: ["TryHackMe", "Holiday Challenge"]
tags: ["tryhackme"]
description: "Two strangers. One conversation. One profile they never meant to reveal."
toc: true
comments: false
---

![image-1409](/assets/img/obsidian/overheard-at-breakfast/image-1409.png)

# Scenario

![image-1410](/assets/img/obsidian/overheard-at-breakfast/image-1410.png)

![image-1411](/assets/img/obsidian/overheard-at-breakfast/image-1411.png)

# Question

![image-1412](/assets/img/obsidian/overheard-at-breakfast/image-1412.png)

---

## Inspect file 

After downloading the file and unzipping it, we get an image of a conversation between  **Ponzi** and **Lambo**

![image-1413](/assets/img/obsidian/overheard-at-breakfast/image-1413.png)

![image-1414](/assets/img/obsidian/overheard-at-breakfast/image-1414.png)

This conversation hints at something for us. He mentioned a free tool that starts with `G`, and it allows you to upload a profile and link other media accounts.

and I think this relates to `Gravatar`, which allows platforms to display profile pictures by creating a unique MD5 hash of a user's lowercase email address.

So, all we need to do is create an MD5 hash of Lambo's email `lambobytelotushotel@gmail.com` and use it in the gravatar url.

![image-1415](/assets/img/obsidian/overheard-at-breakfast/image-1415.png)

![image-1416](/assets/img/obsidian/overheard-at-breakfast/image-1416.png)

![image-1417](/assets/img/obsidian/overheard-at-breakfast/image-1417.png)

and we found Lambo's profile

we got this from Lambo's profile as a prize, so let's decode it with base64

![image-1418](/assets/img/obsidian/overheard-at-breakfast/image-1418.png)

and we got the flag!

*DONE!!!*

---

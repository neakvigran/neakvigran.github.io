---
title: "Overheard at Breakfast"
date: 2026-10-31 20:49:22 +0700
categories: ["TryHackMe", "Holiday Challenge"]
tags: ["tryhackme", "web-security"]
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

# Inspect file 

After download file and unzip it contain image of conversation between  Ponzi and Lambo

![image-1413](/assets/img/obsidian/overheard-at-breakfast/image-1413.png)

![image-1414](/assets/img/obsidian/overheard-at-breakfast/image-1414.png)

This conversation hint something to us. He said free tool that start with `G` and it allow to upload profile and link other media account.

and I think this relate to `Gravatar` which allow platform to display profile pictures by creating a unique MD5 hash of a user lowercase email address.

So, all we need to do `lambobytelotushotel@gmail.com` is perform MD5 hash with lambo email and use in gravatar url.

![image-1415](/assets/img/obsidian/overheard-at-breakfast/image-1415.png)

![image-1416](/assets/img/obsidian/overheard-at-breakfast/image-1416.png)

![image-1417](/assets/img/obsidian/overheard-at-breakfast/image-1417.png)

and we found Lambo profile

we got this from Lambo profile as a prize, so let decode with base64

![image-1418](/assets/img/obsidian/overheard-at-breakfast/image-1418.png)

and we got the flag!

*DONE!!!*

---

---
title: "Silent Monitor"
date: 2026-10-31 18:17:37 +0700
categories: ["TryHackMe", "Challenge"]
tags: ["tryhackme"]
description: "Enumerate a running internal service, exploit a vulnerable web application, pivot through the system, and crack your way to root."
toc: true
comments: false
---

![image-1135](/assets/img/obsidian/silent-monitor/image-1135.png)

# Scenario

## Green Lights, Dark Corners

CorpNet's internal network operations centre has been running quietly for years. Monitoring hosts, logging events, and keeping the infrastructure alive. Or so it seems. A tip from a disgruntled contractor suggests that someone on the NOC team has been cutting corners, leaving doors open, and hiding things in places no one thinks to look.

The portal is up. The services show green. The audit log looks clean.

But clean logs can be written by anyone.

Your job is to get in, move through the system, and find out what is really running behind the secret dashboard.

# Questions

![image-1136](/assets/img/obsidian/silent-monitor/image-1136.png)

---

# Reconnaissance


![image-1137](/assets/img/obsidian/silent-monitor/image-1137.png)

![image-1138](/assets/img/obsidian/silent-monitor/image-1138.png)

It show that port 22 (SSH) and 5050 (http) are running, which mean this website use unusually port instead of port 80.

**Check that it access able**
![image-1139](/assets/img/obsidian/silent-monitor/image-1139.png)

`http://10.49.191.80:5050`

![image-1140](/assets/img/obsidian/silent-monitor/image-1140.png)

I try to inspect this page, but since it not have any feature to try on. Next I will try to use gobuster tool to find more pages.

```
gobuster dir -u http://10.49.191.80:5050/ \
-w /usr/share/seclists/Discovery/Web-Content/DirBuster-2007_directory-list-2.3-medium.txt
```

![image-1141](/assets/img/obsidian/silent-monitor/image-1141.png)

I found `/internal` page

![image-1142](/assets/img/obsidian/silent-monitor/image-1142.png)

This seem like a sign in page for the website.

# Burpsuite

Since I gobuster hasn't found any other pages. I will catch the POST request using Burpsuite. And use SQL injection.

I put username `' OR 1==1--` and randomly put password, let's see if it work or not.

![image-1143](/assets/img/obsidian/silent-monitor/image-1143.png)

It worked! Now we login as `netops` user 

![image-1145](/assets/img/obsidian/silent-monitor/image-1145.png)

In the audit log, we can see that attacker already try to attack using SQL injection and Command injection. This show that attacker might already successfully attacked.


`http://10.49.191.80:5050/internal/health`

![image-1144](/assets/img/obsidian/silent-monitor/image-1144.png)

Now, at Host Health page this look like something that we can use command injection

![image-1146](/assets/img/obsidian/silent-monitor/image-1146.png)

![image-1147](/assets/img/obsidian/silent-monitor/image-1147.png)

and from audit log we can see that attacker use `%0a` which mean newline. This mean we may bypass command using same method.

I use Burp suite Repeater to send command injection with the request

![image-1148](/assets/img/obsidian/silent-monitor/image-1148.png)

It worked! So, let's play around and find some thing interesting. 

![image-1150](/assets/img/obsidian/silent-monitor/image-1150.png)

I found `secret.config` file this is interesting, let's see what inside the file.

![image-1151](/assets/img/obsidian/silent-monitor/image-1151.png)

We got the user `syadmin` and its password, Since port 22 (SSH) open let's access to the user using this credential

![image-1152](/assets/img/obsidian/silent-monitor/image-1152.png)

Now we can access to this user

![image-1154](/assets/img/obsidian/silent-monitor/image-1154.png)

And this is the answer for our first question.

Moreover, in backups folder it contain some important information

![image-1155](/assets/img/obsidian/silent-monitor/image-1155.png)

So, `infrastructure.kdbx` is contained backups credential. We will export this file to our machine and crack it using `keepass2john`

![image-1156](/assets/img/obsidian/silent-monitor/image-1156.png)

then:![image-1157](/assets/img/obsidian/silent-monitor/image-1157.png)

![image-1158](/assets/img/obsidian/silent-monitor/image-1158.png)

We got the password: `spring` to open `infrastructure.kdbx` file

I use` keepassxc infrastructure.kdbx ` to open the file
![image-1159](/assets/img/obsidian/silent-monitor/image-1159.png)

And we got root password!

![image-1160](/assets/img/obsidian/silent-monitor/image-1160.png)

# Root

![image-1161](/assets/img/obsidian/silent-monitor/image-1161.png)

![image-1162](/assets/img/obsidian/silent-monitor/image-1162.png)

and here we go! Answer for the last questions!

*DONE!!!*

---

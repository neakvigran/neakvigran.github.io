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

---

## Green Lights, Dark Corners

CorpNet's internal network operations centre has been running quietly for years. Monitoring hosts, logging events, and keeping the infrastructure alive. Or so it seems. A tip from a disgruntled contractor suggests that someone on the NOC team has been cutting corners, leaving doors open, and hiding things in places no one thinks to look.

The portal is up. The services show green. The audit log looks clean.

But clean logs can be written by anyone.

Your job is to get in, move through the system, and find out what is really running behind the secret dashboard.

# Questions

![image-1136](/assets/img/obsidian/silent-monitor/image-1136.png)

---

## Reconnaissance


![image-1137](/assets/img/obsidian/silent-monitor/image-1137.png)

![image-1138](/assets/img/obsidian/silent-monitor/image-1138.png)

It shows that ports **22 (SSH) and 5050 (http)** are running, which means this website uses an unusual port instead of port 80.

**Check that it is accessible**
![image-1139](/assets/img/obsidian/silent-monitor/image-1139.png)

`http://10.49.191.80:5050`

![image-1140](/assets/img/obsidian/silent-monitor/image-1140.png)

I try to inspect this page, but since it doesn't have any features to try, next I will try to use the gobuster tool to find more pages.

```
gobuster dir -u http://10.49.191.80:5050/ \
-w /usr/share/seclists/Discovery/Web-Content/DirBuster-2007_directory-list-2.3-medium.txt
```

![image-1141](/assets/img/obsidian/silent-monitor/image-1141.png)

I found the `/internal` page

![image-1142](/assets/img/obsidian/silent-monitor/image-1142.png)

This seems like a sign-in page for the website.

# Burpsuite

Since `gobuster` hasn't found any other pages, I will catch the `POST` request using `Burpsuite`. And use `SQL injection`.

I put `' OR 1==1--` as the username and put in a random password. Let's see if it works or not.

![image-1143](/assets/img/obsidian/silent-monitor/image-1143.png)

It worked! Now we log in as user `netops` 

![image-1145](/assets/img/obsidian/silent-monitor/image-1145.png)

In the audit log, we can see that an attacker already tried to attack using SQL injection and Command injection. This shows that the attacker might have already successfully attacked.


`http://10.49.191.80:5050/internal/health`

![image-1144](/assets/img/obsidian/silent-monitor/image-1144.png)

---

## Command Injection

Now, on the **Host Health** page, this looks like something where we can use`command injection`

![image-1146](/assets/img/obsidian/silent-monitor/image-1146.png)

![image-1147](/assets/img/obsidian/silent-monitor/image-1147.png)

and from the audit log we can see that the attacker uses `%0a`, which means newline. This means we may bypass the command using the same method.

I use `Burp suite Repeater` to send command injection with the request

![image-1148](/assets/img/obsidian/silent-monitor/image-1148.png)

It worked! So, let's play around and find something interesting. 

![image-1150](/assets/img/obsidian/silent-monitor/image-1150.png)

I found a `secret.config` file. This is interesting, let's see what's inside the file.

![image-1151](/assets/img/obsidian/silent-monitor/image-1151.png)

---

## SSH Access

We got the user `syadmin` and its password. Since port 22 (SSH) is open, let's access the user using these credentials

![image-1152](/assets/img/obsidian/silent-monitor/image-1152.png)

Now we can access this user

![image-1154](/assets/img/obsidian/silent-monitor/image-1154.png)

And this is the answer for our first question.

---

## Crack KeePass

Moreover, the backups folder contains some important information

![image-1155](/assets/img/obsidian/silent-monitor/image-1155.png)

So, `infrastructure.kdbx` contains backup credentials. We will export this file to our machine and crack it using `keepass2john`

![image-1156](/assets/img/obsidian/silent-monitor/image-1156.png)

`keepass2john` extracts the database hash into `hash.txt`. We can then try cracking this hash to find the password for the KeePass file.

then:![image-1157](/assets/img/obsidian/silent-monitor/image-1157.png)

![image-1158](/assets/img/obsidian/silent-monitor/image-1158.png)

We got the password: `spring` to open the `infrastructure.kdbx` file

I use` keepassxc infrastructure.kdbx ` to open the file
![image-1159](/assets/img/obsidian/silent-monitor/image-1159.png)

And we got the root password!

![image-1160](/assets/img/obsidian/silent-monitor/image-1160.png)

# Root

![image-1161](/assets/img/obsidian/silent-monitor/image-1161.png)

I use `su` with the root password we found, and now we are root. Let's find `root.txt` and read it.

![image-1162](/assets/img/obsidian/silent-monitor/image-1162.png)

and here we go! The answer to the last question!

*DONE!!!*

---

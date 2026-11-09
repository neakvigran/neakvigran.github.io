---
title: "Net Sec Challenge"
date: 2026-07-22
categories: ["TryHackMe", "Challenge"]
tags: ["tryhackme"]
description: "Practice the skills you have learned in the Network Security module."
toc: true
comments: false
---

![image-1222](/assets/img/obsidian/net-sec-challenge/image-1222.png)

# Description

Use this challenge to test your mastery of the skills you have acquired in the Network Security module. All the questions in this challenge can be solved using only `nmap`, `telnet`, and `hydra`.

# Questions

![image-1223](/assets/img/obsidian/net-sec-challenge/image-1223.png)

---

## Reconnaissance

Let's use `nmap` to scan for open ports
*What is the highest port number that is open and less than 10,000?*

![image-1224](/assets/img/obsidian/net-sec-challenge/image-1224.png)

**Ans** 
	 Port number 8081

*There is an open port outside the common 1000 ports; it is above 10,100. What is it?*

![image-1225](/assets/img/obsidian/net-sec-challenge/image-1225.png)


**Ans** 
	Port number 10121

*How many TCP ports are open?*

**Ans**  7

---

## Service Banners

 *On port 80, what is the service version value?*

![image-1226](/assets/img/obsidian/net-sec-challenge/image-1226.png)

I use `nmap -sV` on port 80 to check the service response. The HTTP `Server` header contains the value we need.

*What is the flag hidden in the SSH server header?*    

![image-1227](/assets/img/obsidian/net-sec-challenge/image-1227.png)

Same idea for SSH. I check port 22 with service detection, and the flag is inside the server banner.


*We have an FTP server listening on a nonstandard port. What is the version of the FTP server?*
![image-1228](/assets/img/obsidian/net-sec-challenge/image-1228.png)

Since **port 10121** previously showed an unknown service, I assume that this port may use the ftp protocol. I use `nmap -sV -p 10121 ` to check.

**Ans** `vsftpd 3.0.5`


---

## FTP Access

*We learned two usernames using social engineering: **eddie** and **quinn**. What is the flag hidden in one of these two account files and accessible via FTP?* 

Seems like we need to brute-force to find passwords for these two accounts using the hydra tool

`hydra -L users.txt -P /usr/share/wordlists/rockyou.txt ftp://10.48.167.230:10121
`
![image-1229](/assets/img/obsidian/net-sec-challenge/image-1229.png)

Now, let's log in to FTP as `quinn` with the password we found. I list the files and download `ftp_flag.txt` with `get`.

![image-1230](/assets/img/obsidian/net-sec-challenge/image-1230.png)

find `ftp_flag.txt` in the **quinn** account

![image-1231](/assets/img/obsidian/net-sec-challenge/image-1231.png)

---

## NULL Scan

*Browsing to `http://10.48.167.230:8081` displays a small challenge that will give you a flag once you solve it. What is the flag?*

![image-1233](/assets/img/obsidian/net-sec-challenge/image-1233.png)

Since they want us to avoid being detected, let's use `nmap` with the `-sN` flag
since it doesn't set any **TCP** header (**TCP NUll**).

![image-1234](/assets/img/obsidian/net-sec-challenge/image-1234.png)

And we get the flag!

*DONE!!!*

---
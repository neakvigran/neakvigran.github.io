---
title: "Interceptor"
date: 2026-10-31 18:17:37 +0700
categories: ["TryHackMe", "Challenge"]
tags: ["tryhackme"]
toc: true
comments: false
---

![image-1285](/assets/img/obsidian/interceptor/image-1285.png)

# Scenario

**MediaHub** appears to be a normal internal portal used by journalists to manage content. Everything seems protected behind a login and verification system, but the real story lies in how the application communicates with its backend APIs.

Your task is to assume the role of an attacker and closely observe traffic between the browser and the server. Using your proxy skills, intercept the requests, analyse how the application processes them, and experiment with modifying the data being sent.

If you understand the flow well enough, a small change in the request might be all it takes to bypass the intended controls. Fire up your proxy, intercept the traffic, and see if you can manipulate the requests to take control of the system.

# Questions

![image-1286](/assets/img/obsidian/interceptor/image-1286.png)

---

# Recon

`rustscan -a 10.48.166.24 -- -sV -sC`

![image-1287](/assets/img/obsidian/interceptor/image-1287.png)

![image-1288](/assets/img/obsidian/interceptor/image-1288.png)

Port 22 (SSH), 53 (DNS), 80 (HTTP) are opened.

So, let start from website enumerate first.

![image-1289](/assets/img/obsidian/interceptor/image-1289.png)

![image-1291](/assets/img/obsidian/interceptor/image-1291.png)

Then I will use `gobuster` to find hidden dir.

![image-1299](/assets/img/obsidian/interceptor/image-1299.png)![image-1292](/assets/img/obsidian/interceptor/image-1292.png)

We found interesting dir `login.php.bak`, which seem to be backup file, so let's download this file first.

```php title:login.php.bak
<?php
include "header.php";

/*
|--------------------------------------------------------------------------
| Developer Note (temporary)
|--------------------------------------------------------------------------
| Admin test account for staging environment
| Email: admin@mediahub.thm
|
| Password policy reminder:
| Admin password follows company format:
| MediaHub + any year
|
| TODO: remove before production deployment
*/
?>

<div class="row justify-content-center">
  <div class="col-md-5">
    <div class="card p-4">

      <h4 class="mb-3">Login</h4>

      <form id="loginForm">
        <input class="form-control mb-3" name="email" placeholder="Email" required>

        <input class="form-control mb-3" name="password" type="password" placeholder="Password" required>

        <button id="btnLogin" class="btn btn-primary w-100" type="submit">
          Login
        </button>
      </form>

      <div id="msg" class="mt-3"></div>

    </div>
  </div>
</div>

<script>
const form = document.getElementById("loginForm");
const msg  = document.getElementById("msg");
const btn  = document.getElementById("btnLogin");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  msg.innerHTML = `<div class="text-muted">Signing in...</div>`;
  btn.disabled = true;

  const payload = new FormData(form);

  try {
    const res = await fetch("api_login.php", {
      method: "POST",
      body: payload
    });

    const data = await res.json();

    if (!data.ok) {
      msg.innerHTML = `<div class="alert alert-danger py-2 mb-0">${data.error}</div>`;
      btn.disabled = false;
      return;
    }

    msg.innerHTML = `<div class="alert alert-success py-2 mb-0">${data.message}</div>`;
    setTimeout(() => window.location = data.redirect, 400);

  } catch (err) {
    msg.innerHTML = `<div class="alert alert-danger py-2 mb-0">Something went wrong.</div>`;
    btn.disabled = false;
  }
});
</script>

<?php include "footer.php"; ?>  
```

![image-1297](/assets/img/obsidian/interceptor/image-1297.png)

It show inportant information like admin email and password format `MediaHub + YEAR`, so we can create custom word list to brute force on login page.

```bash
for y in {1990..2035}; do
    echo "MediaHub$y"
done > mediahub-years.txt
```

I use some simple for loop to create wordlists contained custom password follow the format.

![image-1300](/assets/img/obsidian/interceptor/image-1300.png)

I use simple script to use curl command and check which password is correct

![image-1301](/assets/img/obsidian/interceptor/image-1301.png)

Password is `MediaHub2026`


![image-1295](/assets/img/obsidian/interceptor/image-1295.png)


![image-1302](/assets/img/obsidian/interceptor/image-1302.png)

After login it ask for OTP sent to the email. I inspect this page script and we can see that if we success it will redirect to `dashboard.php`

```html
<script>
const form = document.getElementById("otpForm");
const msg  = document.getElementById("msg");
const btn  = document.getElementById("btnVerify");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  msg.innerHTML = `<div class="text-muted">Verifying...</div>`;
  btn.disabled = true;

  const payload = new FormData(form);

  try {
    const res = await fetch("verify_otp.php", {
      method: "POST",
      body: payload
    });

    const data = await res.json();

    // UI: show only message/error on DOM
    if (!data.ok) {
      msg.innerHTML = `<div class="alert alert-danger py-2 mb-0">${data.error}</div>`;
      btn.disabled = false;
      return;
    }

    msg.innerHTML = `<div class="alert alert-success py-2 mb-0">${data.message}</div>`;

    setTimeout(() => {
      window.location = "dashboard.php";
    }, 700);

  } catch (err) {
    msg.innerHTML = `<div class="alert alert-danger py-2 mb-0">Something went wrong.</div>`;
    btn.disabled = false;
  }
});
</script>
```

So, I try put some number and use burp to inspect response

![image-1303](/assets/img/obsidian/interceptor/image-1303.png)

"is_verified:false" is interesting, I will use this to bypass otp verification. So, I use burp intercept and put is_verified and set value to true and send request.

![image-1304](/assets/img/obsidian/interceptor/image-1304.png)

Now, it said redirecting... so I change path to `/dashboard.php` and now we are in.

![image-1305](/assets/img/obsidian/interceptor/image-1305.png)

![image-1306](/assets/img/obsidian/interceptor/image-1306.png)

Inside we can use upload and Import feed. This might be vuln.

But it seem like picture upload is filter only picture, so let's focus on import feed features

![image-1307](/assets/img/obsidian/interceptor/image-1307.png)

we can see from error that they use curl command.

Now, I try to do command injection by fetch back to they localhost ip.

![image-1310](/assets/img/obsidian/interceptor/image-1310.png)

"Private network access blocked", so let's bypass by using `127.1` instead

![image-1311](/assets/img/obsidian/interceptor/image-1311.png)


Now it work!

![image-1312](/assets/img/obsidian/interceptor/image-1312.png)

but it not work but from the error message "Could not resolve host: id"
this might mean we have to put file path instead of command.

![image-1313](/assets/img/obsidian/interceptor/image-1313.png)

I try `http://127.1 ; file:///etc/passwd` and now it work this mean we can fetch file directly via this injection

since question asked for `/var/www/user.txt`

Use `http://127.1 ; file:///var/www/user.txt`

![image-1316](/assets/img/obsidian/interceptor/image-1316.png)

and we got the flag!

*DONE!!!*

---

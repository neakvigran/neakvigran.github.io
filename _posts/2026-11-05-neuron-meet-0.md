---
title: "Neuron Meet 0"
date: 2026-08-16
categories: ["CyLab(picoCTF)", "AI"]
tags: ["easy", "ai"]
description: "Probe a 1D perceptron over the network. Send it numbers and watch whether the neuron fires or not. Use those responses to figure out the decision boundary, then line up the last eight outputs to read the ASCII for p (01110000) and you'll earn the flag. Connect with netcat:\n\n$ nc aureolin-pixie.cylabacademy.net 50288\n\nThe input bounds are shown on connect to keep the search small. You cannot submit the same number back-to-back."
math: true
toc: true
comments: false
---

![image-1696](/assets/img/obsidian/neuron-meet-0/image-1696.png)

![image-1697](/assets/img/obsidian/neuron-meet-0/image-1697.png)

![image-1698](/assets/img/obsidian/neuron-meet-0/image-1698.png)

Test numbers with the probe until the output matches the target pattern to get the flag!

The perceptron fires when $$w*x + b>=0$$. Testing 0, 1, and 2 shows that it fires when $$x>=2$$. To make it fire, send a number greater than or equal to 2; otherwise, send a number less than 2.

---

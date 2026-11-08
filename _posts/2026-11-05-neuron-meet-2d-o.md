---
title: "Neuron Meet 2D-O"
date: 2026-07-08
categories: ["CyLab(picoCTF)", "AI"]
tags: ["easy", "ai"]
description: "Probe a 2D perceptron over the network. Send it pairs of numbers (x, y) and watch whether the neuron fires or not. Use those responses to figure out the decision boundary, then line up the last eight outputs to read the ASCII for p (01110000) and you'll earn the flag. Connect with netcat:\n\n$ nc aureolin-pixie.cylabacademy.net 64543\n\nThe input bounds are shown on connect to keep the search small. You cannot submit the same (x, y) pair back-to-back."
math: true
toc: true
comments: false
---

![image-1700](/assets/img/obsidian/neuron-meet-2d-o/image-1700.png)

![image-1701](/assets/img/obsidian/neuron-meet-2d-o/image-1701.png)

![image-1702](/assets/img/obsidian/neuron-meet-2d-o/image-1702.png)

This is similar to the 1D challenge, but it takes two inputs, (x, y). Apply the same strategy
to get the flag!

Each input pair produces one bit: the perceptron outputs 1 when $$w_1x + w_2y + b \geq 0$$, and 0 otherwise. Choose pairs that produce the target sequence `01110000` (ASCII `p`), avoiding identical consecutive pairs as required by the challenge.

---

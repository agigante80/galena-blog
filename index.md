---
layout: default
title: Galena Blog
---

# Galena Mining & Jewelry Blog 💎

Welcome to our AI-powered blog about **Galena mining and jewelry**.  
Explore our latest posts below!

## 📜 Blog Posts

{% for post in site.posts %}
- **[{{ post.title }}]({{ post.url }})**  
  *Published on {{ post.date | date: "%B %d, %Y" }}*
{% endfor %}

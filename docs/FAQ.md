# FAQ: Custom Build and Additional Resources

This document addresses common issues, additional resources, and useful guides for building and managing the system using Docker, as well as solutions for specific challenges like email sending, LDAP authentication, and more.

## Table of Contents
1. [Error: No Space on Device](#error-no-space-on-device)
2. [Sending Emails](#sending-emails)
3. [LDAP Authentication](#ldap-authentication)
3. [Set up Ollama](#set-up-ollama)

---

## Error: No Space on Device

### Issue:
If you encounter the following error:


### Solution:
This error indicates that your EBS (Elastic Block Store) volume is full. You need to increase the size of your EBS volume.

For detailed instructions, refer to this AWS knowledge center article:  
[Increase EBS Volume Size](https://repost.aws/knowledge-center/ebs-volume-size-increase)

---

## Sending Emails

To send emails using Python, follow this guide:  
[How to Send Emails with Python](https://viblo.asia/p/gui-mail-voi-python-bWrZn7Mrlxw)

### Gmail Setup:
1. **Set up an App Password in Gmail:**
   - Go to your Google Account.
   - Select **Security** on the left-hand side.
   - Under "Signing in to Google," if you have 2-Step Verification enabled, select **App Passwords**.
   - Create a new App Password and use this password instead of your regular Gmail password in the email script.

---

## LDAP Authentication

For LDAP authentication using FastAPI, explore the following resources:

- **LDAP3 FastAPI Authentication:**  
  A simple authentication implementation using FastAPI and LDAP:  
  [LDAP3 FastAPI Auth GitHub Repository](https://github.com/RetributionByRevenue/LDAP3-fastapi-auth-simple)

- **Online LDAP Test Server:**  
  Test your LDAP configuration using an online test server:  
  [Forumsys Online LDAP Test Server](https://www.forumsys.com/2022/05/10/online-ldap-test-server/)

---

## Set up Ollama

- ollama: https://ollama.com/blog/ollama-is-now-available-as-an-official-docker-image

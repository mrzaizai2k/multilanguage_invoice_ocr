# FAQ: Custom Build and Additional Resources

This document addresses common issues, additional resources, and useful guides for building and managing the system using Docker, as well as solutions for specific challenges like email sending, LDAP authentication, and more.

## Table of Contents
1. [AWS Error](#aws-error)
2. [Sending Emails](#sending-emails)
3. [LDAP Authentication](#ldap-authentication)
3. [Set up Ollama](#set-up-ollama)
3. [Illegal instruction using lang ch in Paddle](#illegal-instruction-using-lang-ch-in-paddle)



## AWS Error

### No Space on Device:
This error indicates that your EBS (Elastic Block Store) volume is full. You need to increase the size of your EBS volume.

For detailed instructions, refer to this AWS knowledge center article:  
[Increase EBS Volume Size](https://repost.aws/knowledge-center/ebs-volume-size-increase)

### Ubuntu AWS instance reachability check failed

- Reboot instance
- Wait 1 2 mins
- Try access the instacen via SSH
    
    ```shell
    ssh -i /path/to/your-key.pem username@public-ip
    ```
https://stackoverflow.com/a/77547382/25622773

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


## Illegal instruction using lang ch in Paddle

  ```shell
  GraphPatternDetector::PDNodeCompare, std::allocator<std::pair<paddle::framework::ir::PDNode* const, paddle::framework::ir::Node*> > > const&, paddle::framework::ir::Graph*)>)
  2024-10-03T07:43:01.546387878Z 
  2024-10-03T07:43:01.546391528Z ----------------------
  2024-10-03T07:43:01.546395211Z Error Message Summary:
  2024-10-03T07:43:01.546398806Z ----------------------
  2024-10-03T07:43:01.546403060Z FatalError: `Illegal instruction` is detected by the operating system.
  2024-10-03T07:43:01.546406784Z   [TimeInfo: *** Aborted at 1727941381 (unix time) try "date -d @1727941381" if you are using GNU date ***]
  2024-10-03T07:43:01.546410723Z   [SignalInfo: *** SIGILL (@0x7682e348331a) received by PID 7 (TID 0x76829a6006c0) from PID 18446744073227744026 ***]
  2024-10-03T07:43:01.546414527Z 
  2024-10-03T07:43:02.258236787Z Illegal instruction (core dumped)
  ```

  https://github.com/PaddlePaddle/PaddleOCR/issues/11597
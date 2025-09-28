

## Username Enumeration

Using a security question form (Personal Question -> Correct Answer -> Granted Access/Privileged Action) is considered an outdated and insecure method for account recovery.

The primary reason for its weakness is that attackers can bypass it with relative ease using two main techniques:
1.  **Brute-Force:** Simply guessing answers to common questions using lists of popular words (e.g., common pet names, cities, colors).
2.  **OSINT (Open-Source Intelligence):** Gathering information about the target from social media and other public sources to find the correct answer.

This writeup demonstrates the process of exploiting this vulnerability, from enumerating a valid username to gaining full access to the account.

---

## Step 1: Enumerate a Valid Username

The first step is to identify a valid username that exists in the system. This can be automated using various tools.

### Method A: Burp Suite Intruder

1.  Navigate to the password reset page in the application and enter any username.
2.  Capture the POST request with Burp Suite.
3.  Send the request to **Intruder** (shortcut: `Ctrl + I`). The request will look similar to this:

    ```http
    POST /reset HTTP/1.1
    Host: 127.0.0.1:8080
    Content-Length: 12
    Cache-Control: max-age=0
    sec-ch-ua: "Not A(Brand";v="8", "Chromium";v="132"
    sec-ch-ua-mobile: ?0
    sec-ch-ua-platform: "Linux"
    Accept-Language: en-US,en;q=0.9
    Origin: [http://127.0.0.1:8080](http://127.0.0.1:8080)
    Content-Type: application/x-www-form-urlencoded
    Upgrade-Insecure-Requests: 1
    User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
    Sec-Fetch-Site: same-origin
    Sec-Fetch-Mode: navigate
    Sec-Fetch-User: ?1
    Sec-Fetch-Dest: document
    Referer: [http://127.0.0.1:8080/reset](http://127.0.0.1:8080/reset)
    Accept-Encoding: gzip, deflate, br
    Connection: keep-alive

    username=user
    ```

4.  In the Intruder tab, highlight the value of the `username` parameter (`ori`) and add it as an injection point (`§`).
5.  In the "Payloads" tab, load a wordlist of common usernames. A great source for such lists is SecLists:
    * [SecLists - Usernames Collection on GitHub](https://github.com/danielmiessler/SecLists/tree/master/Usernames)
6.  Launch the attack and analyze the responses (e.g., by status code or content length) to differentiate between valid and invalid usernames.

### Method B: Using `ffuf`

This method is highly recommended, especially for users of Burp Suite Community Edition.

1.  Copy the raw HTTP request from Burp Suite and save it to a text file named `request.txt`.
2.  In the file, replace the username you want to test with the keyword `FUFF`.

    ```http
    POST /reset HTTP/1.1
    Host: 127.0.0.1:8080
    ...

    username=FUFF
    ```
3.  Download a username wordlist (e.g., `wordlist.txt`) and save it in the same directory.
4.  Run the following command in your terminal:

    ```bash
    ffuf -w wordlist.txt -request request.txt
    ```

After running the command, you will have a list of valid usernames. For this example, let's assume we discovered the username `frank`.

---

## Step 2: Find the Correct Answer to the Security Question

Once a valid username (`frank`) is found, the system presents their security question. Let's assume the question is:
> What is your first pet's name?

Just as we enumerated usernames, we can now brute-force the answer. We can use Burp Intruder or `ffuf` again, but this time with a wordlist tailored to the question (e.g., a list of common pet names).

After running an attack with a list of common pet names, we find that the correct answer is `max`.

---

## Step 3: Reset the Password and Gain Access

1.  Submit the username `frank` and the correct security answer `max`.
2.  The application validates the answer and redirects to a form where you can set a new password for the user `frank`.
3.  Set a new password of your choice.
4.  You can now log in to the application as the user `frank` with the new password, having successfully compromised the account.

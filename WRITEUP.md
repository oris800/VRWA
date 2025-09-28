

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



# Business Logic Flaw in Cart Functionality Leads to Price Manipulation

1.  **Initial State:** As a user with insufficient funds, attempt to purchase a high-value item. For this example, we add the "Amiga 500" priced at **$699.00** to the cart. Proceeding to checkout results in an error message indicating insufficient funds.

2.  **Add a Cheaper Item:** To enable the exploit, add a second, low-cost item to the cart.

3.  **Intercept the 'Decrease Quantity' Request:** Navigate to the cart (`/cart`) and click the button to decrease the quantity of the *cheaper* item. Intercept the resulting `POST` request using a proxy tool like Burp Suite. The legitimate request looks as follows:

    ```http
    POST /cart HTTP/1.1
    Host: 127.0.0.1:8080
    Content-Length: 31
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
    Referer: [http://127.0.0.1:8080/cart](http://127.0.0.1:8080/cart)
    Accept-Encoding: gzip, deflate, br
    Cookie: session=eyJ1c2VybmFtZSI6ImJvYiJ9.aNhTwA.nEqHq_WGZ5scxON6xOqs5HfxRwc
    Connection: keep-alive

    quantity=1&productid_dcrease=12
    ```

4.  **Manipulate the Request:** Modify the `quantity` parameter in the request body from its original value (`1`) to a number greater than the quantity of the cheap item in the cart. For instance, if there is one cheap item in the cart, we can change the parameter to `10`. This effectively asks the server to decrease the quantity by 10, resulting in a negative value.

5.  **Observe the Result:** Forward the modified request. The server processes it, and the cart's state is updated. The quantity of the cheap item becomes negative (`-9`), resulting in a negative price.

    The cart calculation is now as follows:
    - Amiga 500: `$699.00`
    - Cheaper Item (Quantity: -9): `-$531.00`
    - **New Total:** `$699.00 - $531.00 = $168.00`

6.  **Complete the Purchase:** The new total price is now **$168.00**. The user now has sufficient funds to complete the transaction and successfully purchase the "Amiga 500" at a fraction of its original cost.

---

## Secondary Finding: Information Disclosure

Upon completing the manipulated purchase, a "fun fact" is displayed on the confirmation page:

> "the entire shopping system for this website was developed by the user customer35 on the amiga 500. Isn't that cool?"

This message discloses an internal username (`customer35`), which could be leveraged in further attacks, such as username enumeration or targeted password guessing attempts.

---

## Remediation

1.  **Implement Strict Server-Side Validation:** The core logic for updating cart quantities must be hardened. The backend should enforce a rule that an item's quantity can never be less than zero. Before processing a decrease request, the server should calculate the potential result and ensure `(current_quantity - quantity_to_decrease) >= 0`. Any request that would result in a negative quantity should be rejected.

2.  **Remove Sensitive Information from Public Messages:** The "fun fact" message should be removed immediately. Internal information, including usernames or development details, should never be exposed to end-users.

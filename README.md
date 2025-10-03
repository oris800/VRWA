# VRWA: A Vulnerable Retro Web Application (CTF)

Welcome to RetroStore, a fully functional e-commerce web application I built from the ground up to serve as a hands-on learning environment for web security.

This project is designed as a complete offensive campaign, not just a collection of random bugs. The goal is to discover and chain multiple vulnerabilities together to achieve a full system compromise.

---

## 🎯 The Mission

Your objective is to chain together **7 distinct vulnerabilities** to achieve a full system takeover (via a Reverse Shell).

### Key Features
* User registration and login system.
* External and internal password reset mechanisms.
* Product review and comment system.
* A complete shopping cart and checkout system.


## 🛠️ Tech Stack

* **Backend:** Python 3, Flask 🐍
* **Database:** MySQL 🐘
* **Infrastructure:** Docker, Docker Compose 🐋

---

## 🔥 The Challenge

Think you have what it takes?

* **Stuck? Or just curious about the design?** The full solution and a detailed explanation of each vulnerability can be found in the official write-up:
    **[WRITEUP.md](WRITEUP.md)**

---

## 🚀 Local Installation & Setup

To run this project on your local machine, please ensure you have Git, Docker, and Docker Compose installed.

**Note:** These instructions are intended for a Unix-like environment (Linux, macOS, BSD or WSL on Windows).

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/oris800/VRWA.git
    ```

2.  **Navigate to the project directory:**
    ```bash
    cd VRWA
    ```

3.  **Build and run the environment using Docker Compose:**
    ```bash
    docker-compose up --build -d
    ```
    *(Note: Depending on your Docker installation, you may need to run this command with `sudo`)*

4.  **Access the application:**
    Once the containers are up and running, navigate to `http://localhost:8080` in your web browser.

5.  **Shutting down the environment:**
    To stop and remove the containers run:
    ```bash
    docker-compose down
    ```

---

## ⚖️ License

This project is licensed under the GPL3 License. See the [LICENSE](LICENSE) file for details.

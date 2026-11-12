This project has not been written by A.I.
# Project – Python Password Manager

**Project** is a secure, lightweight password manager built with Python for the command line. It allows you to generate strong passwords, store them in an encrypted format, and retrieve them easily — all locally, without external dependencies.

---

## Features

*  **User Authentication** – Sign up and log in with secure credential validation.
*  **Authenticated Encryption** – Passwords are protected with Fernet authenticated encryption.
*  **Password Generator** – Create passwords of custom length and strength (weak, medium, strong).
*  **Per-User Encrypted Storage** – Each user has a separate `.csv` file, encrypted with their own password.
*  **Tabular Display** – View stored credentials in a clean, structured table using `tabulate`.

---

## Requirements

Install dependencies:

```bash
pip install cryptography tabulate pytest
```
Or

Also avalable in requirements.txt you can install with:

```bash
pip install -r requirements.txt
```


Compatible with **Python 3.10+**.

---

## Getting Started

Clone the repository and run the script:

```bash
git clone https://github.com/MCnima/project.git
cd project
python project.py
```

---

## How It Works

### Authentication

* Credentials are stored as a SHA3-512 hash of `username + password` in `data.csv`.
* The login process validates this hash before allowing access.

### File Structure

```
project/
├── project.py               # Main program
├── data.csv                 # Stores hashed login credentials
├── <user1>.csv              # Encrypted, per-user storage file
├── <user2>.csv              # Encrypted, per-user storage file
.
.
.
```

### Encryption

* **Algorithm**: Fernet authenticated encryption (AES and HMAC, via `cryptography.Fernet`)
* **Key Derivation**: PBKDF2-HMAC-SHA256 with 1,500,000 iterations
* **Salt**: Static (for simplicity and lack of options; can be improved for production)

### Password Generation

* **Weak**: Lowercase letters only
* **Medium**: Lowercase letters + digits
* **Strong**: Lowercase + uppercase + digits + symbols

---

## Example

```bash
$ python project.py
Welcome. Use login to access your account or use signup to create a new account (login/signup)
```

After loging in choose:

* `1. Show saved passwords` with `show`
* `2. Create new password` with `create`

After a successful login, the user's file is decrypted only for the active menu operation.
It is re-encrypted in a `finally` block whenever that operation ends, including normal
completion, invalid input, `ValueError`, `Ctrl+C`, end-of-file input, and unexpected errors.
If decryption fails, the file remains encrypted and the session does not attempt to overwrite it.

---

##  Notes

* If you forget your login password, your encrypted data **cannot** be recovered.
* All data is stored **locally** in the script directory.
* The program currently uses `clear` to clear the console; Windows users can replace it with `cls`.
* A new user's storage file is encrypted immediately, even before the first login.

---

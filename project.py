import sys
import random
import os
import csv
import hashlib
import base64
from tabulate import tabulate
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def main():
    if not os.path.exists(r"data.csv"):
        print("Creating data file...")
        open("data.csv", "a").close()
    try:
        log_sign = str(input("Wellcome. Use login to access your account or use signup to create new account (login/signup)\n")).lower()
        match log_sign:
            case "login":
                user, passw = login()
                decryptt(user, passw)
                try:
                    print("____Menu____")
                    match str(input("-Show saved passwords\n--Create new password\n(show/create)")).lower():
                        case "show":
                            show(user)

                        case "create":
                            usr = str(input("What should your username be? "))
                            leng = int(input("how many characters should your password be?(e.g. 12) "))
                            strength = str(input("How strong should your password be?(weak/medium/strong) ")).lower()
                            if strength == "weak":
                                password = generate(weak=True, length=leng)
                            elif strength == "medium":
                                password = generate(medium=True, length=leng)
                            elif strength == "strong":
                                password = generate(strong=True, length=leng)
                            else:
                                sys.exit("Wrong type of input was used.\nExiting program...")
                            desc = str(input("Add a description for your password(optional): "))
                            if desc == "":
                                desc = "None"
                            add_to_file(file=user, user=usr, password=password, description=desc)
                finally:
                    encrypt_file(user, passw)

            case "signup":
                signup()

    except ValueError:
        sys.exit("Wrong type of input was used.\nExiting program...")





def generate(weak=False, medium=False, strong=False, length=12):
    """
    Creates passwords with different strength level.
    Weak passwords are made of only lowercase alphabet characters.
    Medium passwords are made of lowercase alphabet plus numbers.
    Strong passwords use lowercase and uppercase alphabet characters as well as numbers and signs.
    (not all of them because some websites dont accept .  ?  /  (back slash) in passwords)
    Returns created password as string
    """
    lower = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o',
             'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    upper = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O',
             'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    number = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
    sign = ['@', '#', '$', '&', '_', '-', '!', '=']
    char_list = []
    password = ''
    if weak:
        char_list = lower
    elif medium:
        char_list = lower + number
    elif strong:
        char_list = lower + upper + number + sign
    else:
        sys.exit("Password stregth was not in correct form")

    for i in range(length):
        password = password + random.choice(char_list)
    print(f"Your new password is: {password}")
    return password


def login():
    """
    Launches login menu.
    Gets username and password from user and sends them to manage_login_pass function to validate them.
    If username and password was valid continues to check if a personal data file in name of <username>.csv exists or not.
    If not asks to create new one or for user to move his file to original place.
    Returns persons login username and password for encryption and decryption purposes.
    """
    os.system("clear")
    print("____Login____")
    log_user_name = str(input("Username : "))
    log_password = str(input("Password : "))
    if not manage_login_pass(user=log_user_name, password=log_password):
        sys.exit("Username or Password was wrong! Exiting program...")
    else:
        print(f"Welcome back {log_user_name} !")
        if not os.path.exists(f"{log_user_name}.csv"):
            if str(input("User file doesn't exit! do you want to create new file?(yes/no) ")).lower() in ['yes', 'y']:
                open(f"{log_user_name}.csv", "a").close()
                encrypt_file(log_user_name, log_password)
                print("New user data file was created!")
            else:
                sys.exit(f"Move or copy original user data file {log_user_name}.csv to current folder and launch program again")
        return log_user_name , log_password


def manage_login_pass(user, password):
    """
    Gets username and password and checks for them in data.csv file.
    Uses hash function to hash combination of password and username.
    If hash value of that password plus username equals saved password
    in data.csv file, returns True
    """
    is_valid = False
    pass_list = []
    with open("data.csv") as file:
        reader = csv.reader(file)
        for a, b in reader:
            pass_list.append([a, b])
        file.close()
    for usr in pass_list:
        if usr[0] == user:
            hashed_password = hash(password, user)
            if usr[1] == hashed_password:
                is_valid = True
    return is_valid


def signup():
    """
    Starts signup menu. Clears the outputs of consule and asks for a username .Checks to make
    sure username is taken or not.If its taken prompts you to input different username then asks
    for a password. After hashing tha password plus username, stores the username and hash value in data.csv.
    Data.csv is main data file for securely storing login usernames and passwords.
    """
    username_list = []
    os.system("clear")
    while True:
        print("____Signup____")
        sign_user_name = str(input("Username : "))
        with open("data.csv") as file:
            reader = csv.reader(file)
            for a, b in reader:
                username_list.append(a)
            file.close()
        if sign_user_name in username_list:
                print("This username is taken.Try another one.")
        else:
            break
    sign_password = str(input("Password : "))
    password = hash(sign_password, sign_user_name)
    line = [[sign_user_name,password]]
    with open("data.csv" , "a") as file:
        writer = csv.writer(file)
        writer.writerows(line)
        file.close()
    print(f"User created!")
    open(f"{sign_user_name}.csv", "a").close()
    encrypt_file(sign_user_name, sign_password)
    sys.exit("Now relunch program and try logging in with your new username and password.")


def hash(phrase, salt):
    """
    Gets a phrase and a salt for it.Adds them together then hashes them with SHA3 512 bit algorithm.
    Returns hash value.
    """
    h = hashlib.sha3_512()
    h.update(phrase.encode('utf-8'))
    h.update(salt.encode('utf-8'))
    return h.hexdigest()


def encrypt_file(file, password):
    """
    Gets file name and password to encrypt that file with.
    Its <username>.csv for file name in this program and login password for its encryption key.
    Adds a static binary salt to combination(it was not possible to ignore this binary salt so
    i gave it static amount!!). Then rewrites encrypted value in same file after removing non encrypted
    data.
    Returns None.
    """
    password = password.encode()
    salt = b'\x8e\xbf\xfa\xed\x01\xdaV;R\xd1\xc8\xbd\x8d\xda\xf48'
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=1_500_000,)
    key = base64.urlsafe_b64encode(kdf.derive(password))
    f = Fernet(key)
    with open(f"{file}.csv", 'rb') as data:
        raw_data = data.read()
        data.close()
    token = f.encrypt(raw_data)
    with open(f"{file}.csv", "wb") as enc:
        enc.write(token)
        enc.close()


def decryptt(file, password):
    """
    Gets file name and password to decrypt file.If file is empty returns None to end function.
    Uses the same static salt from encrypt function. Reads file and replaces encrypted value
    with decrypted value.Returns None
    """
    password = password.encode()
    salt = b'\x8e\xbf\xfa\xed\x01\xdaV;R\xd1\xc8\xbd\x8d\xda\xf48'
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=1_500_000,)
    key = base64.urlsafe_b64encode(kdf.derive(password))
    f = Fernet(key)
    with open(f"{file}.csv", 'rb') as enc:
        encrypted_data = enc.read()
        enc.close()
    if encrypted_data == b"":
        return None
    token = f.decrypt(encrypted_data)
    with open(f"{file}.csv", "wb") as data:
        data.write(token)
        data.close()


def show(name):
    """
    Gets username and shows the content of that users data file with <username>.csv name using
    tabulate library. Returns None
    """
    ls = []
    head = ["Username", "Passwprd", "Description"]
    with open(f"{name}.csv") as file:
        reader = csv.reader(file)
        for a, b, c in reader:
            ls.append([a, b, c])
        file.close()
    print(tabulate(ls, head, tablefmt="grid"))


def add_to_file(file, user, password, description):
    """
    Gets newly created password username and a description for it and writes it in givin file.
    """
    ls = [user, password, description]
    with open(f"{file}.csv", "a") as f:
        writer = csv.writer(f)
        writer.writerow(ls)
        f.close()


if __name__ == "__main__":
    main()
    # print(hash("nima", "salt"))
    # encrypt_file("nima", "1234")
    # decrypt("nima", "1234")
    # print(os.urandom(16))

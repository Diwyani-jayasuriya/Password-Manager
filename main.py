import sqlite3
from cryptography.fernet import Fernet
import os
import hashlib

def setup_master_password():
    if not os.path.exists("master.txt"):
        print("--- First Time Setup ---")
        mp = input("Create a Master Password: ")
        hashed_mp = hashlib.sha256(mp.encode()).hexdigest()
        with open("master.txt", "w") as f:
            f.write(hashed_mp)
        print("Master Password created successfully!\n")
        return True
    else:
        mp = input("Enter Master Password: ")
        hashed_mp = hashlib.sha256(mp.encode()).hexdigest()
        with open("master.txt", "r") as f:
            stored_hash = f.read().strip()
        if hashed_mp == stored_hash:
            return True
        else:
            return False

def load_or_generate_key():
    if not os.path.exists("secret.key"):
        key = Fernet.generate_key()
        with open("secret.key", "wb") as key_file:
            key_file.write(key)
    else:
        with open("secret.key", "rb") as key_file:
            key = key_file.read()
    return key

def setup_database():
    conn = sqlite3.connect("passwords.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS credentials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            website TEXT NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    return conn

def add_password(conn, cipher_suite):
    website = input("Website: ")
    username = input("Username: ")
    password = input("Password: ")
    
    encrypted_pwd = cipher_suite.encrypt(password.encode()).decode()
    
    cursor = conn.cursor()
    cursor.execute("INSERT INTO credentials (website, username, password) VALUES (?, ?, ?)", 
                   (website, username, encrypted_pwd))
    conn.commit()
    print("Added Successfully.\n")

def view_passwords(conn, cipher_suite):
    cursor = conn.cursor()
    cursor.execute("SELECT website, username, password FROM credentials")
    rows = cursor.fetchall()
    
    print("\n--- Saved Passwords ---")
    for row in rows:
        decrypted_pwd = cipher_suite.decrypt(row[2].encode()).decode()
        print(f"Website: {row[0]} | Username: {row[1]} | Password: {decrypted_pwd}")
    print("-----------------------\n")

if __name__ == "__main__":
    if not setup_master_password():
        print("Access Denied: Incorrect Master Password.")
        exit()
        
    key = load_or_generate_key()
    cipher_suite = Fernet(key)
    conn = setup_database()
    
    while True:
        mode = input("Options: add / view / q (quit): ").lower()
        if mode == "q":
            break
        elif mode == "add":
            add_password(conn, cipher_suite)
        elif mode == "view":
            view_passwords(conn, cipher_suite)
        else:
            print("Invalid option.")
import tkinter as tk
from tkinter import messagebox
import sqlite3
import hashlib
from homepage import MainPage


class Login:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Login")
        self.root.geometry("450x250")
        self.conn = sqlite3.connect("Database.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY AUTOINCREMENT, username VARCHAR(255), password VARCHAR(255))"
        )
        self.conn.commit()
        self.create_login_page()

    ######################################### Encrypt the Inputted Password ##################################
    def encrypt_password(self, password):
        sha256 = hashlib.sha256()
        sha256.update(password.encode("utf-8"))
        encrypted_password = sha256.hexdigest()
        return encrypted_password

    ######################################### Submit the New Username and Passowrd ##########################
    def submit(self):
        new_username = self.entry_new_username.get()
        new_password = self.entry_new_password.get()
        enc_password = self.encrypt_password(new_password)

        self.cursor.execute("SELECT * FROM Users WHERE username=?", (new_username,))
        existing_user = self.cursor.fetchall()

        if existing_user:
            messagebox.showerror(
                "Username Exists", "Username already exists. Try logging in instead."
            )
        else:
            self.cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (new_username, enc_password),
            )
            self.conn.commit()
            messagebox.showinfo("Success", "User Added")

    ######################################### Login Check and Entry #######################################
    def login_conn(self):
        entered_username = self.entry_username.get()
        entered_password = self.entry_password.get()
        enc_password = self.encrypt_password(entered_password)

        self.cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (entered_username, enc_password),
        )
        user = self.cursor.fetchall()
        if user:
            messagebox.showinfo("Login", f"Welcome, {entered_username}!")
            self.root.destroy()

            self.cursor.execute(
                "SELECT user_id FROM users WHERE username = ?", (entered_username,)
            )
            user_id = self.cursor.fetchone()[0]

            homepage = MainPage(user_id)
            homepage.root.mainloop()
        else:
            messagebox.showerror("Login Error", "Credentials don't match")

    ######################################### Login Page UI ##############################################
    def create_login_page(self):
        if hasattr(self, "signup_frame"):
            self.signup_frame.pack_forget()
        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack(fill=tk.BOTH, expand=True)

        self.label_username = tk.Label(self.login_frame, text="Username:")
        self.label_username.pack()

        self.entry_username = tk.Entry(self.login_frame)
        self.entry_username.pack()

        self.label_password = tk.Label(self.login_frame, text="Password:")
        self.label_password.pack()

        self.entry_password = tk.Entry(self.login_frame, show="*")
        self.entry_password.pack()

        button_login = tk.Button(
            self.login_frame, text="Login", command=lambda: self.login_conn()
        )
        button_login.pack(pady=10)

        label_new_user = tk.Label(self.login_frame, text="New User?")
        label_new_user.pack(side=tk.LEFT)

        button_signup = tk.Button(
            self.login_frame, text="Sign Up", command=lambda: self.create_signup_page()
        )
        button_signup.pack(side=tk.LEFT)

    ##################################### Sign Up Page UI #############################################

    def create_signup_page(self):
        if hasattr(self, "signup_frame"):
            self.signup_frame.pack_forget()

        self.login_frame.pack_forget()

        self.signup_frame = tk.Frame(self.root)
        self.signup_frame.pack(fill=tk.BOTH, expand=True)

        self.label_new_username = tk.Label(self.signup_frame, text="New Username:")
        self.label_new_username.pack()

        self.entry_new_username = tk.Entry(self.signup_frame)
        self.entry_new_username.pack()

        self.label_new_password = tk.Label(self.signup_frame, text="New Password:")
        self.label_new_password.pack()

        self.entry_new_password = tk.Entry(self.signup_frame, show="*")
        self.entry_new_password.pack()

        button_submit = tk.Button(
            self.signup_frame, text="Submit", command=lambda: self.submit()
        )
        button_submit.pack(pady=10)

        button_return_login = tk.Button(
            self.signup_frame,
            text="Return to Login Page",
            command=lambda: self.create_login_page(),
        )
        button_return_login.pack(pady=10)

if __name__ == "__main__":
    display_instance = Login()
    display_instance.root.mainloop()
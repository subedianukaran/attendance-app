import tkinter as tk
from tkinter import messagebox
import sqlite3
import os

from homepage import MainPage

class DatabaseManager:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def create_table(self, table_name, columns):
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")
        self.conn.commit()

    def execute_query(self, query, data=None):
        if data:
            self.cursor.execute(query, data)
        else:
            self.cursor.execute(query)
        self.conn.commit()

    def fetch_all(self, query, data=None):
        if data:
            self.cursor.execute(query, data)
        else:
            self.cursor.execute(query)
        return self.cursor.fetchall()

    def close_connection(self):
        self.conn.close()


class Login:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Login")
        self.root.geometry("450x250") # 450 x 250

        self.main_db = DatabaseManager('Credentials.db')
        self.create_main_table()

        self.create_login_page()

    def create_main_table(self):
        columns = "username TEXT PRIMARY KEY, password TEXT"
        self.main_db.create_table('Users', columns)

    def create_user_db(self, username):
        db_name = f"{username}.db"
        user_db = DatabaseManager(db_name)
        user_db.create_table('RecordList', 'id INTEGER PRIMARY KEY, Class TEXT')
        user_db.close_connection()

    def submit(self):
        new_username = self.entry_new_username.get()
        new_password = self.entry_new_password.get()

        # Checking if existing user is trying to signup
        query = 'SELECT * FROM Users WHERE username=?'
        existing_user = self.main_db.fetch_all(query, (new_username,))

        if existing_user:
            messagebox.showerror("Username Exists", "Username already exists. Try logging in instead.")
        else:
            self.main_db.execute_query('INSERT INTO Users VALUES (?, ?)', (new_username, new_password))
            messagebox.showinfo("Success", "User Added")
            self.create_user_db(new_username)

    def login_conn(self):
        entered_username = self.entry_username.get()
        entered_password = self.entry_password.get()

        query = 'SELECT * FROM Users WHERE username=? AND password=?'
        user = self.main_db.fetch_all(query, (entered_username, entered_password))
        if user:
            self.root.destroy()
            messagebox.showinfo("Login", f"Welcome, {entered_username}!")
            homepage= MainPage(entered_username)
            homepage.root.mainloop()
          # entered_username as variable
        else:
            messagebox.showerror("Login Error", "Credentials don't match")

    def remove_user(self):
        selected_index = int(self.entry_index.get())

        conn = sqlite3.connect('Credentials.db')
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM Users')
        users = cursor.fetchall()

        if selected_index >= 0 and selected_index < len(users):
            username_to_remove = users[selected_index][0]
            cursor.execute('DELETE FROM Users WHERE username=?', (username_to_remove,))
            conn.commit()
            os.remove(f"{username_to_remove}.db")
            messagebox.showinfo("Success", f"User '{username_to_remove}' removed successfully.")
            self.remove_frame.destroy()
            self.create_remove_page()

        else:
            messagebox.showerror("Error", "Invalid index")

        conn.close()

    def create_login_page(self):
        if hasattr(self, 'remove_frame'):
            self.remove_frame.pack_forget()
        if hasattr(self, 'signup_frame'):
            self.signup_frame.pack_forget()
        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack(fill=tk.BOTH, expand=True)

        self.label_username = tk.Label(self.login_frame, text="Username:")
        self.label_username.pack()

        self.entry_username = tk.Entry(self.login_frame)
        self.entry_username.pack()

        self.label_password = tk.Label(self.login_frame, text="Password:")
        self.label_password.pack()

        self.entry_password = tk.Entry(self.login_frame, show='*')
        self.entry_password.pack()

        button_login = tk.Button(self.login_frame, text="Login", command=lambda: self.login_conn())
        button_login.pack()

        label_new_user = tk.Label(self.login_frame, text="New User?")
        label_new_user.pack(side=tk.LEFT)

        button_signup = tk.Button(self.login_frame, text="Sign Up", command=lambda: self.create_signup_page())
        button_signup.pack(side=tk.LEFT)

        button_remove_user = tk.Button(self.login_frame, text="Remove Existing User", command=lambda: self.create_remove_page())
        button_remove_user.pack(side=tk.RIGHT)

    def create_signup_page(self):
        if hasattr(self, 'signup_frame'):
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

        self.entry_new_password = tk.Entry(self.signup_frame, show='*')
        self.entry_new_password.pack()

        button_submit = tk.Button(self.signup_frame, text="Submit", command=lambda: self.submit())
        button_submit.pack()

        button_return_login = tk.Button(self.signup_frame, text="Return to Login Page", command=lambda: self.create_login_page())
        button_return_login.pack()

    def create_remove_page(self):
        if hasattr(self, 'remove_frame'):
            self.remove_frame.pack_forget()

        self.login_frame.pack_forget()

        self.remove_frame = tk.Frame(self.root)
        self.remove_frame.pack(fill=tk.BOTH, expand=True)

        label_instructions = tk.Label(self.remove_frame, text="Enter index of user to remove:")
        label_instructions.pack()

        # Display user list
        conn = sqlite3.connect('Credentials.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Users')
        users = cursor.fetchall()

        for index, user in enumerate(users):
            tk.Label(self.remove_frame, text=f"{index}: {user[0]}").pack()

        self.entry_index = tk.Entry(self.remove_frame)
        self.entry_index.pack()

        button_remove = tk.Button(self.remove_frame, text="Remove", command=lambda: self.remove_user())
        button_remove.pack()

        button_return_login = tk.Button(self.remove_frame, text="Return to Login Page", command=lambda: self.create_login_page())
        button_return_login.pack()

        conn.close()


display_instance = Login()
display_instance.root.mainloop()

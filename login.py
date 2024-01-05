from tkinter import *
from tkinter import messagebox
import sqlite3
import hashlib

def create_database():
    conn = sqlite3.connect('Credentials.db')
    cursor = conn.cursor()

    # Create the Users table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    ''')

    conn.commit()
    conn.close()


class Display:

    def __init__(self):
        pass

    def create_user_db(self,username):
        self.username = username
        db_name = f"{self.username}.db"
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS RecordList (
                id INTEGER PRIMARY KEY,
                Class TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def submit(self):
        self.new_username = self.entry_new_username.get()
        self.new_password = self.entry_new_password.get()

        # Connect to the main credentials database
        conn_main = sqlite3.connect('Credentials.db')
        cursor_main = conn_main.cursor()

        cursor_main.execute('INSERT INTO Users VALUES (?, ?)', (self.new_username, self.new_password))
        conn_main.commit()

        messagebox.showinfo("Success", "User Added")

        conn_main.close()

        # Create a separate database for the new user
        self.create_user_db(self.new_username)

    def login_conn(self,username_entry, password_entry):
        self.entered_username = username_entry.get()  # Use username_entry in the login page
        self.entered_password = password_entry.get()  # Use password_entry in the login page

        conn = sqlite3.connect('Credentials.db')
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM Users WHERE username=? AND password=?', (self.entered_username, self.entered_password))
        user = cursor.fetchone()

        if user:
            messagebox.showinfo("Login", f"Welcome, {self.entered_username}!")
            root.destroy()
            import gui_homepage

        else:
            messagebox.showerror("Login Error", "Credentials don't match")

        conn.close()
    def login_page(self):
        self.loginframe = Frame(root)
        self.loginframe.pack(fill=BOTH, expand=True)

        login_label = Label(self.loginframe, text="Login", font=("Arial", 18, "bold"))
        login_label.grid(pady=30)
        login_label.pack()
        label_username = Label(self.loginframe, text="Username:")
        label_username.pack()

        entry_username = Entry(self.loginframe)
        entry_username.pack()

        label_password = Label(self.loginframe, text="Password:")
        label_password.pack()

        entry_password = Entry(self.loginframe, show='*')
        entry_password.pack()

        button_login = Button(self.loginframe, text="Login") #command=login_conn(entry_username, entry_password))
        button_login.pack()

        label_new_user = Label(self.loginframe, text="New User?")
        label_new_user.pack(side=LEFT)

        button_signup = Button(self.loginframe, text="Sign Up",
                               command=lambda: (self.loginframe.destroy(), self.signup_page()))
        button_signup.pack(side=LEFT)

        button_remove_user = Button(self.loginframe, text="Remove Existing User",
                                    command=lambda: (self.loginframe.destroy(), self.remove_page())) #, command=removeuser_page) # this may create error try to use this same command
        button_remove_user.pack(side=RIGHT)

    def signup_page(self):
        self.signupframe = Frame(root)
        self.signupframe.pack(fill=BOTH, expand=TRUE)

        signup_label = Label(self.signupframe, text="Sign Up", font=("Arial", 18, "bold"))
        signup_label.grid(pady=30)
        signup_label.pack()


        self.label_new_username = Label(self.signupframe, text="Username:")
        self.label_new_username.pack()

        self.entry_new_username = Entry(self.signupframe)
        self.entry_new_username.pack()

        self.label_new_password = Label(self.signupframe, text="Password:")
        self.label_new_password.pack()

        self.entry_new_password = Entry(self.signupframe, show='*')
        self.entry_new_password.pack()

        button_submit = Button(self.signupframe, text="Submit", command=self.submit)
        button_submit.pack()

        button_return_login = Button(self.signupframe, text="Return to Login Page", command=lambda: (self.signupframe.destroy(), self.login_page()))
        button_return_login.pack()

    def display_users(self):
        conn = sqlite3.connect('Credentials.db')
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM Users')
        users = cursor.fetchall()

        conn.close()

        return users

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
            messagebox.showinfo("Success", f"User '{username_to_remove}' removed successfully.")
        else:
            messagebox.showerror("Error", "Invalid index")

        conn.close()

    def remove_page(self):
        self.removeframe = Frame(root)
        self.removeframe.pack(fill=BOTH, expand=TRUE)


        label_instructions = Label(self.removeframe, text="Enter index of user to remove:")
        label_instructions.pack()

        # Display user list
        users = self.display_users()
        for index, user in enumerate(users):
            Label(self.removeframe, text=f"{index}: {user[0]}").pack()

        self.entry_index = Entry(self.removeframe)
        self.entry_index.pack()

        button_remove = Button(self.removeframe, text="Remove", command=self.remove_user)
        button_remove.pack()

        button_return_login = Button(self.removeframe, text="Return to Login Page", command=lambda: (self.removeframe.destroy(), self.login_page()))
        button_return_login.pack()


def login_window():
    global root
    root = Tk()
    root.title("Login")
    root.geometry("450x250")
    display_instance = Display()
    display_instance.login_page()
    root.mainloop()


create_database()
login_window()


import tkinter as tk
from tkinter import messagebox
import sqlite3
from tkinter import simpledialog
from datetime import datetime


class AttendanceManager:
    def __init__(self, conn, class_name):

        self.class_name = class_name
        self.conn = conn
        self.cursor = self.conn.cursor()

        self.take_attendance()

    def take_attendance(self):
        pass

    def show_attendance(self, student, date):
        pass

    def mark_attendance(self, date, roll_no, status):
        pass


class ClassHomePage:
    def __init__(self, class_name, root, cursor, conn):
        self.class_name = class_name
        self.root = root
        self.cursor = cursor
        self.conn = conn

    def take_attendance(self):
        pass

    def edit_records(self):
        pass

    def view_statistics(self):
        pass

    def delete_records(self):
        pass

    def view_students(self):
        pass

    def remove_students(self):
        def remove_students():
            student_names = student_entry.get()
            student_window.destroy()
            student_list = [name.strip() for name in student_names.split(",")]
            students_not_found = []

            try:

                for name in student_list:
                    if name:
                        self.cursor.execute(
                            f"DELETE FROM students WHERE student_name = ?", (name,)
                        )
                        if self.cursor.rowcount == 0:
                            students_not_found.append(name)

                self.conn.commit()

                if students_not_found:
                    messagebox.showwarning(
                        "Students Not Found",
                        f"The following students weren't found: {', '.join(students_not_found)}",
                    )
                else:
                    messagebox.showinfo("Success", "Students removed successfully.")

            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Error: {e}")

        student_window = tk.Toplevel()
        student_window.title("Remove Students")

        student_label = tk.Label(
            student_window, text="Enter student names to remove (separated by comma):"
        )
        student_label.pack()

        student_entry = tk.Entry(student_window, width=40)
        student_entry.pack()

        remove_button = tk.Button(
            student_window, text="Remove", command=remove_students
        )
        remove_button.pack()

    def edit_students(self):
        pass

    def add_students(self):
        def add_students_d():
            student_names = student_entry.get()
            student_window.destroy()
            student_list = [name.strip() for name in student_names.split(",")]

            try:
                for name in student_list:
                    if name:
                        self.cursor.execute(
                            f"INSERT INTO students(student_name) VALUES (?)", (name,)
                        )
                        self.conn.commit()

                messagebox.showinfo("Success", "Students added successfully.")

            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Error: {e}")

        student_window = tk.Toplevel()
        student_window.title("Add Students")

        student_label = tk.Label(
            student_window, text="Enter student names (separated by comma):"
        )
        student_label.pack()

        student_entry = tk.Entry(student_window, width=40)
        student_entry.pack()

        add_button = tk.Button(student_window, text="Add", command=add_students_d)
        add_button.pack()

    def classpage(self):
        self.class_frame = tk.Frame(self.root)
        self.class_frame.pack(fill=tk.BOTH, expand=True)

        class_label = tk.Label(
            self.class_frame, text=self.class_name, font=("Arial", 18, "bold")
        )
        class_label.grid(pady=30)
        class_label.pack()

        button_texts = [
            "Take Attendance",
            "Edit Records",
            "View Statistics",
            "Delete Records",
            "View Students",
            "Add Students",
            "Remove Students",
        ]
        button_commands = [
            self.take_attendance,
            self.edit_records,
            self.view_statistics,
            self.delete_records,
            self.view_students,
            self.add_students,
            self.remove_students,
        ]

        for i in range(0, len(button_texts), 2):
            frame = tk.Frame(self.class_frame)
            frame.pack()

            for j in range(2):
                if i + j < len(button_texts):
                    button = tk.Button(
                        frame,
                        text=button_texts[i + j],
                        width=15,
                        command=button_commands[i + j],
                    )
                    button.pack(side=tk.LEFT, padx=20, pady=20)


class MainPage:
    def __init__(self, username):
        self.root = tk.Tk()
        self.root.title("Attendance Application")
        self.root.geometry("600x450")
        self.conn = sqlite3.connect("Database.db")
        self.cursor = self.conn.cursor()
        self.username = username
        self.cursor.execute("")
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS classes (class_id INTEGER PRIMARY KEY AUTOINCREMENT, class_name VARCHAR(255));"
        )
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS students (student_id INTEGER PRIMARY KEY AUTOINCREMENT, student_name VARCHAR(255));"
        )
        self.conn.commit()
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS user_class (user_id INTEGER, class_id INTEGER, PRIMARY KEY (user_id, class_id), FOREIGN KEY (user_id) REFERENCES users(user_id), FOREIGN KEY (class_id) REFERENCES classes(class_id));"
        )
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS class_student (class_id INTEGER, student_id INTEGER, PRIMARY KEY (class_id, student_id), FOREIGN KEY (class_id) REFERENCES classes(class_id), FOREIGN KEY (student_id) REFERENCES students(student_id));"
        )
        self.conn.commit()
        self.home_page()

    def add_new_class(self):
        self.new_class_name = tk.simpledialog.askstring(
            "Add New Class", "Enter new class name:"
        )

        if self.new_class_name:
            self.cursor.execute(
                "SELECT 1 FROM classes WHERE class_name = ? LIMIT 1",
                (self.new_class_name,),
            )
            self.conn.commit()
            existing_class = self.cursor.fetchone()
            if existing_class:
                messagebox.showinfo("Class Exists", "Class already exists.")
            else:
                self.cursor.execute(
                    "INSERT INTO classes (class_name) VALUES (?)",
                    (self.new_class_name,),
                )
                self.conn.commit()
                self.cursor.execute(
                    """INSERT INTO user_class (user_id, class_id)
    VALUES ((SELECT user_id FROM users WHERE username = ?), (SELECT class_id FROM classes WHERE class_name = ?));
""",
                    (self.username, self.new_class_name),
                )
                self.conn.commit()
                messagebox.showinfo(
                    "Success", f"Class '{self.new_class_name}' added successfully."
                )
                self.home_frame.destroy()
                self.home_page()

    def display_classes(self):
        self.cursor.execute("SELECT class_name FROM classes")
        classes = self.cursor.fetchall()

        for class_name in classes:
            tk.Button(
                self.home_frame,
                text=class_name[0],
                command=lambda cn=class_name[0].title(): self.class_details(cn),
                width=10,
                height=2,
            ).pack(padx=5, pady=5)

    def remove_class(self):
        pass

    def check_class_exists(self, class_name):
        pass

    def class_details(self, class_name):
        self.home_frame.destroy()
        class_page = ClassHomePage(class_name, self.root, self.cursor, self.conn)
        class_page.classpage()

    def home_page(self):
        self.home_frame = tk.Frame(self.root)
        self.home_frame.pack(fill=tk.BOTH, expand=True)

        label_classes = tk.Label(
            self.home_frame, text="Classes", font=("Arial", 24, "bold")
        )
        label_classes.pack(pady=20)

        self.display_classes()

        button_frame = tk.Frame(self.home_frame)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        self.add_class_button = tk.Button(
            button_frame, text="Add New Class", command=self.add_new_class
        )
        self.add_class_button.pack(side=tk.LEFT, padx=10)

        self.remove_class_button = tk.Button(
            button_frame, text="Remove Class", command=self.remove_class
        )
        self.remove_class_button.pack(side=tk.RIGHT, padx=10)

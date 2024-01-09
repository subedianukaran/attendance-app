import tkinter as tk
from tkinter import messagebox
import sqlite3
from tkinter import simpledialog
class MainPage:
    def __init__(self,database):
        self.root = tk.Tk()
        self.root.title("Attendance Application")
        self.root.geometry("700x450")
        self.conn = sqlite3.connect(f"{database}.db")
        self.cursor = self.conn.cursor()

        self.home_page()

    def add_new_class(self):
        new_class_name = tk.simpledialog.askstring("Add New Class", "Enter new class name:")

        if new_class_name:
            class_exists = self.check_class_exists(new_class_name)

            if class_exists:
                messagebox.showinfo("Class Exists", "Class already exists.")
            else:
                self.cursor.execute('INSERT INTO RecordList (Class) VALUES (?)', (new_class_name,))
                self.conn.commit()
                self.create_class_tables(new_class_name)
                messagebox.showinfo("Success", f"Class '{new_class_name}' added successfully.")
                self.home_frame.destroy()
                self.home_page()



                # Create new tables for the added class


    def create_class_tables(self, class_name):
        # Table for storing names of students in the class
        create_names_table_query = f'''
            CREATE TABLE IF NOT EXISTS names_{class_name} (
                RollNo INTEGER PRIMARY KEY,
                Name TEXT
            )
        '''
        self.cursor.execute(create_names_table_query)
        self.conn.commit()

        # Table for storing attendance of students in the class
        create_attendance_table_query = f'''
            CREATE TABLE IF NOT EXISTS attendance_{class_name}(
                RollNo INTEGER,
                FOREIGN KEY(RollNo) REFERENCES names_{class_name}(RollNo)
            )
        '''
        self.cursor.execute(create_attendance_table_query)
        self.conn.commit()

        messagebox.showinfo("Tables Created", f"Tables created for '{class_name}' successfully.")


    def display_classes(self):
        self.cursor.execute('SELECT Class FROM RecordList')
        classes = self.cursor.fetchall()

        for class_name in classes:
            tk.Button(self.home_frame, text=class_name[0], command=lambda cn=class_name[0].title(): self.class_details(cn),
                      width=10, height=2).pack(padx=5, pady=5)

    def remove_class(self):
        index = tk.simpledialog.askinteger("Remove Class", "Enter index of the class to remove:")  # Get index from user

        if index is not None:
            classes = self.cursor.execute('SELECT Class FROM RecordList').fetchall()

            if 0 <= index < len(classes):
                class_name = classes[index][0]
                self.cursor.execute('DELETE FROM RecordList WHERE Class=?', (class_name,))
                self.conn.commit()
                messagebox.showinfo("Success", f"Class '{class_name}' removed successfully.")
                self.home_frame.destroy()
                self.home_page()

            else:
                messagebox.showwarning("Invalid Index", "Please enter a valid index.")

    def check_class_exists(self, class_name):
        self.cursor.execute('SELECT * FROM RecordList WHERE Class=?', (class_name,))
        return self.cursor.fetchone()

    def class_details(self, class_name):
        messagebox.showinfo("Class Details", f"You selected class: '{class_name}'.")

    def refresh_display(self):
        # Clear the existing buttons and re-display classes
        for widget in self.root.winfo_children():
            widget.destroy()

        self.display_classes()

    def home_page(self):
        self.home_frame = tk.Frame(self.root)
        self.home_frame.pack(fill=tk.BOTH, expand=True)

        # Top section: "Classes" label
        label_classes = tk.Label(self.home_frame, text="Classes", font=("Arial", 24, "bold"))
        label_classes.pack(pady=20)

        # Middle section: Display Classes
        self.display_classes()  # Assuming this method displays classes in the middle of the frame
        # (Replace this line with your method to display classes)

        # Bottom section: Buttons
        button_frame = tk.Frame(self.home_frame)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        # Bottom left button
        self.add_class_button = tk.Button(button_frame, text="Add New Class", command=self.add_new_class)
        self.add_class_button.pack(side=tk.LEFT, padx=10)

        # Bottom right button
        self.remove_class_button = tk.Button(button_frame, text="Remove Class", command=self.remove_class)
        self.remove_class_button.pack(side=tk.RIGHT, padx=10)

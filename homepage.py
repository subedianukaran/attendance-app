import tkinter as tk
from tkinter import messagebox
import sqlite3
from tkinter import simpledialog

class ClassHomePage:
    def __init__(self, class_name, root,cursor, conn):
        self.class_name = class_name
        self.root = root
        self.cursor = cursor
        self.conn = conn
        pass

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
        pass

    def edit_students(self):
        pass
    def add_students(self):
        def add_students_d():
            student_names = student_entry.get()
            student_list = [name.strip() for name in student_names.split(',')]

            try:
                for name in student_list:
                    if name:
                        self.cursor.execute(f"INSERT INTO names_{self.class_name} (Name) VALUES (?)", (name,))
                        self.conn.commit()

                self.conn.close()
                messagebox.showinfo("Success", "Students added successfully.")

            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Error: {e}")

        student_window = tk.Toplevel()
        student_window.title("Add Students")

        student_label = tk.Label(student_window, text="Enter student names (separated by comma):")
        student_label.pack()

        student_entry = tk.Entry(student_window, width=40)
        student_entry.pack()

        add_button = tk.Button(student_window, text="Add", command=add_students_d)
        add_button.pack()
    def classpage(self):
        self.class_frame = tk.Frame(self.root)
        self.class_frame.pack(fill=tk.BOTH, expand=True)

        # Label for class name
        class_label = tk.Label(self.class_frame, text=self.class_name, font=("Arial", 18, "bold"))
        class_label.grid(pady=30)
        class_label.pack()

        # Buttons
        button_texts = ["Take Attendance", "Edit Records", "View Statistics",
                        "Delete Records", "View Students","Add Students", "Remove Students", "Edit Student Data"]
        button_commands = [self.take_attendance, self.edit_records, self.view_statistics, self.delete_records,
                           self.view_students, self.add_students, self.remove_students, self.edit_students]

        for i in range(0, len(button_texts), 2):
            frame = tk.Frame(self.class_frame)
            frame.pack()

            for j in range(2):
                if i + j < len(button_texts):
                    button = tk.Button(frame, text=button_texts[i + j], width=15, command=button_commands[i+j])
                    button.pack(side=tk.LEFT, padx=20, pady=20)


class MainPage:
    def __init__(self,database):
        self.root = tk.Tk()
        self.root.title("Attendance Application")
        self.root.geometry("600x450")
        self.database=database
        self.conn = sqlite3.connect(f"{self.database}.db")
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
            CREATE TABLE IF NOT EXISTS attendance_{class_name} (
                RollNo INTEGER,
                FOREIGN KEY(RollNo) REFERENCES names_{class_name} (RollNo)
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
                self.cursor.execute(f"DELETE FROM RecordList WHERE Class='{class_name}'")
                self.cursor.execute(f'DROP TABLE names_{class_name}')
                self.cursor.execute(f'DROP TABLE attendance_{class_name}')
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
        self.home_frame.destroy()
        class_page = ClassHomePage(class_name, self.root,self.cursor,self.conn)
        class_page.classpage()

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



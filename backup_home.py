import tkinter as tk
from tkinter import messagebox
import sqlite3
from tkinter import simpledialog
from datetime import datetime

class AttendanceManager:
    def __init__(self,conn,class_name):

        self.class_name = class_name
        self.conn = conn
        self.cursor = self.conn.cursor()

        self.take_attendance()


    def take_attendance(self):

        date = datetime.today().date()

        if date:
            column_check_query = f"PRAGMA table_info({self.class_name}_attendance)"
            self.cursor.execute(column_check_query)
            columns = [column[1] for column in self.cursor.fetchall()]

            if date in columns:
                messagebox.showinfo("Info", "Already taken, go to edit data to make changes.")
            else:

                self.cursor.execute(f"ALTER TABLE {self.class_name}_attendance ADD COLUMN '{date}' BIT")
                self.conn.commit()

                student_query = f"SELECT Name, RollNo FROM {self.class_name}_names ORDER BY Name"
                self.cursor.execute(student_query)
                self.students = self.cursor.fetchall()

                self.attendance_window = tk.Toplevel()
                self.attendance_window.title(f"Attendance for {date}")

                self.current_student = 0
                self.show_attendance(self.students[self.current_student], date)


    def show_attendance(self, student, date):
        name_label = tk.Label(self.attendance_window, text=f"Name of Student: {student[0]}")
        name_label.pack()

        roll_label = tk.Label(self.attendance_window, text=f"Roll No: {student[1]}")
        roll_label.pack()

        present_button = tk.Button(self.attendance_window, text="Present", command=lambda: self.mark_attendance(date, student[1], status = True))
        present_button.pack()

        absent_button = tk.Button(self.attendance_window, text="Absent", command=lambda: self.mark_attendance(date, student[1], status = False))
        absent_button.pack()


    def mark_attendance(self, date, roll_no, status):
        update_query = f"UPDATE {self.class_name}_attendance SET '{date}' = ? WHERE RollNo = ?"
        self.cursor.execute(update_query, (status, roll_no))
        self.conn.commit()

        self.current_student += 1

        if self.current_student < len(self.students):
            self.show_attendance(self.students[self.current_student], date)
        else:
            messagebox.showinfo("Info", "Attendance taken for all students.")
            self.attendance_window.destroy()


class ClassHomePage:
    def __init__(self, class_name, root,cursor, conn):
        self.class_name = class_name
        self.root = root
        self.cursor = cursor
        self.conn = conn
        pass

    def take_attendance(self):
        attendance = AttendanceManager(self.conn, self.class_name)
        attendance.take_attendance()


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
            student_list = [name.strip() for name in student_names.split(',')]
            students_not_found = []

            try:

                for name in student_list:
                    if name:
                        self.cursor.execute(f"DELETE FROM {self.class_name}_names WHERE Name = ?", (name,))
                        if self.cursor.rowcount == 0:
                            students_not_found.append(name)

                self.conn.commit()

                if students_not_found:
                    messagebox.showwarning("Students Not Found",
                                           f"The following students weren't found: {', '.join(students_not_found)}")
                else:
                    messagebox.showinfo("Success", "Students removed successfully.")

            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Error: {e}")


        student_window = tk.Toplevel()
        student_window.title("Remove Students")

        student_label = tk.Label(student_window, text="Enter student names to remove (separated by comma):")
        student_label.pack()

        student_entry = tk.Entry(student_window, width=40)
        student_entry.pack()

        remove_button = tk.Button(student_window, text="Remove", command=remove_students)
        remove_button.pack()


    def edit_students(self):
        pass


    def add_students(self):
        def add_students_d():
            student_names = student_entry.get()
            student_window.destroy()
            student_list = [name.strip() for name in student_names.split(',')]

            try:
                for name in student_list:
                    if name:
                        self.cursor.execute(f"INSERT INTO {self.class_name}_names (Name) VALUES (?)", (name,))
                        self.conn.commit()

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

        class_label = tk.Label(self.class_frame, text=self.class_name, font=("Arial", 18, "bold"))
        class_label.grid(pady=30)
        class_label.pack()

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
        self.conn = sqlite3.connect("Database.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('')
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
        create_names_table_query = f'''
            CREATE TABLE IF NOT EXISTS {class_name}_names (
                RollNo INTEGER PRIMARY KEY,
                Name TEXT
            )
        '''
        self.cursor.execute(create_names_table_query)
        self.conn.commit()

        create_attendance_table_query = f'''
            CREATE TABLE IF NOT EXISTS {class_name}_attendance (
                RollNo INTEGER,
                FOREIGN KEY(RollNo) REFERENCES {class_name}_names (RollNo)
            )
        '''
        self.cursor.execute(create_attendance_table_query)
        self.conn.commit()


    def display_classes(self):
        self.cursor.execute('SELECT class_name FROM class')
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
                self.cursor.execute(f'DROP TABLE {class_name}_names')
                self.cursor.execute(f'DROP TABLE {class_name}_attendance')
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
        self.home_frame.destroy()
        class_page = ClassHomePage(class_name, self.root,self.cursor,self.conn)
        class_page.classpage()


    def home_page(self):
        self.home_frame = tk.Frame(self.root)
        self.home_frame.pack(fill=tk.BOTH, expand=True)

        label_classes = tk.Label(self.home_frame, text="Classes", font=("Arial", 24, "bold"))
        label_classes.pack(pady=20)

        self.display_classes() 

        button_frame = tk.Frame(self.home_frame)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        self.add_class_button = tk.Button(button_frame, text="Add New Class", command=self.add_new_class)
        self.add_class_button.pack(side=tk.LEFT, padx=10)

        self.remove_class_button = tk.Button(button_frame, text="Remove Class", command=self.remove_class)
        self.remove_class_button.pack(side=tk.RIGHT, padx=10)

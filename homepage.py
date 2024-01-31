import tkinter as tk
from tkinter import messagebox
import sqlite3
from tkinter import simpledialog
from datetime import date


class AttendanceManager:
    def __init__(self,root,conn, class_id):

        self.class_id = class_id
        self.root = root
        self.conn = conn
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS attendance (attendance_id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER, attendance_date DATE, status BOOLEAN, FOREIGN KEY (student_id) REFERENCES students(student_id));"
        )
        self.conn.commit()
        self.take_attendance


    def take_attendance(self):
        self.date = date.today()
        print(self.date)
        self.cursor.execute(f"SELECT class_student.student_id, students.student_name FROM students INNER JOIN class_student ON students.student_id = class_student.student_id WHERE class_student.class_id= ?", (self.class_id,))
        self.students = self.cursor.fetchall()

        self.attendance_window = tk.TopLevel(self.root)
        self.attendance_window.title(f"Attendance for {self.date}")
        self.current_student = 0
        self.show_attendance(self.students[self.current_student])

    def show_attendance(self, student):
        self.id_label = tk.Label(self.attendance_window, text = f"{self.students[0]}")
        self.id_label.pack()

        self.name_label = tk.Label(self.attendance_window, text = f"{self.students[1]}")
        self.name_label.pack()

        self.present_button = tk.Button(self.attendance_window, text="Present", command=lambda: self.mark_attendance(self.date, student[0], "Present"))
        self.present_button.pack()

        self.absent_button = tk.Button(self.attendance_window, text="Absent", command=lambda: self.mark_attendance(self.date, student[0], "Absent"))
        self.absent_button.pack()

        

    def mark_attendance(self,student_id, val):
        if val=="Present":
            status = True
        elif val=="Absent":
            status = False

        self.cursor.execute(f"INSERT INTO attendance (student_id, attendance_date, status) VALUES (?,?,?)", (student_id, self.date, status,))
        self.conn.commit()

        self.current_student +=1

        if self.current_student < len(self.students):
            self.show_attendance(self.students[self.current_student])
        else:
            messagebox.showinfo("Info", "Attendance taken for all students.")
            self.attendance_window.destroy()



class ClassHomePage:
    def __init__(self, class_name, root, cursor, conn, user_id):
        self.class_name = class_name
        self.user_id = user_id
        self.root = root
        self.cursor = cursor
        self.conn = conn
        self.cursor.execute(f"SELECT class_id FROM classes WHERE class_name = ?", (self.class_name,))
        self.class_id = self.cursor.fetchone()[0]

    def wipepage(self):
        if hasattr(self, "viewstd_frame"):
            self.viewstd_frame.pack_forget()
        if hasattr(self, "class_frame"):
            self.class_frame.pack_forget()
        if hasattr(self, "home_frame"):
            self.home_frame.pack_forget()
        if hasattr(self, "removeclass_frame"):
            self.removeclass_frame.pack_forget()

    def edit_records(self):
        pass

    def view_statistics(self):
        pass

    def delete_records(self):
        pass

    def view_students(self):
        self.wipepage()
        self.viewstd_frame = tk.Frame(self.root)
        self.viewstd_frame.pack(fill=tk.BOTH, expand=True)
        self.title_label = tk.Label(self.viewstd_frame, text= "")
        self.title_label.pack()
        self.title_label = tk.Label(self.viewstd_frame, text= "Students Data", font=("Arial", 15, "bold"))
        self.title_label.pack()

        self.cursor.execute(f"SELECT class_student.student_id, students.student_name FROM students INNER JOIN class_student ON students.student_id = class_student.student_id WHERE class_student.class_id= ?", (self.class_id,))
        self.students = self.cursor.fetchall()

        # Create a treeview
        self.tree = tk.ttk.Treeview(self.viewstd_frame, columns=('ID', 'Name'), show='headings')

        # Define column headings
        self.tree.heading('ID', text='Student ID')
        self.tree.heading('Name', text='Name')

        # Add data to the treeview
        for student in self.students:
            self.tree.insert('', 'end', values=student)

        # Pack the treeview
        self.tree.pack()

        button_frame = tk.Frame(self.viewstd_frame)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        self.add_class_button = tk.Button(
            button_frame, text="Add Students", command=self.add_students
        )
        self.add_class_button.pack(side=tk.LEFT, padx=10)

        self.remove_class_button = tk.Button(
            button_frame, text="Remove Students", command=self.remove_students
        )
        self.remove_class_button.pack(side=tk.RIGHT, padx=10)
        self.button_back = tk.Button(
            self.viewstd_frame,
            text="Back",
            command=lambda: self.classpage(),
        )
        self.button_back.pack(pady=10)



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
                            "SELECT student_id FROM students WHERE student_name = ?",
                            (name,)
                        )
                        student_id = self.cursor.fetchone()[0]
                        print('student_id is updated')
                        print(student_id)
                        self.conn.commit()
                        self.cursor.execute(
                            f"DELETE FROM students WHERE student_id = ?", (student_id,)
                        )
                        self.conn.commit()
                        self.cursor.execute(
                            f"DELETE FROM class_student WHERE student_id = ?",
                            (student_id,)
                        )
                        self.conn.commit()
                        if self.cursor.rowcount == 0:
                            students_not_found.append(name)

                self.conn.commit()

                self.viewstd_frame.pack_forget()
                self.view_students()

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

    def take_attendance(self):
        attendance = AttendanceManager(self.root,self.conn,self.class_id)
        attendance.take_attendance()

    def add_students(self):
        def add_students_d():
            student_names = student_entry.get()
            student_window.destroy()
            student_list = [name.strip() for name in student_names.split(",")]

            try:
                for name in student_list:
                    if name:
                        self.cursor.execute(
                            f"INSERT INTO students (student_name) VALUES (?)", (name,)
                        )
                        self.conn.commit()
                        self.cursor.execute(f"SELECT student_id FROM students WHERE student_name = ?", (name,))
                        self.student_id = self.cursor.fetchone()[0]
                        print(self.student_id)
                        self.cursor.execute(
                            f"""INSERT INTO class_student (class_id, student_id)
                                VALUES (?, ?);
                            """,
                            (self.class_id, self.student_id),
                        )
                        self.conn.commit()

                messagebox.showinfo("Success", "Students added successfully.")
                self.viewstd_frame.pack_forget()
                self.view_students()


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
        self.wipepage()
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
        ]
        button_commands = [
            self.take_attendance,
            self.edit_records,
            self.view_statistics,
            self.delete_records,
            self.view_students,
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
    def __init__(self, user_id):
        self.root = tk.Tk()
        self.root.title("Attendance Application")
        self.root.geometry("600x450")
        self.conn = sqlite3.connect("Database.db")
        self.cursor = self.conn.cursor()
        self.user_id = user_id
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

    def wipepage(self):
        if hasattr(self, "home_frame"):
            self.home_frame.pack_forget()
        if hasattr(self, "viewstd_frame"):
            self.viewstd_frame.pack_forget()
        if hasattr(self, "class_frame"):
            self.class_frame.pack_forget()
        if hasattr(self, "removeclass_frame"):
            self.removeclass_frame.pack_forget()

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
    VALUES ((?), (SELECT class_id FROM classes WHERE class_name = ?));
""",
                    (self.user_id, self.new_class_name),
                )
                self.conn.commit()
                messagebox.showinfo(
                    "Success", f"Class '{self.new_class_name}' added successfully."
                )
                self.home_frame.destroy()
                self.home_page()

    def display_classes(self):
        self.cursor.execute(
            "SELECT class_name FROM classes INNER JOIN user_class ON classes.class_id = user_class.class_id WHERE user_class.user_id = ?",
            (self.user_id,),
        )
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
        selected_class_id = int(self.rentry_index.get())

        self.cursor.execute(
            "SELECT * FROM classes INNER JOIN user_class on classes.class_id = user_class.class_id WHERE user_class.user_id = ?",
            (self.user_id,),
        )
        classes = self.cursor.fetchall()

        for classvar in classes:
            if classvar[0] == selected_class_id:

                self.cursor.execute(
                    "DELETE FROM classes WHERE class_id=?", (selected_class_id,)
                )
                self.conn.commit()
                self.cursor.execute(
                    "DELETE FROM user_class WHERE class_id=?", (selected_class_id,)
                )
                self.conn.commit()
                # left to remove students from those classes
                self.removeclass_frame.destroy()
                self.remove_class_page()

    def remove_class_page(self):
        self.wipepage()

        self.removeclass_frame = tk.Frame(self.root)
        self.removeclass_frame.pack(fill=tk.BOTH, expand=True)

        label_instructions = tk.Label(
            self.removeclass_frame, text="Enter class_id of class to remove:"
        )
        label_instructions.pack()

        self.cursor.execute(
            "SELECT * FROM classes INNER JOIN user_class ON classes.class_id = user_class.class_id where user_id = ?",
            (self.user_id,),
        )  
        classes = self.cursor.fetchall()

        for classvar in classes:
            label_text = f"{classvar[0]}: {classvar[1]}"
            print(classvar[0])
            tk.Label(self.removeclass_frame, text=label_text).pack()

        self.rentry_index = tk.Entry(self.removeclass_frame)
        self.rentry_index.pack()

        button_remove = tk.Button(
            self.removeclass_frame, text="Remove", command=lambda: self.remove_class()
        )
        button_remove.pack()

        button_return_page = tk.Button(
            self.removeclass_frame, text="Back", command=lambda: self.home_page()
        )
        button_return_page.pack()

    def class_details(self, class_name):
        self.wipepage()
        class_page = ClassHomePage(class_name, self.root, self.cursor, self.conn, self.user_id)
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
            button_frame, text="Remove Class", command=self.remove_class_page
        )
        self.remove_class_button.pack(side=tk.RIGHT, padx=10)
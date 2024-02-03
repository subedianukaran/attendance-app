import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import sqlite3
from datetime import date
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class AttendanceManager:
    def __init__(self,root,conn, class_id):

        self.class_id = class_id
        self.root = root
        self.conn = conn
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS attendance (attendance_id INTEGER PRIMARY KEY AUTOINCREMENT, class_id INTEGER, student_id INTEGER, attendance_date DATE, status BOOLEAN, FOREIGN KEY (class_id) REFERENCES class_student(class_id), FOREIGN KEY (student_id) REFERENCES students(student_id));"
        )
        self.conn.commit()
        self.take_attendance

############################ Check Attendance & Take Attendance #########################################################

    def take_attendance(self):
        self.date = date.today()
        if self.date:
            self.cursor.execute(
                "SELECT 1 FROM attendance INNER JOIN class_student ON attendance.student_id = class_student.student_id WHERE class_student.class_id = ? AND attendance.attendance_date = ? LIMIT 1",
                (self.class_id,self.date,),
            )
            self.conn.commit()
            existing_date = self.cursor.fetchone()
            if existing_date:
                messagebox.showinfo("Attendance Taken", "Attendance already taken for today. Go to edit records to edit")
            else:
                self.cursor.execute(f"SELECT class_student.student_id, students.student_name FROM students INNER JOIN class_student ON students.student_id = class_student.student_id WHERE class_student.class_id= ?", (self.class_id,))
                self.students = self.cursor.fetchall()
                self.stdid_array=[item[0] for item in self.students]
                self.stdname_array=[item[1] for item in self.students]
       
                self.attendance_window = tk.Toplevel()
                self.attendance_window.geometry("300x200")
                self.attendance_window.title(f"Attendance for {self.date}")
                self.current_student = 0
                self.show_attendance()

######################### UI for taking Attendance ######################################################################
                
    def show_attendance(self):
        if hasattr(self, "attendance_frame"):
            self.attendance_frame.pack_forget()
        self.attendance_frame = tk.Frame(self.attendance_window)
        self.attendance_frame.pack(fill=tk.BOTH, expand=True)
        self.id_label = tk.Label(self.attendance_frame, text = f"Student ID: {self.stdid_array[self.current_student]}")
        self.id_label.pack()

        self.name_label = tk.Label(self.attendance_frame, text = f"Name: {self.stdname_array[self.current_student]}")
        self.name_label.pack()

        self.present_button = tk.Button(self.attendance_frame, text="Present", command=lambda: self.mark_attendance(self.stdid_array[self.current_student], "Present"))
        self.present_button.pack(side=tk.RIGHT, padx=20)

        self.absent_button = tk.Button(self.attendance_frame, text="Absent", command=lambda: self.mark_attendance(self.stdid_array[self.current_student], "Absent"))
        self.absent_button.pack(side=tk.LEFT, padx=20)
        
###################### Mark Attendance in the Database ##############################################################
        
    def mark_attendance(self,student_id, val):
        if val=="Present":
            status = True
        elif val=="Absent":
            status = False

        self.cursor.execute(f"INSERT INTO attendance (class_id, student_id, attendance_date, status) VALUES (?,?,?,?)", (self.class_id,student_id, self.date, status,))
        self.conn.commit()

        self.current_student +=1

        if self.current_student < len(self.students):
            self.show_attendance()
        else:
            self.attendance_window.destroy()
            messagebox.showinfo("Info", "Attendance taken for all students.")


class ClassHomePage:
    def __init__(self, class_name, root, cursor, conn, user_id):
        self.class_name = class_name
        self.user_id = user_id
        self.root = root
        self.date = date.today()
        self.cursor = cursor
        self.conn = conn
        self.conn.commit()
        self.cursor.execute(f"SELECT class_id FROM classes WHERE class_name = ?", (self.class_name,))
        self.class_id = self.cursor.fetchone()[0]

    def logout(self):
        self.root.destroy()
        import login
    
#################### Sorting Algorithm ##############################################################################

    def selection_sort(self,record, sort_by):
        n = len(record)

        if sort_by == "Student ID":
            sortby = 0
        elif sort_by == "Student Name":
            sortby = 1
        else:
            sortby = 0

        for i in range(n - 1):
            min = i
            for j in range(i + 1, n):
                if record[j][sortby] < record[min][sortby]:
                    min = j

            record[i], record[min] = record[min], record[i]
        
        self.update_treeview()

    def wipepage(self):
        if hasattr(self, "viewstd_frame"):
            self.viewstd_frame.pack_forget()
        if hasattr(self, "class_frame"):
            self.class_frame.pack_forget()
        if hasattr(self, "home_frame"):
            self.home_frame.pack_forget()
        if hasattr(self, "removeclass_frame"):
            self.removeclass_frame.pack_forget()
        if hasattr(self, "edit_frame"):
            self.edit_frame.pack_forget()

################################# Edit Record Button Function ##########################################
            
    def edit_records(self):
        def edit_record(event):
            selected_item = self.tree.selection()
            if not selected_item:
                return

            values = self.tree.item(selected_item, 'values')

            self.selected_id = values[0]
            displayed_status = "Present" if values[2] == 1 else "Absent"
            self.status_var.set(displayed_status)

            selected_name = values[1]
            self.selected_name_label.config(text=f"Student: {selected_name}")
        
        def update_record():
            if not hasattr(self, 'selected_id'):
                return

            displayed_status = self.status_var.get()

            new_status_value = self.status_display_map.get(displayed_status, 0)

            self.cursor.execute('UPDATE attendance SET status=? WHERE student_id=?', (new_status_value, self.selected_id))
            self.conn.commit()

            refresh_treeview()
        
        def refresh_treeview():
            for child in self.tree.get_children():
                self.tree.delete(child)

            self.cursor.execute('''
                SELECT students.student_id, students.student_name, attendance.status 
                FROM attendance 
                INNER JOIN students ON attendance.student_id = students.student_id WHERE attendance.class_id = ? AND attendance.attendance_date = ?
            ''', (self.class_id,self.date,))
            data = self.cursor.fetchall()


            for row in data:
                displayed_status = "Present" if row[2] == 1 else "Absent"
                row_display = (row[0], row[1], displayed_status)
                self.tree.insert('', 'end', values=row_display)    

        self.wipepage()
        self.edit_frame= tk.Frame(self.root)
        self.edit_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(self.edit_frame, columns=('Student ID', 'Student Name', 'Status'), show='headings')
        self.tree.heading('Student ID', text='Student ID')
        self.tree.heading('Student Name', text='Student Name')
        self.tree.heading('Status', text='Status')

        self.tree.bind("<Double-1>", edit_record)

        self.tree.pack(pady=10)

        self.entry_frame = tk.Frame(self.edit_frame)
        self.entry_frame.pack(pady=5)

        self.selected_name_label = tk.Label(self.entry_frame, text="Selected Student Name:")
        self.selected_name_label.grid(row=0, column=0, padx=10, pady=5)

        self.status_var = tk.StringVar()
        self.status_display_map = {"Present": 1, "Absent": 0}
        self.status_entry = ttk.Combobox(self.entry_frame, textvariable=self.status_var, values=["Absent", "Present"], state="readonly")
        self.status_entry.grid(row=0, column=1, pady=5)

        self.update_button = tk.Button(self.edit_frame, text="Update", command=update_record)
        self.update_button.pack(pady=5)
        self.button_back = tk.Button(
            self.edit_frame,
            text="Back",
            command=lambda: self.classpage(),
        )
        self.button_back.pack(pady=10)

        refresh_treeview()

############################### View Statistics Button Function ####################################################################

    def view_statistics(self):
        self.cursor.execute(
            "SELECT COUNT(*) FROM attendance WHERE class_id = ? AND attendance_date = ? AND status = 1",
            (self.class_id, self.date),
        )
        present_count = self.cursor.fetchone()[0]
        self.conn.commit()
        self.cursor.execute(
            "SELECT COUNT(*) FROM attendance WHERE class_id = ? AND attendance_date = ? AND status = 0",
            (self.class_id, self.date),
        )
        absent_count = self.cursor.fetchone()[0]
        self.conn.commit()
        labels = ['Present', 'Absent']
        sizes = [present_count, absent_count]

        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')      
        ax.set_title("Attendance Distribution", fontsize=16)

        pie_chart_window = tk.Toplevel(self.root)
        pie_chart_window.title("Attendance Pie Chart")
        canvas = FigureCanvasTkAgg(fig, master=pie_chart_window)
        canvas.get_tk_widget().pack()
        canvas.draw()

        plt.close(fig) 

############################### Manage Students Button Function #################################################

    def manage_students(self):
        self.wipepage()
        self.viewstd_frame = tk.Frame(self.root)
        self.viewstd_frame.pack(fill=tk.BOTH, expand=True)

        self.cursor.execute(f"SELECT class_student.student_id, students.student_name FROM students INNER JOIN class_student ON students.student_id = class_student.student_id WHERE class_student.class_id= ?", (self.class_id,))
        self.students = self.cursor.fetchall()

        self.sort_by_variable = tk.StringVar()
        sort_combobox = ttk.Combobox(self.viewstd_frame, textvariable=self.sort_by_variable, values=["Student ID", "Student Name"])
        sort_combobox.set("Sort by")
        sort_combobox.pack()
        sort_combobox.bind("<<ComboboxSelected>>", self.sort_students)


        self.title_label = tk.Label(self.viewstd_frame, text= "")
        self.title_label.pack()
        self.title_label = tk.Label(self.viewstd_frame, text= "Students Data", font=("Arial", 15, "bold"))
        self.title_label.pack()
        self.tree = tk.ttk.Treeview(self.viewstd_frame, columns=('ID', 'Name'), show='headings')

        self.tree.heading('ID', text='Student ID')
        self.tree.heading('Name', text='Name')

        for student in self.students:
            self.tree.insert('', 'end', values=student)

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

    def sort_students(self, event):
        sort_by = self.sort_by_variable.get()
        if sort_by in ["Student ID", "Student Name"]:
            self.selection_sort(self.students, sort_by)
            self.update_treeview()

    def update_treeview(self):
        for child in self.tree.get_children():
            self.tree.delete(child)

        for student in self.students:
            self.tree.insert('', 'end', values=student)

########################### Remove Existing Students ####################################################

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
                self.manage_students()

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

############################# Add New Students ##########################################################
        
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
                        self.cursor.execute(
                            f"""INSERT INTO class_student (class_id, student_id)
                                VALUES (?, ?);
                            """,
                            (self.class_id, self.student_id),
                        )
                        self.conn.commit()

                messagebox.showinfo("Success", "Students added successfully.")
                self.viewstd_frame.pack_forget()
                self.manage_students()


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

############################### Class Page UI ####################################################################

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
            "Manage Students",
        ]
        button_commands = [
            self.take_attendance,
            self.edit_records,
            self.view_statistics,
            self.manage_students,
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

        logout_button = tk.Button(
            self.class_frame, text="Log Out", command=lambda: self.logout()
        )
        logout_button.pack(side=tk.BOTTOM, pady=10)


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

    def logout(self):
        self.root.destroy()
        import login

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
                command=lambda cn=class_name[0]: self.class_details(cn),
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

################################### Home Page UI #################################################################3

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

        logout_button = tk.Button(
            button_frame, text="Log Out", command=lambda: self.logout()
        )
        logout_button.pack(side=tk.BOTTOM)
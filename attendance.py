import tkinter as tk
from tkinter import simpledialog, messagebox
import sqlite3

class AttendanceManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Take Attendance")

        self.conn = sqlite3.connect("baburam.db")
        self.cursor = self.conn.cursor()

        self.take_attendance_button = tk.Button(self.root, text="Take Attendance", command=self.take_attendance)
        self.take_attendance_button.pack()

        self.root.mainloop()

    def take_attendance(self):
        date = simpledialog.askstring("Input", "Enter date for attendance (YYYY-MM-DD):")

        if date:
            column_check_query = f"PRAGMA table_info(Class_9_attendance)"
            self.cursor.execute(column_check_query)
            columns = [column[1] for column in self.cursor.fetchall()]

            if date in columns:
                messagebox.showinfo("Info", "Already taken, go to edit data to make changes.")
            else:
                self.cursor.execute(f"ALTER TABLE Class_9_attendance ADD COLUMN '{date}' TEXT")
                self.conn.commit()

                student_query = f"SELECT Name, RollNo FROM Class_9_names ORDER BY Name"
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

        present_button = tk.Button(self.attendance_window, text="Present", command=lambda: self.mark_attendance(date, student[1], "Present"))
        present_button.pack()

        absent_button = tk.Button(self.attendance_window, text="Absent", command=lambda: self.mark_attendance(date, student[1], "Absent"))
        absent_button.pack()

    def mark_attendance(self, date, roll_no, status):
        self.classname = "Class_9"
        update_query = f"UPDATE {self.classname}_attendance SET '{date}' = ? WHERE RollNo = ?"
        self.cursor.execute(update_query, (status, roll_no))
        self.conn.commit()

        self.current_student += 1

        if self.current_student < len(self.students):
            self.show_attendance(self.students[self.current_student], date)
        else:
            messagebox.showinfo("Info", "Attendance taken for all students.")
            self.attendance_window.destroy()

if __name__ == "__main__":
    AttendanceManager()

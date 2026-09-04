import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from db_connect import create_connection
from mysql.connector import Error

class AshscomGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ashscom Management System")
        self.root.geometry("800x600")
        self.root.configure(bg="#ADFFB1")

        header_canvas = tk.Canvas(self.root, height=100, highlightthickness=0)
        header_canvas.pack(fill="x")

        logo1_img = Image.open("ateneo1.png").resize((65, 65))
        self.logo1 = ImageTk.PhotoImage(logo1_img)

        logo2_img = Image.open("ashscom.png").resize((90, 90))
        self.logo2 = ImageTk.PhotoImage(logo2_img)

        def redraw_header(event):
            width = event.width
            height = 100
            header_canvas.delete("all")  # clear everything and redraw fresh

            # Gradient
            r1, g1, b1 = self.root.winfo_rgb("#D4FFD9")
            r2, g2, b2 = self.root.winfo_rgb("#7ED985")
            for i in range(height):
                nr = int(r1 + (r2 - r1) * i / height) >> 8
                ng = int(g1 + (g2 - g1) * i / height) >> 8
                nb = int(b1 + (b2 - b1) * i / height) >> 8
                color = f'#{nr:02x}{ng:02x}{nb:02x}'
                header_canvas.create_line(0, i, width, i, fill=color)

            # Logos
            header_canvas.create_image(35, 50, image=self.logo1, anchor="w")
            header_canvas.create_image(115, 50, image=self.logo2, anchor="w")

            # Text - right-aligned using the CURRENT width, every time
            right_x = width - 15
            header_canvas.create_text(right_x, 28, text="Ateneo De Davao University Senior High School",
                                       font=("Segoe UI", 12, "bold"), fill="#004202", anchor="e")
            header_canvas.create_text(right_x, 48, text="Commission on Elections",
                                       font=("Segoe UI", 12, "bold"), fill="#004202", anchor="e")
            header_canvas.create_text(right_x, 75, text="ASHSCOM MANAGEMENT SYSTEM",
                                       font=("Segoe UI", 23, "bold"), fill="#004202", anchor="e")

        header_canvas.bind("<Configure>", redraw_header)

        divider = tk.Frame(self.root, bg="darkgreen", height=3)
        divider.pack(fill="x")

        # Create a connection to the database
        self.connection = create_connection()
        if not self.connection or not self.connection.is_connected():
            messagebox.showerror("Database Error", "Failed to connect to the database.")
            self.root.destroy()
            return

        # Create students table if it doesn't exist
        self.create_students_table()

        # Create a notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both')

        # Create tabs
        self.create_home_tab()
        self.create_users_tab()
        self.create_settings_tab()

    def create_students_table(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    grade_level VARCHAR(50) NOT NULL,
                    section VARCHAR(50) NOT NULL
                )
            """)
            self.connection.commit()
            cursor.close()
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to create table: {e}")

    def create_home_tab(self):
        home_frame = ttk.Frame(self.notebook)
        self.notebook.add(home_frame, text="Home")

        # Add content to the Home tab
        welcome_label = ttk.Label(home_frame, text="Welcome to Ashscom Management System", font=("Arial", 16))
        welcome_label.pack(pady=20)

    def create_users_tab(self):
        users_frame = ttk.Frame(self.notebook)
        self.notebook.add(users_frame, text="Users")

        # Create a LabelFrame for the Add Student section
        add_student_frame = ttk.LabelFrame(users_frame, text="Add Student")
        add_student_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Form fields
        ttk.Label(add_student_frame, text="Student Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.name_entry = ttk.Entry(add_student_frame, width=30)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(add_student_frame, text="Grade Level:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.grade_entry = ttk.Entry(add_student_frame, width=30)
        self.grade_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(add_student_frame, text="Section:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.section_entry = ttk.Entry(add_student_frame, width=30)
        self.section_entry.grid(row=2, column=1, padx=5, pady=5)

        # Add Student button
        ttk.Button(add_student_frame, text="Add Student", command=self.add_student).grid(row=3, column=0, columnspan=2, pady=10)

        # Treeview to display students
        tree_frame = ttk.Frame(add_student_frame)
        tree_frame.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        add_student_frame.grid_rowconfigure(4, weight=1)
        add_student_frame.grid_columnconfigure(1, weight=1)

        # Scrollbars
        tree_scroll_y = ttk.Scrollbar(tree_frame)
        tree_scroll_y.pack(side="right", fill="y")
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal")
        tree_scroll_x.pack(side="bottom", fill="x")

        # Treeview
        self.student_tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set, selectmode="browse")
        self.student_tree.pack(fill="both", expand=True)

        tree_scroll_y.config(command=self.student_tree.yview)
        tree_scroll_x.config(command=self.student_tree.xview)

        # Define columns
        self.student_tree['columns'] = ("id", "name", "grade_level", "section")
        self.student_tree.column("#0", width=0, stretch=tk.NO)  # hidden column
        self.student_tree.column("id", width=50, anchor=tk.CENTER)
        self.student_tree.column("name", width=150, anchor=tk.W)
        self.student_tree.column("grade_level", width=80, anchor=tk.CENTER)
        self.student_tree.column("section", width=80, anchor=tk.CENTER)

        # Headings
        self.student_tree.heading("#0", text="", anchor=tk.W)
        self.student_tree.heading("id", text="ID", anchor=tk.CENTER)
        self.student_tree.heading("name", text="Name", anchor=tk.CENTER)
        self.student_tree.heading("grade_level", text="Grade Level", anchor=tk.CENTER)
        self.student_tree.heading("section", text="Section", anchor=tk.CENTER)

        # Buttons for update and delete
        button_frame = ttk.Frame(add_student_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=5)

        self.update_btn = ttk.Button(button_frame, text="Update Selected", command=self.update_student, state="disabled")
        self.update_btn.pack(side="left", padx=5)

        self.delete_btn = ttk.Button(button_frame, text="Delete Selected", command=self.delete_student, state="disabled")
        self.delete_btn.pack(side="left", padx=5)

        # Bind treeview selection
        self.student_tree.bind("<<TreeviewSelect>>", self.on_student_select)

        # Load initial data
        self.load_students()

    def create_settings_tab(self):
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="Assignment")

        # Add content to the Assignment tab
        settings_label = ttk.Label(settings_frame, text="Assign Members to Task", font=("Arial", 16))
        settings_label.pack(pady=20)

    def load_students(self):
        # Clear the treeview
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT id, name, grade_level, section FROM students")
            rows = cursor.fetchall()
            for row in rows:
                self.student_tree.insert("", tk.END, values=row)
            cursor.close()
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to load students: {e}")

    def add_student(self):
        name = self.name_entry.get().strip()
        grade = self.grade_entry.get().strip()
        section = self.section_entry.get().strip()
        if not name:
            messagebox.showwarning("Input Error", "Student name is required.")
            return
        if not grade:
            messagebox.showwarning("Input Error", "Grade level is required.")
            return
        if not section:
            messagebox.showwarning("Input Error", "Section is required.")
            return
        try:
            cursor = self.connection.cursor()
            cursor.execute("INSERT INTO students (name, grade_level, section) VALUES (%s, %s, %s)", (name, grade, section))
            self.connection.commit()
            cursor.close()
            messagebox.showinfo("Success", "Student added successfully.")
            self.clear_form()
            self.load_students()
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to add student: {e}")

    def clear_form(self):
        self.name_entry.delete(0, tk.END)
        self.grade_entry.delete(0, tk.END)
        self.section_entry.delete(0, tk.END)

    def on_student_select(self, event):
        selected = self.student_tree.focus()
        if selected:
            values = self.student_tree.item(selected, 'values')
            if values:
                # Populate form with selected student's data
                self.name_entry.delete(0, tk.END)
                self.name_entry.insert(0, values[1])
                self.grade_entry.delete(0, tk.END)
                self.grade_entry.insert(0, values[2])
                self.section_entry.delete(0, tk.END)
                self.section_entry.insert(0, values[3])
                # Enable update and delete buttons
                self.update_btn.config(state="normal")
                self.delete_btn.config(state="normal")
        else:
            self.clear_form()
            self.update_btn.config(state="disabled")
            self.delete_btn.config(state="disabled")

    def update_student(self):
        selected = self.student_tree.focus()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a student to update.")
            return
        values = self.student_tree.item(selected, 'values')
        student_id = values[0]
        name = self.name_entry.get().strip()
        grade = self.grade_entry.get().strip()
        section = self.section_entry.get().strip()
        if not name:
            messagebox.showwarning("Input Error", "Student name is required.")
            return
        if not grade:
            messagebox.showwarning("Input Error", "Grade level is required.")
            return
        if not section:
            messagebox.showwarning("Input Error", "Section is required.")
            return
        try:
            cursor = self.connection.cursor()
            cursor.execute("UPDATE students SET name=%s, grade_level=%s, section=%s WHERE id=%s", (name, grade, section, student_id))
            self.connection.commit()
            cursor.close()
            messagebox.showinfo("Success", "Student updated successfully.")
            self.clear_form()
            self.load_students()
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to update student: {e}")

    def delete_student(self):
        selected = self.student_tree.focus()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a student to delete.")
            return
        values = self.student_tree.item(selected, 'values')
        student_id = values[0]
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this student?"):
            try:
                cursor = self.connection.cursor()
                cursor.execute("DELETE FROM students WHERE id=%s", (student_id,))
                self.connection.commit()
                cursor.close()
                messagebox.showinfo("Success", "Student deleted successfully.")
                self.clear_form()
                self.load_students()
            except Error as e:
                messagebox.showerror("Database Error", f"Failed to delete student: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = AshscomGUI(root)
    root.mainloop()


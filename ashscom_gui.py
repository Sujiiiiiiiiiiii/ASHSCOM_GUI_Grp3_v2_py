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
        self.setup_styles()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TLabelframe.Label", font=("Segoe UI", 12, "bold"), foreground="#004202")
        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("TEntry", padding=6)

        style.configure("Add.TButton", font=("Segoe UI", 10, "bold"), padding=8, background="#7ED985", foreground="#004202")
        style.map("Add.TButton", background=[("active", "#5FC46B")])

        style.configure("Update.TButton", font=("Segoe UI", 10, "bold"), padding=8, background="#FFD966", foreground="#5C4400")
        style.map("Update.TButton", background=[("active", "#E6C25C")])

        style.configure("Delete.TButton", font=("Segoe UI", 10, "bold"), padding=8, background="#F27C7C", foreground="#5C0000")
        style.map("Delete.TButton", background=[("active", "#D96666")])

        style.configure("Treeview", font=("Segoe UI", 10), rowheight=28)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#7ED985", foreground="#004202")
        style.map("Treeview.Heading", background=[("active", "#7ED985")])

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

        divider = tk.Frame(self.root, bg="#004202", height=3)
        divider.pack(fill="x")

        # Create a connection to the database
        self.connection = create_connection()
        if not self.connection or not self.connection.is_connected():
            messagebox.showerror("Database Error", "Failed to connect to the database.")
            self.root.destroy()
            return

        # Create a notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both')

        # Create tabs
        self.create_home_tab()
        self.create_users_tab()
        self.create_settings_tab()

    def create_home_tab(self):
        home_frame = ttk.Frame(self.notebook)
        self.notebook.add(home_frame, text="Home")

        # Add content to the Home tab
        welcome_label = ttk.Label(home_frame, text="Welcome to Ashscom Management System", font=("Arial", 16))
        welcome_label.pack(pady=20)

    def create_users_tab(self):
        users_frame = ttk.Frame(self.notebook)
        self.notebook.add(users_frame, text="Users")

        add_student_frame = ttk.LabelFrame(users_frame, text="Add Student")
        add_student_frame.pack(fill="both", expand=True, padx=15, pady=15)

        ttk.Label(add_student_frame, text="Student Name:").grid(row=1, column=0, padx=8, pady=8, sticky="w")
        self.name_entry = ttk.Entry(add_student_frame, width=30)
        self.name_entry.grid(row=1, column=1, padx=8, pady=8)

        ttk.Label(add_student_frame, text="Grade Level:").grid(row=2, column=0, padx=8, pady=8, sticky="w")
        self.grade_entry = ttk.Entry(add_student_frame, width=30)
        self.grade_entry.grid(row=2, column=1, padx=8, pady=8)

        ttk.Label(add_student_frame, text="Section:").grid(row=3, column=0, padx=8, pady=8, sticky="w")
        self.section_entry = ttk.Entry(add_student_frame, width=30)
        self.section_entry.grid(row=3, column=1, padx=8, pady=8)

        ttk.Button(add_student_frame, text="+ Add Student", style="Add.TButton",
                   command=self.add_student).grid(row=4, column=0, columnspan=2, pady=12)

        # Treeview section
        tree_frame = ttk.Frame(add_student_frame)
        tree_frame.grid(row=5, column=0, columnspan=2, padx=8, pady=8, sticky="nsew")
        add_student_frame.grid_rowconfigure(5, weight=1)
        add_student_frame.grid_columnconfigure(1, weight=1)

        tree_scroll_y = ttk.Scrollbar(tree_frame)
        tree_scroll_y.pack(side="right", fill="y")
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal")
        tree_scroll_x.pack(side="bottom", fill="x")

        self.student_tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll_y.set,
                                          xscrollcommand=tree_scroll_x.set, selectmode="browse")
        self.student_tree.pack(fill="both", expand=True)

        tree_scroll_y.config(command=self.student_tree.yview)
        tree_scroll_x.config(command=self.student_tree.xview)

        self.student_tree['columns'] = ("id", "name", "grade_level", "section")
        self.student_tree.column("#0", width=0, stretch=tk.NO)
        self.student_tree.column("id", width=50, anchor=tk.CENTER)
        self.student_tree.column("name", width=180, anchor=tk.W)
        self.student_tree.column("grade_level", width=100, anchor=tk.CENTER)
        self.student_tree.column("section", width=100, anchor=tk.CENTER)

        self.student_tree.heading("#0", text="", anchor=tk.W)
        self.student_tree.heading("id", text="ID", anchor=tk.CENTER)
        self.student_tree.heading("name", text="Name", anchor=tk.CENTER)
        self.student_tree.heading("grade_level", text="Grade Level", anchor=tk.CENTER)
        self.student_tree.heading("section", text="Section", anchor=tk.CENTER)

        # Alternating row stripes for readability
        self.student_tree.tag_configure("evenrow", background="#F3FFF4")
        self.student_tree.tag_configure("oddrow", background="#FFFFFF")

        button_frame = ttk.Frame(add_student_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=10)

        self.update_btn = ttk.Button(button_frame, text="Update Selected", style="Update.TButton",
                                      command=self.update_student, state="disabled")
        self.update_btn.pack(side="left", padx=6)

        self.delete_btn = ttk.Button(button_frame, text="Delete Selected", style="Delete.TButton",
                                      command=self.delete_student, state="disabled")
        self.delete_btn.pack(side="left", padx=6)

        self.student_tree.bind("<<TreeviewSelect>>", self.on_student_select)

        self.load_students()

    def create_settings_tab(self):
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="Assignment")

        # Add content to the Assignment tab
        settings_label = ttk.Label(settings_frame, text="Assign Members to Task", font=("Arial", 16))
        settings_label.pack(pady=20)

    def load_students(self):
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT StudentID, StudentName, GradeLevel, Section FROM Student")
            rows = cursor.fetchall()
            for i, row in enumerate(rows):
                tag = "evenrow" if i % 2 == 0 else "oddrow"
                self.student_tree.insert("", tk.END, values=row, tags=(tag,))
            cursor.close()
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to load students: {e}")

# Student management methods
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
            cursor.execute("INSERT INTO Student (StudentName, GradeLevel, Section) VALUES (%s, %s, %s)", (name, grade, section))
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
            cursor.execute("UPDATE Student SET StudentName=%s, GradeLevel=%s, Section=%s WHERE StudentID=%s", (name, grade, section, student_id))
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
                cursor.execute("DELETE FROM Student WHERE StudentID=%s", (student_id,))
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


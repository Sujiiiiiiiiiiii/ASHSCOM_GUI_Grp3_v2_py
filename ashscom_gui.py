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
        self.root.configure(bg="#F7FFF9")

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Clean white/soft background instead of default gray
        style.configure("TFrame", background="#F7FFF9")
        style.configure("TLabelframe", background="#F7FFF9", bordercolor="#7ED985")
        style.configure("TLabel", background="#F7FFF9", font=("Segoe UI", 10))
        style.configure("TNotebook", background="#F7FFF9")
        style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=[12, 6])

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
                                       font=("Segoe UI", 12, "bold"), fill="#017103", anchor="e")
            header_canvas.create_text(right_x, 48, text="Commission on Elections",
                                       font=("Segoe UI", 12, "bold"), fill="#017103", anchor="e")
            header_canvas.create_text(right_x, 75, text="ASHSCOM MANAGEMENT SYSTEM",
                                       font=("Segoe UI", 23, "bold"), fill="#005901", anchor="e")

        header_canvas.bind("<Configure>", redraw_header)

        divider = tk.Frame(self.root, bg="#7ED985", height=3)
        divider.pack(fill="x")

        # Create a connection to the database
        self.connection = create_connection()
        if not self.connection or not self.connection.is_connected():
            messagebox.showerror("Database Error", "Failed to connect to the database.")
            self.root.destroy()
            return

        # --- Sidebar + Content layout (replaces Notebook tabs) ---
        body_frame = ttk.Frame(self.root)
        body_frame.pack(expand=True, fill="both")

        sidebar = tk.Frame(body_frame, bg="#7ED985", width=230)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        content_frame = ttk.Frame(body_frame)
        content_frame.pack(side="right", expand=True, fill="both")

        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)

        self.pages = {}
        self.nav_buttons = {}
        self.nav_accents = {}
        self.nav_buttons_active = "home"

        def show_page(name):
            self.pages[name].tkraise()
            self.nav_buttons_active = name
            for key, b in self.nav_buttons.items():
                b.config(bg="#004202", fg="white")
                self.nav_accents[key].config(bg="#7ED985")
            self.nav_buttons[name].config(bg="#7ED985", fg="#000000")
            self.nav_accents[name].config(bg="#004202")

        nav_buttons = [("👥  Students", "students"), ("➕  Add Student", "add_student"), ("📋  Tasks/Assignments", "task/assignment")]
        for label, key in nav_buttons:
            row = tk.Frame(sidebar, bg="#004202")
            row.pack(fill="x", pady=(4, 0))

            accent = tk.Frame(row, bg="#004202", width=5)
            accent.pack(side="left", fill="y")
            self.nav_accents[key] = accent

            btn = tk.Button(
                row, text=label, font=("Segoe UI", 11, "bold"),
                bg="#004202", fg="white", activebackground="#0A5C13", activeforeground="#7ED985",
                bd=0, relief="flat", anchor="w", padx=18, pady=16, cursor="hand2",
                command=lambda k=key: show_page(k)
            )
            btn.pack(side="left", fill="x", expand=True)
            self.nav_buttons[key] = btn

            def on_enter(e, k=key):
                if self.nav_buttons_active != k:
                    self.nav_buttons[k].config(bg="#0A5C13")

            def on_leave(e, k=key):
                if self.nav_buttons_active != k:
                    self.nav_buttons[k].config(bg="#004202")

            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)

        self.create_students_tab(content_frame)
        self.create_add_student_tab(content_frame)
        self.create_tasks_assignments_tab(content_frame)

        show_page("students")

    def create_students_tab(self, parent):
        settings_frame = ttk.Frame(parent)
        settings_frame.grid(row=0, column=0, sticky="nsew")
        self.pages["students"] = settings_frame

        overview_frame = ttk.LabelFrame(settings_frame, text="Student Management")
        overview_frame.pack(fill="both", expand=True, padx=15, pady=15)

        overview_frame.columnconfigure(0, weight=0)
        overview_frame.columnconfigure(1, weight=1)
        overview_frame.rowconfigure(0, weight=1)

        # --- LEFT: Edit form ---
        form_frame = ttk.LabelFrame(overview_frame, text="Edit Student")
        form_frame.grid(row=0, column=0, sticky="ns", padx=(10, 5), pady=10)

        ttk.Label(form_frame, text="Student Name:").pack(anchor="w", padx=10, pady=(10, 2))
        self.edit_name_entry = ttk.Entry(form_frame, width=25)
        self.edit_name_entry.pack(padx=10, pady=(0, 8))

        ttk.Label(form_frame, text="Grade Level:").pack(anchor="w", padx=10, pady=(0, 2))
        self.edit_grade_entry = ttk.Entry(form_frame, width=25)
        self.edit_grade_entry.pack(padx=10, pady=(0, 8))

        ttk.Label(form_frame, text="Section:").pack(anchor="w", padx=10, pady=(0, 2))
        self.edit_section_entry = ttk.Entry(form_frame, width=25)
        self.edit_section_entry.pack(padx=10, pady=(0, 8))

        ttk.Label(form_frame, text="Addu Email:").pack(anchor="w", padx=10, pady=(0, 2))
        self.edit_email_entry = ttk.Entry(form_frame, width=25)
        self.edit_email_entry.pack(padx=10, pady=(0, 8))

        ttk.Label(form_frame, text="Committee:").pack(anchor="w", padx=10, pady=(0, 2))
        self.edit_committee_combo = ttk.Combobox(form_frame, width=22, state="readonly")
        self.edit_committee_combo['values'] = self.load_committees()
        self.edit_committee_combo.pack(padx=10, pady=(0, 8))

        ttk.Label(form_frame, text="Role:").pack(anchor="w", padx=10, pady=(0, 2))
        self.edit_role_combo = ttk.Combobox(form_frame, width=22, state="readonly",
                                             values=["Election Candidate", "Chairperson", "Secretary-General", "Finance Officer",
                                                     "G12 Commissioner", "G11 Commissioner", "Public Information Officer",
                                                     "Auditor", "Committee Head Commissioner", "Asst. Committee Head Commissioner", "Member"])
        self.edit_role_combo.pack(padx=10, pady=(0, 12))

        self.update_btn = ttk.Button(form_frame, text="Update Selected", style="Update.TButton",
                                      command=self.update_student, state="disabled")
        self.update_btn.pack(fill="x", padx=10, pady=(0, 6))

        self.delete_btn = ttk.Button(form_frame, text="Delete Selected", style="Delete.TButton",
                                      command=self.delete_student, state="disabled")
        self.delete_btn.pack(fill="x", padx=10, pady=(0, 10))

        # --- RIGHT: View switcher + single table ---
        right_col = ttk.Frame(overview_frame)
        right_col.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)

        view_row = ttk.Frame(right_col)
        view_row.pack(fill="x", pady=(0, 8))
        ttk.Label(view_row, text="Show:", font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 8))
        self.view_combo = ttk.Combobox(view_row, width=20, state="readonly",
                                        values=["All Students", "ASHSCOM Members"])
        self.view_combo.set("All Students")
        self.view_combo.pack(side="left")
        self.view_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_table_view())

        self.student_tree = self._build_tree(right_col)
        self.student_tree.bind("<<TreeviewSelect>>", lambda e: self.on_student_select(self.student_tree))

        self.load_students()

    def _build_tree(self, parent):
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill="both", expand=True, padx=8, pady=8)

        tree_scroll_y = ttk.Scrollbar(tree_frame)
        tree_scroll_y.pack(side="right", fill="y")

        tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll_y.set, selectmode="browse")
        tree.pack(fill="both", expand=True)
        tree_scroll_y.config(command=tree.yview)

        tree['columns'] = ("id", "name", "grade_level", "section", "addu_email", "committee", "role")
        tree.column("#0", width=0, stretch=tk.NO)
        tree.column("id", width=35, anchor=tk.CENTER)
        tree.column("name", width=110, anchor=tk.W)
        tree.column("grade_level", width=60, anchor=tk.CENTER)
        tree.column("section", width=60, anchor=tk.CENTER)
        tree.column("addu_email", width=130, anchor=tk.W)
        tree.column("committee", width=90, anchor=tk.CENTER)
        tree.column("role", width=120, anchor=tk.CENTER)

        tree.heading("id", text="ID", anchor=tk.CENTER)
        tree.heading("name", text="Name", anchor=tk.CENTER)
        tree.heading("grade_level", text="Grade", anchor=tk.CENTER)
        tree.heading("section", text="Section", anchor=tk.CENTER)
        tree.heading("addu_email", text="Email", anchor=tk.CENTER)
        tree.heading("committee", text="Committee", anchor=tk.CENTER)
        tree.heading("role", text="Role", anchor=tk.CENTER)

        tree.tag_configure("evenrow", background="#F3FFF4")
        tree.tag_configure("oddrow", background="#FFFFFF")
        return tree


    def create_add_student_tab(self, parent):
        students_frame = ttk.Frame(parent)
        students_frame.grid(row=0, column=0, sticky="nsew")
        self.pages["add_student"] = students_frame

        add_student_frame = ttk.LabelFrame(students_frame, text="Add Student")
        add_student_frame.pack(fill="both", expand=True, padx=15, pady=15)

        entry_frame = ttk.Frame(add_student_frame)
        entry_frame.pack(fill="x", padx=10, pady=(10, 5))

        ttk.Label(entry_frame, text="Student Name:").grid(row=0, column=0, padx=8, pady=6, sticky="w")
        self.name_entry = ttk.Entry(entry_frame, width=40)
        self.name_entry.grid(row=0, column=1, padx=20, pady=6)

        ttk.Label(entry_frame, text="Grade Level:").grid(row=1, column=0, padx=8, pady=6, sticky="w")
        self.grade_entry = ttk.Entry(entry_frame, width=40)
        self.grade_entry.grid(row=1, column=1, padx=20, pady=6)

        ttk.Label(entry_frame, text="Section:").grid(row=2, column=0, padx=8, pady=6, sticky="w")
        self.section_entry = ttk.Entry(entry_frame, width=40)
        self.section_entry.grid(row=2, column=1, padx=20, pady=6)

        ttk.Label(entry_frame, text="Addu Email:").grid(row=3, column=0, padx=8, pady=6, sticky="w")
        self.email_entry = ttk.Entry(entry_frame, width=40)
        self.email_entry.grid(row=3, column=1, padx=20, pady=6)

        ttk.Label(entry_frame, text="Committee:").grid(row=4, column=0, padx=8, pady=6, sticky="w")
        self.committee_combo = ttk.Combobox(entry_frame, width=37, state="readonly")
        self.committee_combo['values'] = self.load_committees()
        self.committee_combo.grid(row=4, column=1, padx=20, pady=6)

        ttk.Label(entry_frame, text="Role:").grid(row=5, column=0, padx=8, pady=6, sticky="w")
        self.role_combo = ttk.Combobox(entry_frame, width=37, state="readonly",
                                        values=["Election Candidate", "Chairperson", "Secretary-General", "Finance Officer",
                                                "G12 Commissioner", "G11 Commissioner", "Public Information Officer",
                                                "Auditor", "Committee Head Commissioner", "Asst. Committee Head Commissioner", "Member"])
        self.role_combo.grid(row=5, column=1, padx=20, pady=6)

        button_frame = ttk.Frame(add_student_frame)
        button_frame.pack(fill="x", padx=10, pady=(5, 10))

        ttk.Button(button_frame, text="+ Add Student", style="Add.TButton",
                   command=self.add_student).pack(side="left", padx=8, ipadx=0)

    def create_tasks_assignments_tab(self, parent):
        settings_frame = ttk.Frame(parent)
        settings_frame.grid(row=0, column=0, sticky="nsew")
        self.pages["task/assignment"] = settings_frame

        settings_label = ttk.Label(settings_frame, text="Assign Members to Task", font=("Arial", 16))
        settings_label.pack(pady=20)

    def load_students(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT s.StudentID, s.StudentName, s.GradeLevel, s.Section, s.AdduEmail,
                       c.CommitteeName, m.OfficerRole, m.CommitteeID
                FROM Student s
                LEFT JOIN Member m ON s.StudentID = m.StudentID
                LEFT JOIN Committee c ON m.CommitteeID = c.CommitteeID
            """)
            rows = cursor.fetchall()
            cursor.close()

            self._all_students_rows = [row[:7] for row in rows]
            self._members_rows = [row[:7] for row in rows if row[7] is not None]

            self.refresh_table_view()
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to load students: {e}")

    def refresh_table_view(self):
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)

        data = self._members_rows if self.view_combo.get() == "ASHSCOM Members" else self._all_students_rows

        for i, row in enumerate(data):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.student_tree.insert("", tk.END, values=row, tags=(tag,))

    def load_committees(self):
        self.committees_list = []
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT CommitteeID, CommitteeName FROM Committee")
            self.committees_list = cursor.fetchall()
            cursor.close()
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to load committees: {e}")
        return [name for (_id, name) in self.committees_list]

# Student management methods
    def add_student(self):
        name = self.name_entry.get().strip()
        grade = self.grade_entry.get().strip()
        section = self.section_entry.get().strip()
        email = self.email_entry.get().strip()
        committee_name = self.committee_combo.get()
        role = self.role_combo.get()

        if not name:
            messagebox.showwarning("Input Error", "Student name is required.")
            return
        if not grade:
            messagebox.showwarning("Input Error", "Grade level is required.")
            return
        if not section:
            messagebox.showwarning("Input Error", "Section is required.")
            return
        if not email:
            messagebox.showwarning("Input Error", "Email is required.")
            return
        if not committee_name and not role:
            messagebox.showwarning("Input Error", "Please select a role for the Student. If the Student is an Election Candidate, please select the Committee and Role accordingly.")
            return

        try:
            cursor = self.connection.cursor()
            cursor.execute("INSERT INTO Student (StudentName, GradeLevel, Section, AdduEmail) VALUES (%s, %s, %s, %s)",
                           (name, grade, section, email))
            new_student_id = cursor.lastrowid

            if committee_name:
                committee_id = next((cid for cid, cname in self.committees_list if cname == committee_name), None)
                cursor.execute(
                    "INSERT INTO Member (StudentID, CommitteeID, OfficerRole) VALUES (%s, %s, %s)",
                    (new_student_id, committee_id, role if role else "Member")
                )

            self.connection.commit()
            cursor.close()
            messagebox.showinfo("Success", "Student added successfully.")
            self.clear_add_form()
            self.load_students()
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to add student: {e}")

    def clear_add_form(self):
        self.name_entry.delete(0, tk.END)
        self.grade_entry.delete(0, tk.END)
        self.section_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.committee_combo.set("")
        self.role_combo.set("")

    def clear_edit_form(self):
        self.edit_name_entry.delete(0, tk.END)
        self.edit_grade_entry.delete(0, tk.END)
        self.edit_section_entry.delete(0, tk.END)
        self.edit_email_entry.delete(0, tk.END)
        self.edit_committee_combo.set("")
        self.edit_role_combo.set("")

    def on_student_select(self, tree):
        selected = tree.focus()
        if selected:
            values = tree.item(selected, 'values')
            if values:
                self.edit_name_entry.delete(0, tk.END)
                self.edit_name_entry.insert(0, values[1])
                self.edit_grade_entry.delete(0, tk.END)
                self.edit_grade_entry.insert(0, values[2])
                self.edit_section_entry.delete(0, tk.END)
                self.edit_section_entry.insert(0, values[3])
                self.edit_email_entry.delete(0, tk.END)
                self.edit_email_entry.insert(0, values[4])
                self.edit_committee_combo.set(values[5] if values[5] else "")
                self.edit_role_combo.set(values[6] if values[6] else "")
                self._selected_student_id = values[0]
                self.update_btn.config(state="normal")
                self.delete_btn.config(state="normal")
        else:
            self.clear_edit_form()
            self.update_btn.config(state="disabled")
            self.delete_btn.config(state="disabled")

    def update_student(self):
        if not hasattr(self, '_selected_student_id') or not self._selected_student_id:
            messagebox.showwarning("Selection Error", "Please select a Student to update.")
            return
        student_id = self._selected_student_id
        name = self.edit_name_entry.get().strip()
        grade = self.edit_grade_entry.get().strip()
        section = self.edit_section_entry.get().strip()
        email = self.edit_email_entry.get().strip()
        committee_name = self.edit_committee_combo.get()
        role = self.edit_role_combo.get()

        if not name:
            messagebox.showwarning("Input Error", "Student name is required.")
            return
        if not grade:
            messagebox.showwarning("Input Error", "Grade level is required.")
            return
        if not section:
            messagebox.showwarning("Input Error", "Section is required.")
            return
        if not email:
            messagebox.showwarning("Input Error", "Email is required.")
            return

        try:
            cursor = self.connection.cursor()
            cursor.execute("UPDATE Student SET StudentName=%s, GradeLevel=%s, Section=%s, AdduEmail=%s WHERE StudentID=%s",
                           (name, grade, section, email, student_id))

            if committee_name:
                committee_id = next((cid for cid, cname in self.committees_list if cname == committee_name), None)
                cursor.execute("""
                    INSERT INTO Member (StudentID, CommitteeID, OfficerRole) VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE CommitteeID=%s, OfficerRole=%s
                """, (student_id, committee_id, role if role else "Member", committee_id, role if role else "Member"))

            self.connection.commit()
            cursor.close()
            messagebox.showinfo("Success", "Student updated successfully.")
            self.clear_edit_form()
            self.load_students()
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to update student: {e}")

    def delete_student(self):
        if not hasattr(self, '_selected_student_id') or not self._selected_student_id:
            messagebox.showwarning("Selection Error", "Please select a Student to delete.")
            return
        student_id = self._selected_student_id
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete this Student #{student_id}?"):
            try:
                cursor = self.connection.cursor()
                cursor.execute("DELETE FROM Student WHERE StudentID=%s", (student_id,))
                self.connection.commit()
                cursor.close()
                messagebox.showinfo("Success", f"Student {student_id} deleted successfully.")
                self.clear_edit_form()
                self.load_students()
            except Error as e:
                messagebox.showerror("Database Error", f"Failed to delete student: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = AshscomGUI(root)
    root.mainloop()


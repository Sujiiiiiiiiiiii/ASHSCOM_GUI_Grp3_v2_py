import tkinter as tk
from tkinter import ttk, messagebox
from types import SimpleNamespace
from PIL import Image, ImageTk
from db_connect import create_connection
from mysql.connector import Error


# ---------------------------------------------------------------------------
# Grade Level -> Sections map (alphabetical)
# ---------------------------------------------------------------------------
GRADE_SECTIONS = {
    "Grade 11": [
        "GARNET",
        "GARNIER",
        "GAVAN",
        "GONZALES",
        "HERNANDEZ",
        "HOLLAND",
        "HURTADO",
        "ISORE",
        "KASUI",
        "KIMURA",
        "KISAI",
        "KOSTKA",
        "LALEMANT",
        "LEWIS",
        "MANGIN",
        "MAUNOIR",
        "MAYER",
        "MIKI",
        "MORSE",
        "NAKAURA",
        "NAVARRO",
        "OGILVIE",
        "OLDCORNE",
        "OTA",
        "OWEN",
        "PACHECO",
        "PAGE",
        "PANTALIA",
        "PEREZ",
        "PIGNATELLI",
        "PONGRACZ",
        "PRO",
        "REALINO",
        "REGIS",
        "RODRIGUEZ",
        "RUBIO",
        "RUIZ",
        "RYOSETSU",
        "SALES",
        "SOUTHWELL",
    ],
    "Grade 12": [
        "ACQUAVIVA",
        "ANCHIETA",
        "ANDLAUER",
        "ANGELIS",
        "ARANHA",
        "ARROWSMITH",
        "AZEVEDO",
        "BALDINUCCI",
        "BELLARMINE",
        "BERCHMANS",
        "BERTHIEU",
        "BEYZYM",
        "BOBOLA",
        "BORGIA",
        "BREBEUF",
        "BRIANT",
        "BRITO",
        "CALUNGSOD",
        "CAMPION",
        "CANISIUS",
        "CHABANEL",
        "COLLINS",
        "COLOMBIERE",
        "CORBY",
        "COTTAM",
        "DAJANI",
        "DANIEL",
        "DE HOYOS",
        "DEL CASTILLO",
        "DENN",
        "ESCRIBANO",
        "EVANS",
        "FAUSTI",
        "FAVRE",
        "FERNANDO",
        "FERRERES",
        "FONTOURA",
        "GARATE",
        "GERONIMO",
        "LOYOLA",
    ],
}
GRADE_LEVELS = list(GRADE_SECTIONS.keys())


class ModernDropdown(tk.Frame):
    BORDER = "#003366"          # AdDU Navy Blue
    BORDER_ACTIVE = "#198754"   # Professional Green for focus
    TEXT = "#1A1A1A"            
    PLACEHOLDER = "#6C757D"     
    HOVER = "#E8F5E9"           # Very soft light green
    SELECTED = "#C8E6C9"        # Solid light green
    ROW_HEIGHT = 28
    MAX_VISIBLE_ROWS = 8

    _active = None  

    def __init__(self, master=None, width=20, state="readonly", values=None, **kwargs):
        super().__init__(master, bg=self.BORDER, highlightthickness=0, bd=0)
        self._values = list(values) if values else []
        self._value = ""
        self._callbacks = []
        self._popup = None
        self._click_id = None

        inner = tk.Frame(self, bg="white")
        inner.pack(fill="both", expand=True, padx=1, pady=1)

        self._label = tk.Label(
            inner,
            text="",
            anchor="w",
            bg="white",
            fg=self.PLACEHOLDER,
            font=("Segoe UI", 10),
            padx=10,
            pady=7,
            width=width,
            cursor="hand2",
        )
        self._label.pack(side="left", fill="both", expand=True)

        self._arrow = tk.Label(
            inner,
            text="\u25be",
            bg="white",
            fg="#6B6B6B",
            font=("Segoe UI", 10),
            padx=8,
            cursor="hand2",
        )
        self._arrow.pack(side="right")

        for w in (self, inner, self._label, self._arrow):
            w.bind("<Button-1>", self._toggle)
        for w in (self, inner, self._label, self._arrow):
            w.bind("<Enter>", lambda e: self.config(bg=self.BORDER_ACTIVE))
            w.bind("<Leave>", self._on_leave)

        self._inner = inner
        self._render()

    # -- public API (mirrors the bits of ttk.Combobox this app relies on) --
    def get(self):
        return self._value

    def set(self, value):
        self._select(value if value else "", notify=False)

    def current(self, index=None):
        if index is None:
            return (
                self._values.index(self._value) if self._value in self._values else -1
            )
        if 0 <= index < len(self._values):
            self._select(self._values[index], notify=False)

    def __setitem__(self, key, value):
        if key == "values":
            self._values = list(value) if value else []
            if self._value not in self._values:
                self._select("", notify=False)

    def __getitem__(self, key):
        if key == "values":
            return list(self._values)
        return None

    def bind(self, sequence=None, func=None, add=None):
        if sequence == "<<ComboboxSelected>>":
            self._callbacks.append(func)
            return
        return super().bind(sequence, func, add)

    # -- internals --
    def _on_leave(self, event=None):
        if not (self._popup is not None and self._popup.winfo_exists()):
            self.config(bg=self.BORDER)

    def _render(self):
        if self._value:
            self._label.config(text=self._value, fg=self.TEXT)
        else:
            self._label.config(text="", fg=self.PLACEHOLDER)

    def _select(self, value, notify=True):
        self._value = value
        self._render()
        self._close_popup()
        if notify:
            evt = SimpleNamespace(widget=self)
            for cb in list(self._callbacks):
                if cb:
                    cb(evt)

    def _toggle(self, event=None):
        if self._popup is not None:
            self._close_popup()
        else:
            self._open_popup()

    def _open_popup(self):
        if not self._values:
            return
        if ModernDropdown._active is not None and ModernDropdown._active is not self:
            ModernDropdown._active._close_popup()
        ModernDropdown._active = self
        self.config(bg=self.BORDER_ACTIVE)

        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height()
        width = max(self.winfo_width(), 140)
        visible_rows = min(len(self._values), self.MAX_VISIBLE_ROWS)
        height = visible_rows * self.ROW_HEIGHT + 2

        popup = tk.Toplevel(self)
        popup.wm_overrideredirect(True)
        popup.wm_geometry(f"{width}x{height}+{x}+{y}")
        popup.config(bg=self.BORDER_ACTIVE)
        self._popup = popup

        frame = tk.Frame(popup, bg="white")
        frame.pack(fill="both", expand=True, padx=1, pady=1)

        needs_scroll = len(self._values) > self.MAX_VISIBLE_ROWS
        canvas = tk.Canvas(frame, bg="white", highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)
        list_frame = tk.Frame(canvas, bg="white")
        canvas.create_window((0, 0), window=list_frame, anchor="nw", width=width - 2)

        if needs_scroll:
            scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
            scrollbar.pack(side="right", fill="y")
            canvas.configure(yscrollcommand=scrollbar.set)

        def on_wheel(event):
            delta = 1 if getattr(event, "num", None) == 5 or event.delta < 0 else -1
            canvas.yview_scroll(delta, "units")

        for val in self._values:
            row = tk.Label(
                list_frame,
                text=val,
                anchor="w",
                bg="white",
                fg=self.TEXT,
                font=("Segoe UI", 10),
                padx=10,
                pady=6,
                cursor="hand2",
            )
            row.pack(fill="x")
            if val == self._value:
                row.config(bg=self.SELECTED)
            row.bind(
                "<Enter>",
                lambda e, r=row, v=val: r.config(
                    bg=self.HOVER if v != self._value else self.SELECTED
                ),
            )
            row.bind(
                "<Leave>",
                lambda e, r=row, v=val: r.config(
                    bg=self.SELECTED if v == self._value else "white"
                ),
            )
            row.bind("<Button-1>", lambda e, v=val: self._select(v))
            for w in (canvas, list_frame, row):
                w.bind("<MouseWheel>", on_wheel)
                w.bind("<Button-4>", on_wheel)
                w.bind("<Button-5>", on_wheel)

        list_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

        self._click_id = self.winfo_toplevel().bind_all(
            "<Button-1>", self._on_global_click, add="+"
        )

    def _on_global_click(self, event):
        if self._popup is None:
            return

        def is_descendant(widget, ancestor):
            while widget is not None:
                if widget == ancestor:
                    return True
                widget = getattr(widget, "master", None)
            return False

        widget_under = getattr(event, "widget", None)
        if is_descendant(widget_under, self._popup) or is_descendant(
            widget_under, self
        ):
            return
        self._close_popup()

    def _close_popup(self):
        if self._popup is not None:
            self._popup.destroy()
            self._popup = None
        if ModernDropdown._active is self:
            ModernDropdown._active = None
        if self._click_id is not None:
            try:
                self.winfo_toplevel().unbind_all("<Button-1>")
            except Exception:
                pass
            self._click_id = None
        self.config(bg=self.BORDER)


class AshscomGUI:
    STUDENT_PASSKEY = "ashscom2026"

    def __init__(self, root):
        self.root = root
        self.root.title("Ashscom Management System")
        self.root.geometry("1200x700")
        self.root.configure(bg="#ADFFB1")
        self.setup_styles()
        self.root.configure(bg="#F7FFF9")

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        BG_COLOR = "#F4F6F9"
        ADDU_BLUE = "#003366"
        ADDU_GOLD = "#D4AF37"
        ACTION_GREEN = "#198754" 
        
        style.configure("TFrame", background=BG_COLOR)
        style.configure("TLabelframe", background=BG_COLOR, bordercolor=ADDU_BLUE)
        style.configure("TLabel", background=BG_COLOR, font=("Segoe UI", 10))
        
        style.configure(
            "TLabelframe.Label",
            font=("Segoe UI", 11, "bold"),
            foreground=ADDU_BLUE,
            background=BG_COLOR,
        )
        
        # Entry Fields - Blue resting, Green focus
        style.configure("TEntry", padding=6, relief="flat", bordercolor="#B0C4DE")
        style.map(
            "TEntry",
            bordercolor=[("focus", ACTION_GREEN)],
            lightcolor=[("focus", ACTION_GREEN)],
            darkcolor=[("focus", ACTION_GREEN)],
        )
        
        # Action Buttons
        style.configure(
            "Add.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=8,
            background=ACTION_GREEN,
            foreground="white",
        )
        style.map("Add.TButton", background=[("active", "#157347")])
        
        style.configure(
            "Update.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=8,
            background="#157347",
            foreground="#FFFFFF", 
        )
        style.map(
            "Update.TButton", 
            background=[("active", "#157347"), ("disabled", "#7ED985")],
            foreground=[("disabled", "#FFFFFF")],
        )
        style.configure(
            "Delete.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=8,
            background="#D9534F", 
            foreground="white",
        )
        style.map(
            "Delete.TButton",
            background=[("active", "#C9302C"), ("disabled", "#F2A6A6")],
            foreground=[("disabled", "#F4F6F9")],
        )
        
        # Treeview
        style.configure(
            "Treeview",
            font=("Segoe UI", 10),
            rowheight=32, 
            background="white",
            fieldbackground="white",
            foreground="#1A1A1A",
        )
        style.map(
            "Treeview",
            background=[("selected", "#E8F5E9")], # Light green selection
            foreground=[("selected", ACTION_GREEN)],
        )
        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 10, "bold"),
            background=ADDU_BLUE,
            foreground="white",
        )
        style.map("Treeview.Heading", background=[("active", "#00205B")])
        self.root.option_add("*TEntry*selectBackground", "#D4FFD9")
        self.root.option_add("*TEntry*selectForeground", "#004202")
        self.root.option_add("*Entry.selectBackground", "#D4FFD9")
        self.root.option_add("*Entry.selectForeground", "#004202")

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
            r1, g1, b1 = self.root.winfo_rgb("#00153B") 
            r2, g2, b2 = self.root.winfo_rgb("#003366")
            
            for i in range(height):
                nr = int(r1 + (r2 - r1) * i / height) >> 8
                ng = int(g1 + (g2 - g1) * i / height) >> 8
                nb = int(b1 + (b2 - b1) * i / height) >> 8
                color = f"#{nr:02x}{ng:02x}{nb:02x}"
                header_canvas.create_line(0, i, width, i, fill=color)

            # Logos
            header_canvas.create_image(35, 50, image=self.logo1, anchor="w")
            header_canvas.create_image(115, 50, image=self.logo2, anchor="w")

            # Text - right-aligned using the CURRENT width, every time
            right_x = width - 15
            header_canvas.create_text(
                right_x,
                28,
                text="Ateneo De Davao University Senior High School",
                font=("Segoe UI", 12, "bold"),
                fill="#F4F6F9",
                anchor="e",
            )
            header_canvas.create_text(
                right_x,
                48,
                text="Commission on Elections",
                font=("Segoe UI", 12, "bold"),
                fill="#F4F6F9",
                anchor="e",
            )
            header_canvas.create_text(
                right_x,
                75,
                text="ASHSCOM MANAGEMENT SYSTEM",
                font=("Segoe UI", 23, "bold"),
                fill="#D4AF37",
                anchor="e",
            )

        header_canvas.bind("<Configure>", redraw_header)

        divider = tk.Frame(self.root, bg="#198754", height=3)
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

        sidebar = tk.Frame(body_frame, bg="#00205B", width=230)
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
                b.config(bg="#00205B", fg="white")
                self.nav_accents[key].config(bg="#00205B")
            self.nav_buttons[name].config(bg="#003366", fg="#28A745")
            self.nav_accents[name].config(bg="#28A745")

        nav_buttons = [
            ("👥  Students", "students"),
            ("➕  Add Student/Tasks", "add_student"),
            ("📋  Tasks/Assignments", "task/assignment"),
        ]
        for label, key in nav_buttons:
            row = tk.Frame(sidebar, bg="#00205B")
            row.pack(fill="x", pady=(4, 0))

            accent = tk.Frame(row, bg="#00205B", width=5)
            accent.pack(side="left", fill="y")
            self.nav_accents[key] = accent

            btn = tk.Button(
                row,
                text=label,
                font=("Segoe UI", 11, "bold"),
                bg="#00205B",
                fg="white",
                activebackground="#003366",
                activeforeground="#28A745",
                bd=0,
                relief="flat",
                anchor="w",
                padx=18,
                pady=16,
                cursor="hand2",
                command=lambda k=key: show_page(k),
            )
            btn.pack(side="left", fill="x", expand=True)
            self.nav_buttons[key] = btn

            def on_enter(e, k=key):
                if self.nav_buttons_active != k:
                    self.nav_buttons[k].config(bg="#003366")

            def on_leave(e, k=key):
                if self.nav_buttons_active != k:
                    self.nav_buttons[k].config(bg="#00205B")

            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)

        self.create_students_tab(content_frame)
        self.create_add_student_tab(content_frame)
        self.create_tasks_assignments_tab(content_frame)

        show_page("students")

    # -----------------------------------------------------------------
    # Cascading Grade -> Section helper (alphabetical + no highlight)
    # -----------------------------------------------------------------
    def _on_grade_selected(self, grade_combo, section_combo, event=None):
        grade = grade_combo.get()
        sections = GRADE_SECTIONS.get(grade, [])
        section_combo["values"] = sections
        section_combo.set("")
        try:
            self.root.focus_set()
        except Exception:
            pass

    def _clear_combo_highlight(self, event=None):
        try:
            self.root.focus_set()
        except Exception:
            pass

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
        form_frame = ttk.LabelFrame(overview_frame, text="Update Student")
        form_frame.grid(row=0, column=0, sticky="new", padx=(10, 5), pady=(10, 11))

        # inline grid layout — labels left, fields right (matches Add Student tab)
        # Fixed label-column width + identical field width/padding/pady on every
        # row so entries and comboboxes line up exactly under one another.
        form_frame.columnconfigure(0, weight=0, minsize=110)
        form_frame.columnconfigure(1, weight=1)
        FIELD_WIDTH = 22
        ROW_PADY = 6

        ttk.Label(form_frame, text="Student Name:").grid(
            row=0, column=0, padx=10, pady=ROW_PADY, sticky="w"
        )
        self.edit_name_entry = ttk.Entry(form_frame, width=FIELD_WIDTH)
        self.edit_name_entry.grid(row=0, column=1, padx=10, pady=ROW_PADY, sticky="ew")

        ttk.Label(form_frame, text="Grade Level:").grid(
            row=1, column=0, padx=10, pady=ROW_PADY, sticky="w"
        )
        self.edit_grade_entry = ModernDropdown(
            form_frame, width=FIELD_WIDTH, state="readonly", values=GRADE_LEVELS
        )
        self.edit_grade_entry.grid(row=1, column=1, padx=10, pady=ROW_PADY, sticky="ew")
        self.edit_grade_combo = self.edit_grade_entry

        ttk.Label(form_frame, text="Section:").grid(
            row=2, column=0, padx=10, pady=ROW_PADY, sticky="w"
        )
        self.edit_section_entry = ModernDropdown(
            form_frame, width=FIELD_WIDTH, state="readonly"
        )
        self.edit_section_entry.grid(
            row=2, column=1, padx=10, pady=ROW_PADY, sticky="ew"
        )
        self.edit_section_combo = self.edit_section_entry

        self.edit_grade_entry.bind(
            "<<ComboboxSelected>>",
            lambda e: self._on_grade_selected(
                self.edit_grade_entry, self.edit_section_entry, e
            ),
        )
        self.edit_section_entry.bind(
            "<<ComboboxSelected>>", self._clear_combo_highlight
        )

        ttk.Label(form_frame, text="Addu Email:").grid(
            row=3, column=0, padx=10, pady=ROW_PADY, sticky="w"
        )
        self.edit_email_entry = ttk.Entry(form_frame, width=FIELD_WIDTH)
        self.edit_email_entry.grid(row=3, column=1, padx=10, pady=ROW_PADY, sticky="ew")

        ttk.Label(form_frame, text="Committee:").grid(
            row=4, column=0, padx=10, pady=ROW_PADY, sticky="w"
        )
        self.edit_committee_combo = ModernDropdown(
            form_frame, width=FIELD_WIDTH, state="readonly"
        )
        self.edit_committee_combo["values"] = self.load_committees()
        self.edit_committee_combo.grid(
            row=4, column=1, padx=10, pady=ROW_PADY, sticky="ew"
        )

        ttk.Label(form_frame, text="Role:").grid(
            row=5, column=0, padx=10, pady=ROW_PADY, sticky="w"
        )
        self.edit_role_combo = ModernDropdown(
            form_frame,
            width=FIELD_WIDTH,
            state="readonly",
            values=[
                "Election Candidate",
                "Chairperson",
                "Secretary-General",
                "Finance Officer",
                "G12 Commissioner",
                "G11 Commissioner",
                "Public Information Officer",
                "Auditor",
                "Committee Head Commissioner",
                "Asst. Committee Head Commissioner",
                "Member",
            ],
        )
        self.edit_role_combo.grid(row=5, column=1, padx=10, pady=ROW_PADY, sticky="ew")
        self.edit_committee_combo.bind(
            "<<ComboboxSelected>>", self._clear_combo_highlight
        )
        self.edit_role_combo.bind("<<ComboboxSelected>>", self._clear_combo_highlight)

        self.update_btn = ttk.Button(
            form_frame,
            text="🔼 Update Selected",
            style="Update.TButton",
            command=self.update_student,
            state="disabled",
        )
        self.update_btn.grid( 
            row=6, column=0, columnspan=2, padx=10, pady=(10, 4), sticky="ew"
        )

        self.delete_btn = ttk.Button(
            form_frame,
            text="🗑 Delete Selected",
            style="Delete.TButton",
            command=self.delete_student,
            state="disabled",
        )
        self.delete_btn.grid(
            row=7, column=0, columnspan=2, padx=10, pady=(0, 4), sticky="ew"
        )

        # --- RIGHT: View switcher + single table ---
        right_col = ttk.Frame(overview_frame)
        right_col.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=0)
        right_col.rowconfigure(0, weight=1)
        right_col.columnconfigure(0, weight=1)

        # Lock screen - shown by default
        self.lock_frame = ttk.Frame(right_col)
        self.lock_frame.grid(row=0, column=0, sticky="nsew")

        lock_inner = ttk.Frame(self.lock_frame)
        lock_inner.place(relx=0.5, rely=0.4, anchor="center")
        ttk.Label(lock_inner, text="🔒", font=("Segoe UI", 40)).pack(pady=(0, 10))
        ttk.Label(lock_inner, text="Student records are protected.",
                  font=("Segoe UI", 11, "bold")).pack(pady=(0, 15))
        ttk.Button(lock_inner, text="🔍 View Students", style="Add.TButton",
                   command=self._prompt_unlock).pack()

        # Data screen - hidden until unlocked
        self.data_frame = ttk.Frame(right_col)
        self.data_frame.grid(row=0, column=0, sticky="nsew")

        view_row = ttk.Frame(self.data_frame)
        view_row.pack(fill="x", padx=8, pady=(10, 8))

        ttk.Label(view_row, text="Show:", font=("Segoe UI", 10, "bold")).pack(
            side="left", padx=(0, 5)
        )
        self.view_combo = ModernDropdown(
            view_row,
            width=20,
            state="readonly",
            values=[
                "All Students",
                "ASHSCOM Members",
                "Election Candidates",
                "Committee Heads",
            ],
        )
        self.view_combo.set("All Students")
        self.view_combo.pack(side="left", padx=(0, 12))
        self.view_combo.bind(
            "<<ComboboxSelected>>",
            lambda e: (self.refresh_table_view(), self._clear_combo_highlight(e)),
        )

        search_wrap = tk.Frame(view_row, bg="#7ED985", bd=0)
        search_wrap.pack(side="left", fill="x", expand=True)

        search_inner = tk.Frame(search_wrap, bg="white")
        search_inner.pack(fill="both", expand=True, padx=1, pady=1)

        tk.Label(search_inner, text="🔍", bg="white", fg="#6B6B6B",
                 font=("Segoe UI", 10)).pack(side="left", padx=(10, 4), pady=6)

        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_inner, textvariable=self.search_var,
                                 bg="white", fg="#0F1A0F", relief="flat",
                                 font=("Segoe UI", 10), bd=0)
        search_entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 10))
        self.search_var.trace_add("write", lambda *args: self.refresh_table_view())

        self.student_tree = self._build_student_tree(self.data_frame)
        self.student_tree.bind(
            "<<TreeviewSelect>>", lambda e: self.on_student_select(self.student_tree)
        )

        self.lock_frame.tkraise()

    def _build_student_tree(self, parent):
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill="both", expand=True, padx=8, pady=(0, 13))

        tree_scroll_y = ttk.Scrollbar(tree_frame)
        tree_scroll_y.pack(side="right", fill="y")
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal")
        tree_scroll_x.pack(side="bottom", fill="x")

        tree = ttk.Treeview(
            tree_frame,
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set,
            selectmode="browse",
        )
        tree.pack(fill="both", expand=True)
        tree_scroll_y.config(command=tree.yview)
        tree_scroll_x.config(command=tree.xview)

        tree["columns"] = (
            "id",
            "name",
            "grade_level",
            "section",
            "addu_email",
            "committee",
            "role",
        )
        tree.column("#0", width=0, stretch=tk.NO)
        tree.column("id", width=50, anchor=tk.CENTER, stretch=False)
        tree.column("name", width=200, anchor=tk.W, stretch=False)
        tree.column("grade_level", width=80, anchor=tk.CENTER, stretch=False)
        tree.column("section", width=100, anchor=tk.CENTER, stretch=False)
        tree.column("addu_email", width=220, anchor=tk.W, stretch=False)
        tree.column("committee", width=140, anchor=tk.CENTER, stretch=False)
        tree.column("role", width=180, anchor=tk.CENTER, stretch=False)

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

    def _build_task_tree(self, parent):
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill="both", expand=True, padx=0, pady=0)

        tree_scroll_y = ttk.Scrollbar(tree_frame)
        tree_scroll_y.pack(side="right", fill="y")
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal")
        tree_scroll_x.pack(side="bottom", fill="x")

        tree = ttk.Treeview(
            tree_frame,
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set,
            selectmode="browse",
        )
        tree.pack(fill="both", expand=True)
        tree_scroll_y.config(command=tree.yview)
        tree_scroll_x.config(command=tree.xview)

        tree["columns"] = ("id", "task_name", "assigned_to", "status")
        tree.column("#0", width=0, stretch=tk.NO)
        tree.column("id", width=50, anchor=tk.CENTER, stretch=True)
        tree.column("task_name", width=300, anchor=tk.W, stretch=True)
        tree.column("assigned_to", width=200, anchor=tk.W, stretch=True)
        tree.column("status", width=100, anchor=tk.CENTER, stretch=True)

        tree.heading("id", text="ID", anchor=tk.CENTER)
        tree.heading("task_name", text="Task Name", anchor=tk.CENTER)
        tree.heading("assigned_to", text="Assigned To", anchor=tk.CENTER)
        tree.heading("status", text="Status", anchor=tk.CENTER)

        tree.tag_configure("evenrow", background="#F3FFF4")
        tree.tag_configure("oddrow", background="#FFFFFF")
        return tree

    def create_add_student_tab(self, parent):
        students_frame = ttk.Frame(parent)
        students_frame.grid(row=0, column=0, sticky="nsew")
        self.pages["add_student"] = students_frame

        container = ttk.Frame(students_frame)
        container.pack(fill="both", expand=True, padx=15, pady=15)
        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(0, weight=1)

        # --- Add Student section (left) ---
        add_student_frame = ttk.LabelFrame(container, text="Add Student")
        add_student_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=5)

        entry_frame = ttk.Frame(add_student_frame)
        entry_frame.pack(fill="x", padx=10, pady=(10, 5))
        # Grid-aligned: same 2-col grid as Update Student — fixes uneven padx/sticky
        entry_frame.columnconfigure(0, weight=0, minsize=110)
        entry_frame.columnconfigure(1, weight=1)
        _FW = 22
        _PY = 6

        ttk.Label(entry_frame, text="Student Name:").grid(
            row=0, column=0, padx=10, pady=_PY, sticky="w"
        )
        self.name_entry = ttk.Entry(entry_frame, width=_FW)
        self.name_entry.grid(row=0, column=1, padx=10, pady=_PY, sticky="ew")

        ttk.Label(entry_frame, text="Grade Level:").grid(
            row=1, column=0, padx=10, pady=_PY, sticky="w"
        )
        self.grade_entry = ModernDropdown(
            entry_frame, width=_FW, state="readonly", values=GRADE_LEVELS
        )
        self.grade_entry.grid(row=1, column=1, padx=10, pady=_PY, sticky="ew")
        self.grade_combo = self.grade_entry

        ttk.Label(entry_frame, text="Section:").grid(
            row=2, column=0, padx=10, pady=_PY, sticky="w"
        )
        self.section_entry = ModernDropdown(entry_frame, width=_FW, state="readonly")
        self.section_entry.grid(row=2, column=1, padx=10, pady=_PY, sticky="ew")
        self.section_combo = self.section_entry

        self.grade_entry.bind(
            "<<ComboboxSelected>>",
            lambda e: self._on_grade_selected(self.grade_entry, self.section_entry, e),
        )
        self.section_entry.bind("<<ComboboxSelected>>", self._clear_combo_highlight)

        ttk.Label(entry_frame, text="Addu Email:").grid(
            row=3, column=0, padx=10, pady=_PY, sticky="w"
        )
        self.email_entry = ttk.Entry(entry_frame, width=_FW)
        self.email_entry.grid(row=3, column=1, padx=10, pady=_PY, sticky="ew")

        ttk.Label(entry_frame, text="Committee:").grid(
            row=4, column=0, padx=10, pady=_PY, sticky="w"
        )
        self.committee_combo = ModernDropdown(entry_frame, width=_FW, state="readonly")
        self.committee_combo["values"] = self.load_committees()
        self.committee_combo.grid(row=4, column=1, padx=10, pady=_PY, sticky="ew")

        ttk.Label(entry_frame, text="Role:").grid(
            row=5, column=0, padx=10, pady=_PY, sticky="w"
        )
        self.role_combo = ModernDropdown(
            entry_frame,
            width=_FW,
            state="readonly",
            values=[
                "Chairperson",
                "Secretary-General",
                "Finance Officer",
                "G12 Commissioner",
                "G11 Commissioner",
                "Public Information Officer",
                "Auditor",
                "Committee Head Commissioner",
                "Asst. Committee Head Commissioner",
                "Member",
            ],
        )
        self.role_combo.grid(row=5, column=1, padx=10, pady=_PY, sticky="ew")

        button_frame = ttk.Frame(add_student_frame)
        button_frame.pack(fill="x", padx=10, pady=(5, 10))

        self.committee_combo.bind("<<ComboboxSelected>>", self._clear_combo_highlight)
        self.role_combo.bind("<<ComboboxSelected>>", self._clear_combo_highlight)

        ttk.Button(
            button_frame,
            text="+ Add Student",
            style="Add.TButton",
            command=self.add_student,
        ).pack(side="left", padx=8, ipadx=0)

        # --- Assign Tasks section (right) - Add Task Functionality ---
        assign_tasks_frame = ttk.LabelFrame(container, text="Assign Tasks")
        assign_tasks_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=5)

        # Single grid block for all 10 rows — labels col0, fields col1, uniform
        assign_tasks_frame.columnconfigure(0, weight=0, minsize=110)
        assign_tasks_frame.columnconfigure(1, weight=1)
        _AFW = 22  # same field width as left form for visual alignment

        ttk.Label(assign_tasks_frame, text="Task Name:").grid(
            row=0, column=0, padx=10, pady=6, sticky="w"
        )
        self.task_name_entry = ttk.Entry(assign_tasks_frame, width=_AFW)
        self.task_name_entry.grid(row=0, column=1, padx=10, pady=6, sticky="ew")

        ttk.Label(assign_tasks_frame, text="Committee:").grid(
            row=1, column=0, padx=10, pady=6, sticky="w"
        )
        self.task_committee_combo = ModernDropdown(
            assign_tasks_frame, width=_AFW, state="readonly"
        )
        self.task_committee_combo.grid(row=1, column=1, padx=10, pady=6, sticky="ew")

        ttk.Label(assign_tasks_frame, text="Due Date (YYYY-MM-DD):").grid(
            row=2, column=0, padx=10, pady=6, sticky="w"
        )
        self.task_due_date_entry = ttk.Entry(assign_tasks_frame, width=_AFW)
        self.task_due_date_entry.grid(row=2, column=1, padx=10, pady=6, sticky="ew")

        add_task_button = ttk.Button(
            assign_tasks_frame,
            text="Add Task",
            style="Add.TButton",
            command=self.add_task,
        )
        add_task_button.grid(row=3, column=0, columnspan=2, pady=15)

        self.task_committee_combo.bind(
            "<<ComboboxSelected>>", self._clear_combo_highlight
        )
        self._load_committees_for_task()

        ttk.Label(
            assign_tasks_frame,
            text="--- Assign Task to Member ---",
            font=("Segoe UI", 9, "italic"),
        ).grid(row=4, column=0, columnspan=2, pady=(10, 5))

        ttk.Label(assign_tasks_frame, text="Task:").grid(
            row=5, column=0, padx=10, pady=6, sticky="w"
        )
        self.assign_task_combo = ModernDropdown(
            assign_tasks_frame, width=_AFW, state="readonly"
        )
        self.assign_task_combo.grid(row=5, column=1, padx=10, pady=6, sticky="ew")

        ttk.Label(assign_tasks_frame, text="Member:").grid(
            row=6, column=0, padx=10, pady=6, sticky="w"
        )
        self.assign_member_combo = ModernDropdown(
            assign_tasks_frame, width=_AFW, state="readonly"
        )
        self.assign_member_combo.grid(row=6, column=1, padx=10, pady=6, sticky="ew")

        ttk.Label(assign_tasks_frame, text="Date Assigned (YYYY-MM-DD):").grid(
            row=7, column=0, padx=10, pady=6, sticky="w"
        )
        self.assign_date_entry = ttk.Entry(assign_tasks_frame, width=_AFW)
        self.assign_date_entry.grid(row=7, column=1, padx=10, pady=6, sticky="ew")

        ttk.Label(assign_tasks_frame, text="Status:").grid(
            row=8, column=0, padx=10, pady=6, sticky="w"
        )
        self.assign_status_combo = ModernDropdown(
            assign_tasks_frame, width=_AFW, state="readonly"
        )
        self.assign_status_combo.grid(row=8, column=1, padx=10, pady=6, sticky="ew")
        self.assign_status_combo["values"] = [
            "Pending",
            "In Progress",
            "Completed",
            "Cancelled",
        ]
        if self.assign_status_combo["values"]:
            self.assign_status_combo.current(0)

        assign_task_button = ttk.Button(
            assign_tasks_frame,
            text="Assign Task",
            style="Add.TButton",
            command=self.assign_task,
        )
        assign_task_button.grid(row=9, column=0, columnspan=2, pady=15)

        self.assign_task_combo.bind("<<ComboboxSelected>>", self._clear_combo_highlight)
        self.assign_member_combo.bind(
            "<<ComboboxSelected>>", self._clear_combo_highlight
        )
        self.assign_status_combo.bind(
            "<<ComboboxSelected>>", self._clear_combo_highlight
        )
        self._load_tasks_for_assignment()
        self._load_members_for_assignment()

    def create_tasks_assignments_tab(self, parent):
        settings_frame = ttk.Frame(parent)
        settings_frame.grid(row=0, column=0, sticky="nsew")
        self.pages["task/assignment"] = settings_frame

        # Create a container for the two sections
        container = ttk.Frame(settings_frame)
        container.pack(fill="both", expand=True, padx=15, pady=15)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1, uniform="task_sections")
        container.rowconfigure(1, weight=1, uniform="task_sections")

        # --- Task Management section (top) ---
        task_management_frame = ttk.LabelFrame(container, text="Task Management")
        task_management_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 5))

        self.tasks_tree = self._build_task_tree(task_management_frame)
        self.tasks_tree.bind(
            "<<TreeviewSelect>>", lambda e: self.on_task_select(self.tasks_tree)
        )

        # --- Assignment Management section (bottom) ---
        assignment_management_frame = ttk.LabelFrame(
            container, text="Assignment Management"
        )
        assignment_management_frame.grid(row=1, column=0, sticky="nsew", pady=(5, 0))

        # Placeholder label
        ttk.Label(assignment_management_frame, text="Placeholder").pack(
            expand=True, padx=20, pady=20
        )

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
            self._candidates_rows = [
                row[:7] for row in rows if row[6] == "Election Candidate"
            ]
            self._heads_rows = [
                row[:7]
                for row in rows
                if row[6]
                in ("Committee Head Commissioner", "Asst. Committee Head Commissioner")
            ]

            self.refresh_table_view()
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to load students: {e}")

    def load_tasks(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT t.TaskID, t.TaskName, c.CommitteeName, t.DueDate
                FROM Task t
                LEFT JOIN Committee c ON t.CommitteeID = c.CommitteeID
            """)
            rows = cursor.fetchall()
            cursor.close()

            self._tasks_rows = rows
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to load tasks: {e}")

    def refresh_table_view(self):
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)

        selected_view = self.view_combo.get()
        if selected_view == "ASHSCOM Members":
            data = self._members_rows
        elif selected_view == "Election Candidates":
            data = self._candidates_rows
        elif selected_view == "Committee Heads":
            data = self._heads_rows
        else:
            data = self._all_students_rows

        query = self.search_var.get().strip().lower() if hasattr(self, "search_var") else ""
        if query:
            data = [
                row for row in data
                if any(query in str(field).lower() for field in row if field is not None)
            ]

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
            messagebox.showwarning(
                "Input Error",
                "Please select a role for the Student. If the Student is an Election Candidate, please select the Committee and Role accordingly.",
            )
            return

        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO Student (StudentName, GradeLevel, Section, AdduEmail) VALUES (%s, %s, %s, %s)",
                (name, grade, section, email),
            )
            new_student_id = cursor.lastrowid

            if committee_name or role:
                committee_id = (
                    next(
                        (
                            cid
                            for cid, cname in self.committees_list
                            if cname == committee_name
                        ),
                        None,
                    )
                    if committee_name
                    else None
                )
                cursor.execute(
                    "INSERT INTO Member (StudentID, CommitteeID, OfficerRole) VALUES (%s, %s, %s)",
                    (new_student_id, committee_id, role if role else "Member"),
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
        self.grade_entry.set("")
        self.section_entry.set("")
        self.section_entry["values"] = []
        self.email_entry.delete(0, tk.END)
        self.committee_combo.set("")
        self.role_combo.set("")

    def clear_edit_form(self):
        self.edit_name_entry.delete(0, tk.END)
        self.edit_grade_entry.set("")
        self.edit_section_entry.set("")
        self.edit_section_entry["values"] = []
        self.edit_email_entry.delete(0, tk.END)
        self.edit_committee_combo.set("")
        self.edit_role_combo.set("")

    def _prompt_unlock(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Enter Passkey")
        dialog.configure(bg="#F7FFF9")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        dialog.update_idletasks()
        w, h = 320, 180
        x = (dialog.winfo_screenwidth() // 2) - (w // 2)
        y = (dialog.winfo_screenheight() // 2) - (h // 2)
        dialog.geometry(f"{w}x{h}+{x}+{y}")
        content = tk.Frame(dialog, bg="#F7FFF9")
        content.pack(fill="both", expand=True, padx=20, pady=15)

        ttk.Label(content, text="Enter passkey to view student records:",
                  font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 8))

        entry_var = tk.StringVar()
        entry = ttk.Entry(content, textvariable=entry_var, width=3, show="*")
        entry.pack(fill="x", pady=(0, 8))
        entry.focus_set()

        show_var = tk.BooleanVar(value=False)

        def toggle_show():
            entry.config(show="" if show_var.get() else "*")

        tk.Checkbutton(content, text="Show passkey", variable=show_var,
                       command=toggle_show, bg="#F7FFF9", fg="#0F1A0F",
                       activebackground="#F7FFF9", font=("Segoe UI", 9),
                       selectcolor="white").pack(anchor="w", pady=(0, 15))

        result = {"value": None}

        def confirm():
            result["value"] = entry_var.get()
            dialog.destroy()

        def cancel():
            dialog.destroy()

        btn_row = tk.Frame(content, bg="#F7FFF9")
        btn_row.pack(anchor="w")
        ttk.Button(btn_row, text="Confirm", style="Add.TButton", command=confirm, width=10).pack(
            side="left", padx=(0, 8)
        )
        ttk.Button(btn_row, text="Cancel", style="Update.TButton", command=cancel, width=10).pack(
            side="left"
        )

        entry.bind("<Return>", lambda e: confirm())
        dialog.wait_window()

        entered = result["value"]
        if entered is None:
            return
        if entered == self.STUDENT_PASSKEY:
            self.data_frame.tkraise()
            self.load_students()
        else:
            messagebox.showerror("Access Denied", "Incorrect passkey.")

    def on_student_select(self, tree):
        selected = tree.focus()
        if selected:
            values = tree.item(selected, "values")
            if values:
                self.edit_name_entry.delete(0, tk.END)
                self.edit_name_entry.insert(0, values[1])
                grade_value = values[2] if values[2] else ""
                self.edit_grade_entry.set(grade_value)
                self.edit_section_entry["values"] = GRADE_SECTIONS.get(grade_value, [])
                self.edit_section_entry.set(values[3] if values[3] else "")
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
        if not hasattr(self, "_selected_student_id") or not self._selected_student_id:
            messagebox.showwarning(
                "Selection Error", "Please select a Student to update."
            )
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
            cursor.execute(
                "UPDATE Student SET StudentName=%s, GradeLevel=%s, Section=%s, AdduEmail=%s WHERE StudentID=%s",
                (name, grade, section, email, student_id),
            )

            if committee_name or role:
                committee_id = (
                    next(
                        (
                            cid
                            for cid, cname in self.committees_list
                            if cname == committee_name
                        ),
                        None,
                    )
                    if committee_name
                    else None
                )
                cursor.execute(
                    """
                    INSERT INTO Member (StudentID, CommitteeID, OfficerRole) VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE CommitteeID=%s, OfficerRole=%s
                """,
                    (
                        student_id,
                        committee_id,
                        role if role else "Member",
                        committee_id,
                        role if role else "Member",
                    ),
                )

            self.connection.commit()
            cursor.close()
            messagebox.showinfo("Success", "Student updated successfully.")
            self.clear_edit_form()
            self.load_students()
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to update student: {e}")

    def delete_student(self):
        if not hasattr(self, "_selected_student_id") or not self._selected_student_id:
            messagebox.showwarning(
                "Selection Error", "Please select a Student to delete."
            )
            return
        student_id = self._selected_student_id
        if messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete this Student #{student_id}?",
        ):
            try:
                cursor = self.connection.cursor()
                cursor.execute("DELETE FROM Student WHERE StudentID=%s", (student_id,))
                self.connection.commit()
                cursor.close()
                messagebox.showinfo(
                    "Success", f"Student {student_id} deleted successfully."
                )
                self.clear_edit_form()
                self.load_students()
            except Error as e:
                messagebox.showerror("Database Error", f"Failed to delete student: {e}")

    def _load_committees_for_task(self):
        """Load committees for the task committee dropdown."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT CommitteeID, CommitteeName FROM Committee")
            self.committees_list = (
                cursor.fetchall()
            )  # Store as list of tuples (ID, Name)
            cursor.close()

            # Populate the combobox with committee names
            committee_names = [name for (_id, name) in self.committees_list]
            self.task_committee_combo["values"] = committee_names
            if committee_names:
                self.task_committee_combo.current(0)
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to load committees: {e}")

    def add_task(self):
        """Add a new task to the database."""
        task_name = self.task_name_entry.get().strip()
        committee_selection = self.task_committee_combo.get()
        due_date = self.task_due_date_entry.get().strip()

        # Validation
        if not task_name:
            messagebox.showwarning("Input Error", "Task name is required.")
            return

        if not committee_selection:
            messagebox.showwarning("Input Error", "Please select a committee.")
            return

        if not due_date:
            messagebox.showwarning("Input Error", "Due date is required.")
            return

        # Validate date format (basic validation)
        import re

        if not re.match(r"^\d{4}-\d{2}-\d{2}$", due_date):
            messagebox.showwarning(
                "Input Error", "Due date must be in YYYY-MM-DD format."
            )
            return

        # Get CommitteeID from the selection
        committee_id = None
        for cid, cname in self.committees_list:
            if cname == committee_selection:
                committee_id = cid
                break

        if committee_id is None:
            messagebox.showerror("Error", "Could not determine Committee ID.")
            return

        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                INSERT INTO Task (TaskName, CommitteeID, DueDate)
                VALUES (%s, %s, %s)
            """,
                (task_name, committee_id, due_date),
            )

            self.connection.commit()
            cursor.close()

            messagebox.showinfo("Success", "Task added successfully.")

            # Clear the form
            self.task_name_entry.delete(0, tk.END)
            self.task_committee_combo.set("")
            self.task_due_date_entry.delete(0, tk.END)

            # Refresh the committee dropdown in case new committees were added
            self._load_committees_for_task()

        except Error as e:
            messagebox.showerror("Database Error", f"Failed to add task: {e}")

    def _load_tasks_for_assignment(self):
        """Load tasks for the assignment task dropdown."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT TaskID, TaskName FROM Task")
            self.tasks_list = cursor.fetchall()  # Store as list of tuples (ID, Name)
            cursor.close()

            # Populate the combobox with task names
            task_names = [name for (_id, name) in self.tasks_list]
            self.assign_task_combo["values"] = task_names
            if task_names:
                self.assign_task_combo.current(0)
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to load tasks: {e}")

    def _load_members_for_assignment(self):
        """Load members for the assignment member dropdown."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT m.MemberID, s.StudentName
                FROM Member m
                JOIN Student s ON m.StudentID = s.StudentID
            """)
            self.members_list = cursor.fetchall()  # Store as list of tuples (ID, Name)
            cursor.close()

            # Populate the combobox with student names
            member_names = [name for (_id, name) in self.members_list]
            self.assign_member_combo["values"] = member_names
            if member_names:
                self.assign_member_combo.current(0)
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to load members: {e}")

    def assign_task(self):
        """Assign a task to a member."""
        task_selection = self.assign_task_combo.get()
        member_selection = self.assign_member_combo.get()
        date_assigned = self.assign_date_entry.get().strip()
        status = self.assign_status_combo.get()

        # Validation
        if not task_selection:
            messagebox.showwarning("Input Error", "Please select a task.")
            return

        if not member_selection:
            messagebox.showwarning("Input Error", "Please select a member.")
            return

        if not date_assigned:
            messagebox.showwarning("Input Error", "Date assigned is required.")
            return

        # Validate date format (basic validation)
        import re

        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_assigned):
            messagebox.showwarning(
                "Input Error", "Date assigned must be in YYYY-MM-DD format."
            )
            return

        if not status:
            messagebox.showwarning("Input Error", "Please select a status.")
            return

        # Get TaskID from the selection
        task_id = None
        for tid, tname in self.tasks_list:
            if tname == task_selection:
                task_id = tid
                break

        if task_id is None:
            messagebox.showerror("Error", "Could not determine Task ID.")
            return

        # Get MemberID from the selection
        member_id = None
        for mid, mname in self.members_list:
            if mname == member_selection:
                member_id = mid
                break

        if member_id is None:
            messagebox.showerror("Error", "Could not determine Member ID.")
            return

        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                INSERT INTO Assignment (TaskID, MemberID, DateAssigned, Status)
                VALUES (%s, %s, %s, %s)
            """,
                (task_id, member_id, date_assigned, status),
            )

            self.connection.commit()
            cursor.close()

            messagebox.showinfo("Success", "Task assigned successfully.")

            # Clear the form
            self.assign_task_combo.set("")
            self.assign_member_combo.set("")
            self.assign_date_entry.delete(0, tk.END)
            self.assign_status_combo.set("")

            # Refresh dropdowns
            self._load_tasks_for_assignment()
            self._load_members_for_assignment()

        except Error as e:
            messagebox.showerror("Database Error", f"Failed to assign task: {e}")
     
     

if __name__ == "__main__":
    root = tk.Tk()
    app = AshscomGUI(root)
    root.mainloop()

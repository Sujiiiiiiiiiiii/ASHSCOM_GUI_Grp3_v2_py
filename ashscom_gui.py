import os
import tkinter as tk
from tkinter import ttk, messagebox
from types import SimpleNamespace
from PIL import Image, ImageTk
import customtkinter as ctk
import mysql.connector
from mysql.connector import Error


def create_connection():
    """Open the configured ASHSCOM database connection."""
    for password in ("root", "roots"):
        try:
            connection = mysql.connector.connect(
                host="127.0.0.1",
                user="root",
                password=password,
                database="ASHCOMManagement",
            )
            if connection.is_connected():
                return connection
        except Error as error:
            if password == "roots":
                print(f"Error while connecting to MySQL: {error}")
    return None


# ---------------------------------------------------------------------------
# Grade Level -> Sections map (alphabetical)
# ---------------------------------------------------------------------------
GRADE_SECTIONS = {
    "Grade 11": [
        "GARNET",
        "GARNIER",
        "GAVAN",
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
    BORDER = "#DDE3EA"
    BORDER_ACTIVE = "#10A37F"
    TEXT = "#172033"
    PLACEHOLDER = "#6C757D"
    HOVER = "#E8F5E9"  # Very soft light green
    SELECTED = "#C8E6C9"  # Solid light green
    ARROW = "#10A37F"
    ARROW_HOVER = "#087A64"
    ROW_HEIGHT = 26
    MAX_VISIBLE_ROWS = 4

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
            text="Select an option",
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
            bg=self.ARROW,
            fg="white",
            font=("Segoe UI", 11, "bold"),
            padx=6,
            width=1,
            anchor="center",
            relief="flat",
            bd=0,
            cursor="hand2",
        )
        self._arrow.pack(side="right", fill="y")

        for w in (self, inner, self._label, self._arrow):
            w.bind("<Button-1>", self._toggle)
        for w in (self, inner, self._label, self._arrow):
            w.bind("<Enter>", lambda e: self.config(bg=self.BORDER_ACTIVE))
            w.bind("<Leave>", self._on_leave)
        self._arrow.bind("<Enter>", lambda e: self._arrow.config(bg=self.ARROW_HOVER))
        self._arrow.bind("<Leave>", lambda e: self._arrow.config(bg=self.ARROW))

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
            self._label.config(text="Select an option", fg=self.PLACEHOLDER)

    def _select(self, value, notify=True, close_popup=True):
        self._value = value
        self._render()
        if close_popup:
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
        top = self.winfo_rooty()
        y = top + self.winfo_height()
        width = max(self.winfo_width(), 140)
        visible_rows = min(len(self._values), self.MAX_VISIBLE_ROWS)
        height = visible_rows * self.ROW_HEIGHT + 2

        screen_height = self.winfo_screenheight()
        space_below = max(screen_height - y - 8, self.ROW_HEIGHT + 2)
        space_above = max(top - 8, self.ROW_HEIGHT + 2)
        if y + height > screen_height and space_above > space_below:
            height = min(height, space_above)
            y = top - height
        else:
            height = min(height, space_below)

        popup = tk.Toplevel(self)
        popup.wm_overrideredirect(True)
        popup.lift()
        popup.wm_geometry(f"{width}x{height}+{x}+{y}")
        popup.config(bg=self.BORDER_ACTIVE)
        popup.grab_set()
        self._popup = popup

        frame = tk.Frame(popup, bg="white")
        frame.pack(fill="both", expand=True, padx=1, pady=1)

        needs_scroll = len(self._values) > self.MAX_VISIBLE_ROWS
        canvas = tk.Canvas(frame, bg="white", highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)
        list_frame = tk.Frame(canvas, bg="white")

        if needs_scroll:
            scrollbar_track = tk.Frame(frame, bg="white", width=16)
            scrollbar_track.place(
                relx=1.0, rely=0, relwidth=16 / width, relheight=1, anchor="ne"
            )
            scrollbar = tk.Canvas(
                scrollbar_track,
                width=16,
                bg="white",
                highlightthickness=0,
                bd=0,
            )
            scrollbar.pack(fill="both", expand=True)

            def update_scrollbar(first, last):
                scrollbar.delete("thumb")
                track_height = max(scrollbar.winfo_height(), 1)
                track_top = 2
                track_bottom = max(track_top + 24, track_height - 2)
                first_y = track_top + int(float(first) * (track_bottom - track_top))
                last_y = track_top + int(float(last) * (track_bottom - track_top))
                if last_y - first_y < 24:
                    last_y = min(track_bottom, first_y + 24)
                first_y = max(track_top, min(first_y, track_bottom - 24))
                last_y = max(first_y + 24, min(last_y, track_bottom))
                scrollbar.create_rectangle(
                    3,
                    first_y,
                    13,
                    last_y,
                    fill="#10A37F",
                    outline="#087A64",
                    tags="thumb",
                )

            drag_state = {"offset": None}

            def scroll_from_click(event):
                scrollbar_height = max(scrollbar.winfo_height(), 1)
                thumb = scrollbar.bbox("thumb")
                if thumb and thumb[1] <= event.y <= thumb[3]:
                    drag_state["offset"] = event.y - thumb[1]
                else:
                    drag_state["offset"] = None
                    canvas.yview_moveto(max(0, min(1, event.y / scrollbar_height)))

            def drag_scrollbar(event):
                if drag_state["offset"] is None:
                    return
                scrollbar_height = max(scrollbar.winfo_height(), 1)
                thumb = scrollbar.bbox("thumb")
                if not thumb:
                    return
                thumb_height = thumb[3] - thumb[1]
                target = event.y - drag_state["offset"]
                max_top = max(scrollbar_height - thumb_height, 1)
                canvas.yview_moveto(max(0, min(1, target / max_top)))

            def stop_drag(event=None):
                drag_state["offset"] = None

            scrollbar.bind("<Button-1>", scroll_from_click)
            scrollbar.bind("<B1-Motion>", drag_scrollbar)
            scrollbar.bind("<ButtonRelease-1>", stop_drag)
            canvas.configure(yscrollcommand=update_scrollbar)

        canvas.create_window(
            (0, 0),
            window=list_frame,
            anchor="nw",
            width=width - (20 if needs_scroll else 0),
        )

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
                font=("Segoe UI", 9),
                padx=10,
                pady=3,
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
            row.bind(
                "<Button-1>",
                lambda e, v=val: self._select_from_popup(v),
            )
            for w in (canvas, list_frame, row):
                w.bind("<MouseWheel>", on_wheel)
                w.bind("<Button-4>", on_wheel)
                w.bind("<Button-5>", on_wheel)

        list_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
        if needs_scroll:
            scrollbar.create_rectangle(
                3,
                2,
                13,
                max(24, scrollbar.winfo_height() - 2),
                fill="#10A37F",
                outline="#087A64",
                tags="thumb",
            )
            scrollbar.after_idle(lambda: update_scrollbar(*canvas.yview()))

        self._click_id = self.winfo_toplevel().bind_all(
            "<Button-1>", self._on_global_click, add="+"
        )

    def _select_from_popup(self, value):
        self._select(value, close_popup=False)
        if self._popup is not None:
            self._popup.after_idle(self._close_popup)
        return "break"

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
            try:
                self._popup.grab_release()
            except tk.TclError:
                pass
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


class ModernComboBox(ctk.CTkComboBox):
    """CTkComboBox adapter used by the existing validation and CRUD methods."""

    def __init__(self, master=None, width=20, state="readonly", values=None, **kwargs):
        self._selection_callbacks = []
        self._placeholder = "Select an option"
        kwargs.setdefault("height", 42)
        kwargs.setdefault("corner_radius", 11)
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("border_color", "#DDE3EA")
        kwargs.setdefault("fg_color", "#FFFFFF")
        kwargs.setdefault("button_color", "#10A37F")
        kwargs.setdefault("button_hover_color", "#087A64")
        kwargs.setdefault("dropdown_fg_color", "#FFFFFF")
        kwargs.setdefault("dropdown_hover_color", "#E8F5F1")
        kwargs.setdefault("dropdown_text_color", "#172033")
        kwargs.setdefault("dropdown_font", ("Segoe UI", 11))
        kwargs.setdefault("text_color", "#172033")
        kwargs.setdefault("font", ("Segoe UI", 11))
        kwargs.setdefault("justify", "left")
        kwargs["state"] = "normal" if state == "readonly" else state
        kwargs["command"] = self._notify_selection
        super().__init__(master, width=max(180, width * 10), values=values or [], **kwargs)
        super().set(self._placeholder)
        if state == "readonly":
            self._entry.bind(
                "<Key>", lambda event: "break", add="+"
            )
            self._entry.bind(
                "<<Paste>>", lambda event: "break", add="+"
            )
            self._entry.bind(
                "<<Cut>>", lambda event: "break", add="+"
            )

    def _notify_selection(self, _value=None):
        event = SimpleNamespace(widget=self)
        for callback in list(self._selection_callbacks):
            if callback:
                callback(event)

    def bind(self, sequence=None, func=None, add=None):
        if sequence == "<<ComboboxSelected>>":
            self._selection_callbacks.append(func)
            return
        return super().bind(sequence, func, add)

    def configure(self, *args, **kwargs):
        if "values" in kwargs:
            kwargs["values"] = list(kwargs["values"] or [])
        return super().configure(*args, **kwargs)

    config = configure

    def __setitem__(self, key, value):
        if key == "values":
            self.configure(values=value)
        else:
            self.configure(**{key: value})

    def __getitem__(self, key):
        if key == "values":
            return list(self.cget("values"))
        return self.cget(key)

    def set(self, value):
        super().set(value or self._placeholder)

    def get(self):
        value = super().get()
        return "" if value == self._placeholder else value

    def current(self, index=None):
        values = list(self.cget("values"))
        if index is None:
            try:
                return values.index(self.get())
            except ValueError:
                return -1
        if 0 <= index < len(values):
            self.set(values[index])


class ModernButton(ctk.CTkButton):
    """CTkButton adapter for the existing ttk style names."""

    def __init__(self, master=None, **kwargs):
        style = kwargs.pop("style", "Add.TButton")
        palette = {
            "Delete.TButton": ("#DC5A5A", "#B94747"),
            "Update.TButton": ("#2878B5", "#1C5F91"),
            "Add.TButton": ("#10A37F", "#087A64"),
        }
        fg_color, hover_color = palette.get(style, palette["Add.TButton"])
        kwargs.setdefault("fg_color", fg_color)
        kwargs.setdefault("hover_color", hover_color)
        kwargs.setdefault("text_color", "#FFFFFF")
        kwargs.setdefault("corner_radius", 9)
        kwargs.setdefault("height", 40)
        kwargs.setdefault("font", ("Segoe UI", 12, "bold"))
        super().__init__(master, **kwargs)

    config = ctk.CTkButton.configure


class AshscomGUI:
    STUDENT_PASSKEY = "ashscom2026"
    ACTION_PIN = "1835"
    THEME = {
        "navy": "#0B2942",
        "navy_dark": "#071D30",
        "green": "#10A37F",
        "green_dark": "#087A64",
        "green_soft": "#E8F5F1",
        "gold": "#F4C95D",
        "background": "#F5F7FA",
        "card": "#FFFFFF",
        "text": "#172033",
        "muted": "#667085",
        "border": "#DDE3EA",
        "danger": "#DC5A5A",
        "info": "#2878B5",
    }

    def __init__(self, root):
        self.root = root
        self.root.title("Ashscom Management System")
        self.root.geometry("1280x820")
        self.root.minsize(980, 680)
        self.root.configure(fg_color=self.THEME["background"])
        self.setup_styles()
        self.root.configure(fg_color=self.THEME["background"])

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        BG_COLOR = self.THEME["background"]
        PANEL_BG = self.THEME["card"]
        CARD_BG = self.THEME["card"]
        ADDU_BLUE = self.THEME["navy"]
        ADDU_BLUE_DARK = self.THEME["navy_dark"]
        ADDU_BLUE_LIGHT = self.THEME["info"]
        ADDU_GOLD = self.THEME["gold"]
        ACTION_GREEN = self.THEME["green"]
        ACTION_GREEN_DARK = self.THEME["green_dark"]
        SOFT_GREEN = self.THEME["green_soft"]
        TEXT = self.THEME["text"]
        MUTED = self.THEME["muted"]

        style.configure("TFrame", background=BG_COLOR)
        style.configure("Card.TFrame", background=CARD_BG)
        style.configure("TLabelframe", background=CARD_BG, bordercolor=self.THEME["border"], relief="solid", borderwidth=1)
        style.configure("TLabel", background=BG_COLOR, font=("Segoe UI", 10), foreground=TEXT)
        style.configure(
            "Form.TLabel",
            background=CARD_BG,
            foreground=TEXT,
            font=("Segoe UI", 10, "bold"),
        )
        style.configure(
            "Student.TLabelframe",
            background=CARD_BG,
            bordercolor=self.THEME["border"],
            relief="solid",
            borderwidth=1,
        )
        style.configure(
            "Student.TLabelframe.Label",
            background=CARD_BG,
            foreground=self.THEME["navy"],
            font=("Segoe UI", 11, "bold"),
        )

        style.configure(
            "TLabelframe.Label",
            font=("Segoe UI", 11, "bold"),
            foreground="#1a2e3d",
            background=CARD_BG,
        )

        style.configure(
            "Assign.TLabelframe",
            background=CARD_BG,
            bordercolor=self.THEME["border"],
            relief="flat",
            borderwidth=1,
        )
        style.configure(
            "Assign.TLabelframe.Label",
            font=("Segoe UI", 11, "bold"),
            foreground=self.THEME["navy"],
            background=CARD_BG,
        )

        style.configure("Modern.Sub.TNotebook", background=BG_COLOR, borderwidth=0)
        style.configure(
            "Modern.Sub.TNotebook.Tab",
            font=("Segoe UI", 9, "bold"),
            padding=[18, 8],
            background="#EEF2F5",
            foreground=self.THEME["navy"],
        )
        style.map(
            "Modern.Sub.TNotebook.Tab",
            background=[("selected", ACTION_GREEN), ("active", "#DDF1EB")],
            foreground=[("selected", "white")],
        )

        style.configure("TEntry", padding=9, relief="flat", bordercolor=self.THEME["border"], fieldbackground=CARD_BG, foreground=TEXT)
        style.map(
            "TEntry",
            bordercolor=[("focus", ACTION_GREEN)],
            lightcolor=[("focus", ACTION_GREEN)],
            darkcolor=[("focus", ACTION_GREEN)],
        )

        style.configure(
            "Add.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=10,
            background=ACTION_GREEN,
            foreground="white",
            borderwidth=0,
            relief="flat",
        )
        style.map(
            "Add.TButton",
            background=[("active", ACTION_GREEN_DARK)],
            foreground=[("active", "white")],
        )

        style.configure(
            "Update.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=9,
            background="#177A5A",
            foreground="#FFFFFF",
            borderwidth=0,
        )
        style.map(
            "Update.TButton",
            background=[("active", ACTION_GREEN_DARK), ("disabled", "#A8DCC7")],
            foreground=[("disabled", "#FFFFFF")],
        )
        style.configure(
            "Delete.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=9,
            background="#D75D5D",
            foreground="white",
            borderwidth=0,
        )
        style.map(
            "Delete.TButton",
            background=[("active", "#C44646"), ("disabled", "#F3B8B8")],
            foreground=[("disabled", "#F4F6F9")],
        )

        style.configure(
            "Treeview",
            font=("Segoe UI", 10),
            rowheight=36,
            background="#ffffff",
            fieldbackground="#ffffff",
            foreground=TEXT,
            borderwidth=0,
            relief="flat",
        )
        style.map(
            "Treeview",
            background=[("selected", "#DDF5EA")],
            foreground=[("selected", "#0D684A")],
        )
        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 10, "bold"),
            background=ADDU_BLUE,
            foreground="white",
            relief="flat",
            borderwidth=0,
            padding=(0, 7),
        )
        style.map("Treeview.Heading", background=[("active", "#00205B")])
        style.layout(
            "Treeview.Heading",
            [
                (
                    "Treeheading.cell",
                    {
                        "sticky": "nswe",
                        "children": [
                            (
                                "Treeheading.padding",
                                {
                                    "sticky": "nswe",
                                    "children": [
                                        ("Treeheading.text", {"sticky": "we"})
                                    ],
                                },
                            )
                        ],
                    },
                )
            ],
        )
        self.root.option_add("*TEntry*selectBackground", "#D4FFD9")
        self.root.option_add("*TEntry*selectForeground", "#004202")
        self.root.option_add("*Entry.selectBackground", "#D4FFD9")
        self.root.option_add("*Entry.selectForeground", "#004202")

        header_canvas = tk.Canvas(self.root, height=112, highlightthickness=0, bg="#24551B")
        header_canvas.pack(fill="x")

        logo1_img = Image.open(os.path.join(os.path.dirname(__file__), "ateneo1.png")).resize((58, 58))
        self.logo1 = ImageTk.PhotoImage(logo1_img)

        logo2_img = Image.open("ashscom.png").resize((70, 70))
        self.logo2 = ImageTk.PhotoImage(logo2_img)

        # Modernized scrollbars
        style.configure(
            "Vertical.TScrollbar",
            background="#B8C5D1",
            troughcolor="#EEF2F5",
            bordercolor="#EEF2F5",
            arrowcolor=ADDU_BLUE,
            relief="flat",
            gripcount=0,
        )
        style.map(
            "Vertical.TScrollbar",
            background=[("active", ACTION_GREEN), ("pressed", ACTION_GREEN_DARK)],
        )

        style.configure(
            "Horizontal.TScrollbar",
            background="#B8C5D1",
            troughcolor="#EEF2F5",
            bordercolor="#EEF2F5",
            arrowcolor=ADDU_BLUE,
            relief="flat",
            gripcount=0,
        )
        style.map(
            "Horizontal.TScrollbar",
            background=[("active", ACTION_GREEN), ("pressed", ACTION_GREEN_DARK)],
        )

        def redraw_header(event):
            width = max(1, event.width)
            height = 112
            header_canvas.delete("all")

            def mix(c1, c2, ratio):
                r1, g1, b1 = self.root.winfo_rgb(c1)
                r2, g2, b2 = self.root.winfo_rgb(c2)
                r = int(r1/256 + (r2/256 - r1/256) * ratio)
                g = int(g1/256 + (g2/256 - g1/256) * ratio)
                b = int(b1/256 + (b2/256 - b1/256) * ratio)
                return f"#{r:02x}{g:02x}{b:02x}"

            for i in range(height):
                ratio = i / max(1, height - 1)
                color = mix("#173B16", "#24551B", ratio)
                header_canvas.create_line(0, i, width, i, fill=color, width=1)

            header_canvas.create_rectangle(0, height - 3, width, height, fill="#437118", outline="")
            header_canvas.create_image(24, 56, image=self.logo1, anchor="w")
            header_canvas.create_image(88, 56, image=self.logo2, anchor="w")
            header_canvas.create_line(
                174, 24, 174, 88, fill="#AFDD6E", width=1
            )

            header_canvas.create_text(
                width - 18,
                30,
                text="Ateneo De Davao University Senior High School",
                font=("Segoe UI", 16, "bold"),
                fill="#F5F3D8",
                anchor="e",
            )
            header_canvas.create_text(
                width - 18,
                54,
                text="Commission on Elections",
                font=("Segoe UI", 15, "bold"),
                fill="#F5F3D8",
                anchor="e",
            )
            header_canvas.create_text(
                width - 18,
                84,
                text="ASHSCOM MANAGEMENT SYSTEM",
                font=("Segoe UI", 22, "bold"),
                fill="#AFDD6E",
                anchor="e",
            )

        header_canvas.bind("<Configure>", redraw_header)

        header_nav = ctk.CTkFrame(
            self.root, fg_color="#173B16", height=62, corner_radius=0
        )
        header_nav.pack(fill="x")
        header_nav.pack_propagate(False)

        divider = tk.Frame(self.root, bg="#437118", height=3)
        divider.pack(fill="x")

        # Create a connection to the database
        self.connection = create_connection()
        if not self.connection or not self.connection.is_connected():
            messagebox.showerror("Database Error", "Failed to connect to the database.")
            self.root.destroy()
            return

        body_frame = ctk.CTkFrame(self.root, fg_color=BG_COLOR, corner_radius=0)
        body_frame.pack(expand=True, fill="both")

        content_frame = ctk.CTkFrame(body_frame, fg_color=BG_COLOR, corner_radius=0)
        content_frame.pack(expand=True, fill="both")

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
                b.configure(fg_color="#173B16", text_color="#E8F5D0")
                self.nav_accents[key].configure(fg_color="#173B16")
            self.nav_buttons[name].configure(fg_color="#10A37F", text_color="#FFFFFF")
            self.nav_accents[name].configure(fg_color="#AFDD6E")

        nav_buttons = [
            ("Students", "students"),
            ("Add Student / Tasks", "add_student"),
            ("Tasks & Assignments", "task/assignment"),
        ]
        ctk.CTkLabel(
            header_nav,
            text="WORKSPACE",
            text_color="#87AECE",
            font=("Segoe UI", 11, "bold"),
            anchor="w",
        ).pack(side="left", padx=(28, 22), pady=0)
        nav_frame = ctk.CTkFrame(header_nav, fg_color="transparent", corner_radius=0)
        nav_frame.pack(side="left", fill="y")
        for label, key in nav_buttons:
            row = ctk.CTkFrame(nav_frame, fg_color="transparent", corner_radius=0)
            row.pack(side="left", fill="y", padx=(0, 8))

            accent = ctk.CTkFrame(row, fg_color="#173B16", width=5, height=44, corner_radius=2)
            accent.pack(side="left", fill="y", padx=(0, 6), pady=9)
            self.nav_accents[key] = accent

            btn = ctk.CTkButton(
                row,
                text=label,
                font=("Segoe UI", 13, "bold"),
                fg_color="#173B16",
                hover_color="#24551B",
                text_color="#E8F5D0",
                corner_radius=8,
                anchor="center",
                height=44,
                cursor="hand2",
                width=180,
                command=lambda k=key: show_page(k),
            )
            btn.pack(side="left", fill="y", padx=(0, 0), pady=9)
            self.nav_buttons[key] = btn

            def on_enter(e, k=key):
                if self.nav_buttons_active != k:
                    self.nav_buttons[k].configure(fg_color="#24551B")

            def on_leave(e, k=key):
                if self.nav_buttons_active != k:
                    self.nav_buttons[k].configure(fg_color="#173B16")

            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)

        self.create_students_tab(content_frame)
        self.create_add_student_tab(content_frame)
        self.create_tasks_assignments_tab(content_frame)

        show_page("students")

    def _calendar_btn(self, parent, entry):
        btn = tk.Button(
            parent,
            text="📅",
            command=self._attach_date_picker(entry),
            bg=self.THEME["green"],
            fg="white",
            relief="flat",
            bd=0,
            borderwidth=0,
            highlightthickness=0,
            overrelief="flat",
            activebackground=self.THEME["green_dark"],
            activeforeground="white",
            padx=5,
            pady=4,
            width=3,
            height=1,
            cursor="hand2",
            font=("Segoe UI", 9),
        )
        btn.bind("<Enter>", lambda e: btn.config(bg=self.THEME["green_dark"]))
        btn.bind("<Leave>", lambda e: btn.config(bg=self.THEME["green"]))
        return btn

    def _attach_date_picker(self, entry):
        import calendar as cal_module
        from datetime import date

        def open_picker():
            popup = tk.Toplevel(self.root)
            popup.title("Select Date")
            popup.resizable(False, False)
            popup.transient(self.root)
            popup.grab_set()
            popup.geometry("320x270")
            popup.configure(bg=self.THEME["border"])
            try:
                popup.update_idletasks()
                rx = self.root.winfo_rootx() + (self.root.winfo_width() - 320) // 2
                ry = self.root.winfo_rooty() + (self.root.winfo_height() - 270) // 2
                popup.geometry(f"320x270+{rx}+{ry}")
            except Exception:
                pass
            state = {"year": date.today().year, "month": date.today().month}
            try:
                cur = entry.get().strip()
                if cur:
                    y, m, d = map(int, cur.split("-"))
                    state["year"], state["month"] = y, m
            except Exception:
                pass
            outer = tk.Frame(popup, bg=self.THEME["border"], bd=0)
            outer.pack(fill="both", expand=True)
            body = tk.Frame(outer, bg=self.THEME["card"])
            body.pack(fill="both", expand=True, padx=1, pady=1)
            header = tk.Frame(body, bg=self.THEME["navy"])
            header.pack(fill="x", ipady=8)

            def prev_month():
                state["month"] -= 1
                if state["month"] < 1:
                    state["month"] = 12
                    state["year"] -= 1
                render()

            def next_month():
                state["month"] += 1
                if state["month"] > 12:
                    state["month"] = 1
                    state["year"] += 1
                render()

            tk.Button(
                header,
                text="‹",
                command=prev_month,
                bg=self.THEME["navy"],
                fg="white",
                activebackground=self.THEME["info"],
                relief="flat",
                bd=0,
                highlightthickness=0,
                font=("Segoe UI", 12, "bold"),
                padx=8,
            ).pack(side="left")
            label = tk.Label(
                header, text="", font=("Segoe UI", 10, "bold"), bg=self.THEME["navy"], fg="white"
            )
            label.pack(side="left", expand=True)
            tk.Button(
                header,
                text="›",
                command=next_month,
                bg=self.THEME["navy"],
                fg="white",
                activebackground=self.THEME["info"],
                relief="flat",
                bd=0,
                highlightthickness=0,
                font=("Segoe UI", 12, "bold"),
                padx=8,
            ).pack(side="right")
            grid_frame = tk.Frame(body, bg=self.THEME["card"])
            grid_frame.pack(pady=(4, 2))

            def render():
                for w in grid_frame.winfo_children():
                    w.destroy()
                label.config(
                    text=f"{cal_module.month_name[state['month']]} {state['year']}"
                )
                for i, d in enumerate(["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]):
                    fg = self.THEME["danger"] if i >= 5 else self.THEME["navy"]
                    tk.Label(
                        grid_frame,
                        text=d,
                        width=4,
                        bg=self.THEME["card"],
                        fg=fg,
                        font=("Segoe UI", 8, "bold"),
                    ).grid(row=0, column=i, pady=(0, 4))
                sel = None
                try:
                    sel = entry.get().strip()
                except Exception:
                    sel = ""
                today = date.today()
                for r, week in enumerate(
                    cal_module.monthcalendar(state["year"], state["month"]), start=1
                ):
                    for c, day in enumerate(week):
                        if day == 0:
                            tk.Label(grid_frame, text="", width=4, bg=self.THEME["card"]).grid(
                                row=r, column=c
                            )
                            continue
                        iso = f"{state['year']:04d}-{state['month']:02d}-{day:02d}"
                        is_today = (
                            today.year == state["year"]
                            and today.month == state["month"]
                            and today.day == day
                        )
                        is_sel = iso == sel
                        bg = (
                            self.THEME["green"]
                            if is_sel
                            else (self.THEME["green_soft"] if is_today else self.THEME["card"])
                        )
                        fg = (
                            "white"
                            if is_sel
                            else (
                                self.THEME["green"]
                                if is_today
                                else (self.THEME["danger"] if c >= 5 else self.THEME["navy"])
                            )
                        )

                        def pick(d=day):
                            entry.delete(0, tk.END)
                            entry.insert(
                                0, f"{state['year']:04d}-{state['month']:02d}-{d:02d}"
                            )
                            popup.destroy()

                        b = tk.Button(
                            grid_frame,
                            text=str(day),
                            width=4,
                            relief="flat",
                            bd=0,
                            highlightthickness=0,
                            bg=bg,
                            fg=fg,
                            activebackground=self.THEME["green_dark"],
                            activeforeground="white",
                            font=(
                                "Segoe UI",
                                9,
                                "bold" if is_sel or is_today else "normal",
                            ),
                            command=pick,
                        )
                        b.grid(row=r, column=c, padx=1, pady=1)

            footer = tk.Frame(body, bg=self.THEME["card"])
            footer.pack(fill="x", side="bottom", pady=(4, 6), padx=8)

            def today_pick():
                entry.delete(0, tk.END)
                entry.insert(0, date.today().isoformat())
                popup.destroy()

            def clear_pick():
                entry.delete(0, tk.END)
                popup.destroy()

            ModernButton(
                footer,
                text="Today",
                command=today_pick,
                style="Add.TButton",
                width=76,
                height=32,
                corner_radius=9,
                font=("Segoe UI", 11, "bold"),
            ).pack(side="left")
            ModernButton(
                footer,
                text="Clear",
                command=clear_pick,
                fg_color="#EEF2F5",
                hover_color="#DDE3EA",
                text_color=self.THEME["navy"],
                width=76,
                height=32,
                corner_radius=9,
                font=("Segoe UI", 11, "bold"),
            ).pack(side="left", padx=(6, 0))
            ModernButton(
                footer,
                text="Cancel",
                command=popup.destroy,
                fg_color="#EEF2F5",
                hover_color="#DDE3EA",
                text_color=self.THEME["navy"],
                width=76,
                height=32,
                corner_radius=9,
                font=("Segoe UI", 11, "bold"),
            ).pack(side="right")
            render()

        return open_picker

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
        settings_frame = ctk.CTkFrame(parent, fg_color=self.THEME["card"], corner_radius=0)
        settings_frame.grid(row=0, column=0, sticky="nsew")
        self.pages["students"] = settings_frame

        overview_frame = tk.Frame(
            settings_frame,
            bg="white",
            padx=10,
            pady=10,
        )
        overview_frame.pack(fill="both", expand=True, padx=10, pady=10)

        overview_frame.columnconfigure(0, weight=1, minsize=460)
        overview_frame.columnconfigure(1, weight=2, minsize=520)
        overview_frame.rowconfigure(0, weight=1)

        # --- LEFT: Edit form ---
        form_frame = tk.LabelFrame(
            overview_frame,
            text="Update Student",
            bg="white",
            fg=self.THEME["navy"],
            font=("Segoe UI", 11, "bold"),
            bd=1,
            relief="solid",
            padx=10,
            pady=10,
        )
        form_frame.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=(10, 11))

        # inline grid layout — labels left, fields right (matches Add Student tab)
        # Fixed label-column width + identical field width/padding/pady on every
        # row so entries and comboboxes line up exactly under one another.
        form_frame.columnconfigure(0, weight=0, minsize=110)
        form_frame.columnconfigure(1, weight=1)
        FIELD_WIDTH = 22
        ROW_PADY = 6

        # --- Form fields ---
        ttk.Label(form_frame, text="Student Name:", style="Form.TLabel").grid(
            row=0, column=0, padx=10, pady=ROW_PADY, sticky="w"
        )
        self.edit_name_entry = ctk.CTkEntry(
            form_frame,
            width=220,
            height=38,
            corner_radius=10,
            border_color="#B8CBD8",
            placeholder_text="e.g. Juan Dela Cruz",
        )
        self.edit_name_entry.grid(row=0, column=1, padx=10, pady=ROW_PADY, sticky="ew")

        ttk.Label(form_frame, text="Grade Level:", style="Form.TLabel").grid(
            row=1, column=0, padx=10, pady=ROW_PADY, sticky="w"
        )
        self.edit_grade_entry = ModernDropdown(
            form_frame, width=FIELD_WIDTH, state="readonly", values=GRADE_LEVELS
        )
        self.edit_grade_entry.grid(row=1, column=1, padx=10, pady=ROW_PADY, sticky="ew")
        self.edit_grade_combo = self.edit_grade_entry

        ttk.Label(form_frame, text="Section:", style="Form.TLabel").grid(
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

        ttk.Label(form_frame, text="Addu Email:", style="Form.TLabel").grid(
            row=3, column=0, padx=10, pady=ROW_PADY, sticky="w"
        )
        email_row = tk.Frame(form_frame, bg="white")
        email_row.grid(row=3, column=1, padx=10, pady=ROW_PADY, sticky="ew")
        self.edit_email_entry = ctk.CTkEntry(
            email_row,
            width=150,
            height=38,
            corner_radius=10,
            border_color="#B8CBD8",
            placeholder_text="username",
        )
        self.edit_email_entry.pack(side="left")
        ttk.Label(email_row, text="@addu.edu.ph", style="Form.TLabel").pack(side="left")

        ttk.Label(form_frame, text="Committee:", style="Form.TLabel").grid(
            row=4, column=0, padx=10, pady=ROW_PADY, sticky="w"
        )
        self.edit_committee_combo = ModernDropdown(
            form_frame, width=FIELD_WIDTH, state="readonly"
        )
        self.edit_committee_combo["values"] = self.load_committees()
        self.edit_committee_combo.grid(
            row=4, column=1, padx=10, pady=ROW_PADY, sticky="ew"
        )

        ttk.Label(form_frame, text="Role:", style="Form.TLabel").grid(
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
        form_frame.rowconfigure(6, weight=0)
        button_row = tk.Frame(form_frame, bg="white")
        button_row.grid(row=7, column=0, columnspan=2, pady=(28, 12))

        self.update_btn = ModernButton(
            button_row,
            text="🔼 Update Selected",
            style="Update.TButton",
            command=self.update_student,
            state="disabled",
            width=140,
            height=38,
        )
        self.update_btn.pack(side="left", padx=(0, 8))

        self.delete_btn = ModernButton(
            button_row,
            text="🗑 Delete Selected",
            style="Delete.TButton",
            command=self.delete_student,
            state="disabled",
            width=140,
            height=38,
        )
        self.delete_btn.pack(side="left")

        # --- RIGHT: View switcher + single table ---
        right_col = tk.Frame(overview_frame, bg="white")
        right_col.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=(10, 11))
        right_col.rowconfigure(0, weight=1)
        right_col.columnconfigure(0, weight=1)

        # Lock screen - shown by default
        self.lock_frame = tk.Frame(right_col, bg="white")
        self.lock_frame.grid(row=0, column=0, sticky="nsew")

        lock_inner = tk.Frame(self.lock_frame, bg="white")
        lock_inner.place(relx=0.5, rely=0.4, anchor="center")
        tk.Label(lock_inner, text="🔒", bg="white", font=("Segoe UI", 40)).pack(pady=(0, 10))
        tk.Label(
            lock_inner,
            text="Student records are protected.",
            bg="white",
            fg=self.THEME["text"],
            font=("Segoe UI", 11, "bold"),
        ).pack(pady=(0, 15))
        ModernButton(
            lock_inner,
            text="🔍 View Students",
            style="Add.TButton",
            command=self._prompt_unlock,
        ).pack()

        # Data screen - hidden until unlocked
        self.data_frame = tk.Frame(right_col, bg="white")
        self.data_frame.grid(row=0, column=0, sticky="nsew")

        view_row = tk.Frame(self.data_frame, bg="white")
        view_row.pack(fill="x", padx=8, pady=(10, 8))

        tk.Label(view_row, text="Show:", bg="white", fg=self.THEME["text"], font=("Segoe UI", 10, "bold")).pack(
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

        tk.Label(view_row, text="🔍", bg="white", fg=self.THEME["text"], font=("Segoe UI", 12)).pack(
            side="left", padx=(0, 6)
        )
        self.search_var = tk.StringVar()
        search_entry = ctk.CTkEntry(
            view_row,
            height=40,
            corner_radius=10,
            border_width=1,
            border_color=self.THEME["border"],
            fg_color=self.THEME["card"],
            text_color=self.THEME["text"],
            placeholder_text="Search students...",
            placeholder_text_color=self.THEME["muted"],
            font=("Segoe UI", 11),
        )
        search_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        search_entry.bind(
            "<KeyRelease>", lambda e: self.search_var.set(search_entry.get())
        )
        self.search_var.trace_add("write", lambda *args: self.refresh_table_view())

        self.student_tree = self._build_student_tree(self.data_frame)
        self.student_tree.bind(
            "<<TreeviewSelect>>", lambda e: self.on_student_select(self.student_tree)
        )

        self.lock_frame.tkraise()

    def _build_student_tree(self, parent):
        tree_frame = ctk.CTkFrame(
            parent,
            fg_color=self.THEME["card"],
            corner_radius=12,
            border_width=1,
            border_color=self.THEME["border"],
        )
        tree_frame.pack(fill="both", expand=True, padx=8, pady=0)

        tree_scroll_y = ctk.CTkScrollbar(
            tree_frame,
            orientation="vertical",
            width=12,
            corner_radius=6,
            fg_color="#DDE6EC",
            button_color="#7893A3",
            button_hover_color=self.THEME["green"],
        )
        tree_scroll_y.pack(side="right", fill="y", padx=(2, 6), pady=6)
        tree_scroll_x = ctk.CTkScrollbar(
            tree_frame,
            orientation="horizontal",
            height=12,
            corner_radius=6,
            fg_color="#DDE6EC",
            button_color="#7893A3",
            button_hover_color=self.THEME["green"],
        )
        tree_scroll_x.pack(side="bottom", fill="x", padx=6, pady=(0, 6))
        tree = ttk.Treeview(
            tree_frame,
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set,
            selectmode="browse",
            height=18,
        )
        tree.pack(fill="both", expand=True, padx=6, pady=6)
        tree_scroll_y.configure(command=tree.yview)
        tree_scroll_x.configure(command=tree.xview)
        self.no_results_label = tk.Label(
            tree_frame,
            text="No results found.",
            bg="white",
            fg=self.THEME["muted"],
            font=("Segoe UI", 11, "italic"),
        )
        self.no_results_label.place(relx=0.5, rely=0.5, anchor="center")
        self.no_results_label.lower()

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
        student_column_widths = {
            "id": (50, 40),
            "name": (110, 90),
            "grade_level": (85, 70),
            "section": (120, 120),
            "addu_email": (220, 170),
            "committee": (130, 100),
            "role": (220, 180),
        }
        for column, (width, minwidth) in student_column_widths.items():
            tree.column(
                column,
                width=width,
                minwidth=minwidth,
                anchor=tk.CENTER,
                stretch=column != "section",
            )

        tree.heading("id", text="ID", anchor=tk.CENTER)
        tree.heading("name", text="Name", anchor=tk.CENTER)
        tree.heading("grade_level", text="Grade", anchor=tk.CENTER)
        tree.heading("section", text="Section", anchor=tk.CENTER)
        tree.heading("addu_email", text="Email", anchor=tk.CENTER)
        tree.heading("committee", text="Committee", anchor=tk.CENTER)
        tree.heading("role", text="Role", anchor=tk.CENTER)

        tree.tag_configure("evenrow", background="#FFFFFF")
        tree.tag_configure("oddrow", background="#F8FAFC")
        tree.tag_configure(
            "no_results",
            background="#FFFFFF",
            foreground=self.THEME["muted"],
            font=("Segoe UI", 11, "italic"),
        )
        return tree

    def _build_task_tree(self, parent):
        tree_frame = ctk.CTkFrame(
            parent,
            fg_color=self.THEME["card"],
            corner_radius=12,
            border_width=1,
            border_color=self.THEME["border"],
        )
        tree_frame.pack(fill="both", expand=True, padx=4, pady=4)

        tree_scroll_y = ctk.CTkScrollbar(
            tree_frame,
            orientation="vertical",
            width=12,
            corner_radius=6,
            fg_color="#E6EDF2",
            button_color="#9FB0BE",
            button_hover_color=self.THEME["green"],
        )
        tree_scroll_y.pack(side="right", fill="y", padx=(0, 6), pady=6)
        tree_scroll_x = ctk.CTkScrollbar(
            tree_frame,
            orientation="horizontal",
            height=12,
            corner_radius=6,
            fg_color="#E6EDF2",
            button_color="#9FB0BE",
            button_hover_color=self.THEME["green"],
        )
        tree_scroll_x.pack(side="bottom", fill="x", padx=6, pady=(0, 6))

        tree = ttk.Treeview(
            tree_frame,
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set,
            selectmode="browse",
            height=18,
        )
        tree.pack(fill="both", expand=True, padx=6, pady=6)
        tree_scroll_y.configure(command=tree.yview)
        tree_scroll_x.configure(command=tree.xview)
        self.task_no_results_label = tk.Label(
            tree_frame,
            text="No results found.",
            bg="white",
            fg=self.THEME["muted"],
            font=("Segoe UI", 11, "italic"),
        )
        self.task_no_results_label.place(relx=0.5, rely=0.5, anchor="center")
        self.task_no_results_label.lower()
        tree["columns"] = ("id", "task_name", "committee", "due_date")
        tree.column("#0", width=0, stretch=tk.NO)
        tree.column("id", width=50, anchor=tk.CENTER, stretch=False)
        tree.column("task_name", width=220, anchor=tk.CENTER, stretch=False)
        tree.column("committee", width=220, anchor=tk.CENTER, stretch=False)
        tree.column("due_date", width=140, anchor=tk.CENTER, stretch=True)

        tree.heading("id", text="ID", anchor=tk.CENTER)
        tree.heading("task_name", text="Task Name", anchor=tk.CENTER)
        tree.heading("committee", text="Committee", anchor=tk.CENTER)
        tree.heading("due_date", text="Due Date", anchor=tk.CENTER)

        tree.tag_configure("evenrow", background="#FFFFFF")
        tree.tag_configure("oddrow", background="#F8FAFC")
        return tree

    def create_add_student_tab(self, parent):
        students_frame = ctk.CTkFrame(parent, fg_color=self.THEME["card"], corner_radius=0)
        students_frame.grid(row=0, column=0, sticky="nsew")
        self.pages["add_student"] = students_frame

        container = tk.Frame(students_frame, bg="white")
        container.pack(fill="both", expand=True, padx=15, pady=15)
        container.columnconfigure(0, weight=1, minsize=360)
        container.columnconfigure(1, weight=1, minsize=360)
        container.columnconfigure(2, weight=1, minsize=360)
        container.rowconfigure(0, weight=1)

        # --- Add Student section (left) ---
        add_student_frame = tk.LabelFrame(
            container,
            text="Add Student",
            bg="white",
            fg=self.THEME["navy"],
            font=("Segoe UI", 11, "bold"),
            bd=1,
            relief="solid",
        )
        add_student_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=5)

        tk.Label(
            add_student_frame,
            text="Enter the student's details and assign a role.",
            bg="white",
            fg=self.THEME["muted"],
            font=("Segoe UI", 9),
            anchor="w",
        ).pack(fill="x", padx=10, pady=(8, 0))

        entry_frame = tk.Frame(add_student_frame, bg="white")
        entry_frame.pack(fill="x", padx=10, pady=(10, 5))
        # Grid-aligned: same 2-col grid as Update Student — fixes uneven padx/sticky
        entry_frame.columnconfigure(0, weight=0, minsize=110)
        entry_frame.columnconfigure(1, weight=1)
        _FW = 22
        _PY = 6

        # --- Form fields ---
        ttk.Label(entry_frame, text="Student Name:", style="Form.TLabel").grid(
            row=0, column=0, padx=10, pady=_PY, sticky="w"
        )
        self.name_entry = ctk.CTkEntry(
            entry_frame,
            width=220,
            height=38,
            corner_radius=10,
            border_color="#B8CBD8",
            placeholder_text="e.g. Juan Dela Cruz",
        )
        self.name_entry.grid(row=0, column=1, padx=10, pady=_PY, sticky="ew")

        ttk.Label(entry_frame, text="Grade Level:", style="Form.TLabel").grid(
            row=1, column=0, padx=10, pady=_PY, sticky="w"
        )
        self.grade_entry = ModernDropdown(
            entry_frame, width=_FW, state="readonly", values=GRADE_LEVELS
        )
        self.grade_entry.grid(row=1, column=1, padx=10, pady=_PY, sticky="ew")
        self.grade_combo = self.grade_entry

        ttk.Label(entry_frame, text="Section:", style="Form.TLabel").grid(
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

        ttk.Label(entry_frame, text="Addu Email:", style="Form.TLabel").grid(
            row=3, column=0, padx=10, pady=_PY, sticky="w"
        )
        email_row = tk.Frame(entry_frame, bg="white")
        email_row.grid(row=3, column=1, padx=10, pady=_PY, sticky="ew")
        self.email_entry = ctk.CTkEntry(
            email_row,
            width=150,
            height=38,
            corner_radius=10,
            border_color="#B8CBD8",
            placeholder_text="username",
        )
        self.email_entry.pack(side="left")
        ttk.Label(email_row, text="@addu.edu.ph", style="Form.TLabel").pack(side="left")

        ttk.Label(entry_frame, text="Committee:", style="Form.TLabel").grid(
            row=4, column=0, padx=10, pady=_PY, sticky="w"
        )
        self.committee_combo = ModernDropdown(entry_frame, width=_FW, state="readonly")
        self.committee_combo["values"] = self.load_committees()
        self.committee_combo.grid(row=4, column=1, padx=10, pady=_PY, sticky="ew")

        ttk.Label(entry_frame, text="Role:", style="Form.TLabel").grid(
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

        button_frame = tk.Frame(add_student_frame, bg="white")
        button_frame.pack(fill="x", padx=10, pady=(5, 10))

        self.committee_combo.bind("<<ComboboxSelected>>", self._clear_combo_highlight)
        self.role_combo.bind("<<ComboboxSelected>>", self._clear_combo_highlight)

        ModernButton(
            button_frame,
            text="+ Add Student",
            style="Add.TButton",
            command=lambda: self.add_student(button_requested=True),
        ).pack(side="left", padx=(126, 0), ipadx=0)

        # --- Assign Task section (center) ---
        assign_tasks_frame = tk.LabelFrame(
            container,
            text="Assign Task",
            bg="white",
            fg=self.THEME["navy"],
            font=("Segoe UI", 11, "bold"),
            bd=1,
            relief="solid",
        )
        assign_tasks_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        assign_task_description = tk.Frame(assign_tasks_frame, bg="white")
        assign_task_description.pack(fill="x", padx=10, pady=(8, 0))
        tk.Label(
            assign_task_description,
            text="Create a task and set its committee and due date.",
            bg="white",
            fg=self.THEME["muted"],
            font=("Segoe UI", 9),
            anchor="w",
        ).pack(fill="x", padx=10, pady=(8, 0))

        assign_task_content = tk.Frame(assign_tasks_frame, bg="white")
        assign_task_content.pack(fill="both", expand=True, padx=10, pady=(4, 10))

        # Single grid block for all 10 rows — labels col0, fields col1, uniform
        assign_task_content.columnconfigure(0, weight=0, minsize=110)
        assign_task_content.columnconfigure(1, weight=1)
        _AFW = 22  # same field width as left form for visual alignment
        tk.Label(assign_task_content, text="Task Name:", bg="white", fg=self.THEME["text"], font=("Segoe UI", 10, "bold")).grid(
            row=0, column=0, padx=10, pady=6, sticky="w"
        )
        self.task_name_entry = ctk.CTkEntry(
            assign_task_content,
            width=220,
            height=38,
            corner_radius=10,
            border_color="#B8CBD8",
            placeholder_text="e.g. Prepare event proposal",
        )
        self.task_name_entry.grid(row=0, column=1, padx=10, pady=6, sticky="ew")

        tk.Label(assign_task_content, text="Committee:", bg="white", fg=self.THEME["text"], font=("Segoe UI", 10, "bold")).grid(
            row=1, column=0, padx=10, pady=6, sticky="w"
        )
        self.task_committee_combo = ModernDropdown(
            assign_task_content, width=_AFW, state="readonly"
        )
        self.task_committee_combo.grid(row=1, column=1, padx=10, pady=6, sticky="ew")

        tk.Label(assign_task_content, text="Due Date (YYYY-MM-DD):", bg="white", fg=self.THEME["text"], font=("Segoe UI", 10, "bold")).grid(
            row=2, column=0, padx=10, pady=6, sticky="w"
        )
        date_row = tk.Frame(assign_task_content, bg="white")
        date_row.grid(row=2, column=1, padx=10, pady=6, sticky="ew")
        self.task_due_date_entry = ctk.CTkEntry(
            date_row,
            width=140,
            height=38,
            corner_radius=10,
            border_color="#B8CBD8",
            placeholder_text="YYYY-MM-DD",
        )
        self.task_due_date_entry.pack(side="left")
        self._calendar_btn(date_row, self.task_due_date_entry).pack(
            side="left", padx=(4, 0)
        )

        add_task_button = ModernButton(
            assign_task_content,
            text="＋ Add Task",
            style="Add.TButton",
            command=self.add_task,
            width=140,
            height=38,
        )
        add_task_button.grid(
            row=3, column=1, padx=10, pady=(12, 8), sticky="w"
        )

        self.task_committee_combo.bind(
            "<<ComboboxSelected>>", self._clear_combo_highlight
        )
        self._load_committees_for_task()

        # --- Assign Task to Member section (right) ---
        assign_member_frame = tk.LabelFrame(
            container,
            text="Assign Task to Member",
            bg="white",
            fg=self.THEME["navy"],
            font=("Segoe UI", 11, "bold"),
            bd=1,
            relief="solid",
        )
        assign_member_frame.grid(row=0, column=2, sticky="nsew", padx=(5, 0), pady=5)
        assign_member_frame.columnconfigure(0, weight=0, minsize=120)
        assign_member_frame.columnconfigure(1, weight=1)

        tk.Label(
            assign_member_frame, text="Choose the task, member, date, and status.",
            bg="white", font=("Segoe UI", 9), fg=self.THEME["muted"]
        ).grid(row=0, column=0, columnspan=2, padx=20, pady=(8, 6), sticky="w")

        tk.Label(assign_member_frame, text="Task:", bg="white", fg=self.THEME["text"], font=("Segoe UI", 10, "bold")).grid(
            row=1, column=0, padx=(20, 10), pady=6, sticky="w"
        )
        self.assign_task_combo = ModernDropdown(
            assign_member_frame, width=_AFW, state="readonly"
        )
        self.assign_task_combo.grid(row=1, column=1, padx=10, pady=6, sticky="ew")

        tk.Label(assign_member_frame, text="Member:", bg="white", fg=self.THEME["text"], font=("Segoe UI", 10, "bold")).grid(
            row=2, column=0, padx=(20, 10), pady=6, sticky="w"
        )
        self.assign_member_combo = ModernDropdown(
            assign_member_frame, width=_AFW, state="readonly"
        )
        self.assign_member_combo.grid(row=2, column=1, padx=10, pady=6, sticky="ew")

        tk.Label(assign_member_frame, text="Date Assigned (YYYY-MM-DD):", bg="white", fg=self.THEME["text"], font=("Segoe UI", 10, "bold")).grid(
            row=3, column=0, padx=(20, 10), pady=6, sticky="w"
        )
        date_row = tk.Frame(assign_member_frame, bg="white")
        date_row.grid(row=3, column=1, padx=10, pady=6, sticky="ew")
        self.assign_date_entry = ctk.CTkEntry(
            date_row,
            width=140,
            height=38,
            corner_radius=10,
            border_color="#B8CBD8",
            placeholder_text="YYYY-MM-DD",
        )
        self.assign_date_entry.pack(side="left")
        self._calendar_btn(date_row, self.assign_date_entry).pack(
            side="left", padx=(4, 0)
        )

        tk.Label(assign_member_frame, text="Status:", bg="white", fg=self.THEME["text"], font=("Segoe UI", 10, "bold")).grid(
            row=4, column=0, padx=(20, 10), pady=6, sticky="w"
        )
        self.assign_status_combo = ModernDropdown(
            assign_member_frame, width=_AFW, state="readonly"
        )
        self.assign_status_combo.grid(row=4, column=1, padx=10, pady=6, sticky="ew")
        self.assign_status_combo["values"] = [
            "Pending",
            "In Progress",
            "Completed",
            "Cancelled",
        ]
        if self.assign_status_combo["values"]:
            self.assign_status_combo.current(0)

        assign_task_button = ModernButton(
            assign_member_frame,
            text="✓ Assign Task",
            style="Add.TButton",
            command=self.assign_task,
            width=140,
            height=38,
        )
        assign_task_button.grid(row=5, column=1, padx=10, pady=(14, 10), sticky="w")

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
        settings_frame = ctk.CTkFrame(parent, fg_color=self.THEME["background"], corner_radius=0)
        settings_frame.grid(row=0, column=0, sticky="nsew")
        # let lock/data layers fill settings_frame
        settings_frame.rowconfigure(0, weight=1)
        settings_frame.columnconfigure(0, weight=1)
        self.pages["task/assignment"] = settings_frame

        # --- lock cover (same passkey as students) ---
        self.task_lock_frame = tk.Frame(settings_frame, bg="white")
        self.task_lock_frame.grid(row=0, column=0, sticky="nsew")

        lock_inner = tk.Frame(self.task_lock_frame, bg="white")
        lock_inner.place(relx=0.5, rely=0.4, anchor="center")
        tk.Label(lock_inner, text="🔒", bg="white", font=("Segoe UI", 40)).pack(pady=(0, 10))
        tk.Label(
            lock_inner,
            text="Task records are protected.",
            bg="white",
            fg=self.THEME["text"],
            font=("Segoe UI", 11, "bold"),
        ).pack(pady=(0, 15))
        ModernButton(
            lock_inner,
            text="🔍 View Tasks",
            style="Add.TButton",
            command=self._prompt_unlock_tasks,
        ).pack()

        self.task_data_frame = tk.Frame(settings_frame, bg="white")
        self.task_data_frame.grid(row=0, column=0, sticky="nsew")

        # Custom white tab bar avoids the native notebook trough background.
        tab_shell = tk.Frame(self.task_data_frame, bg="white")
        tab_shell.pack(fill="both", expand=True, padx=15, pady=15)
        tab_bar = tk.Frame(tab_shell, bg="white")
        tab_bar.pack(fill="x")
        tab_pages = tk.Frame(tab_shell, bg="white")
        tab_pages.pack(fill="both", expand=True)

        tasks_page = tk.Frame(tab_pages, bg="white")
        assignments_page = tk.Frame(tab_pages, bg="white")
        for page in (tasks_page, assignments_page):
            page.grid(row=0, column=0, sticky="nsew")
        tab_pages.rowconfigure(0, weight=1)
        tab_pages.columnconfigure(0, weight=1)

        tab_buttons = {}

        def show_task_page(page_name):
            page = tasks_page if page_name == "Tasks" else assignments_page
            page.tkraise()
            for name, button in tab_buttons.items():
                button.configure(
                    fg_color=self.THEME["green"] if name == page_name else "white",
                    text_color="white" if name == page_name else self.THEME["navy"],
                )

        for name in ("Tasks", "Assignments"):
            tab_buttons[name] = ctk.CTkButton(
                tab_bar,
                text=name,
                command=lambda selected=name: show_task_page(selected),
                fg_color="white",
                hover_color="#87AECE",
                text_color=self.THEME["navy"],
                border_width=1,
                border_color="#1D2A62",
                font=("Segoe UI", 12, "bold"),
                corner_radius=6,
                width=132,
                height=40,
                cursor="hand2",
            )
            tab_buttons[name].pack(side="left", padx=(0, 4), pady=3)

        show_task_page("Tasks")

        # --- TASKS SUBTAB ---
        tasks_page.columnconfigure(0, weight=1)
        tasks_page.rowconfigure(1, weight=1)

        task_top_row = tk.Frame(tasks_page, bg="white")
        task_top_row.grid(row=0, column=0, sticky="ew", padx=8, pady=8)
        task_top_row.columnconfigure(0, weight=1)

        self.task_search_var = tk.StringVar()
        task_search_wrap = tk.Frame(task_top_row, bg="white")
        task_search_wrap.grid(row=0, column=0, sticky="ew", padx=(0, 12))
        tk.Label(
            task_search_wrap,
            text="🔍",
            bg="white",
            fg=self.THEME["text"],
            font=("Segoe UI", 12),
        ).pack(side="left", padx=(0, 6))
        task_search_entry = ctk.CTkEntry(
            task_search_wrap,
            height=40,
            corner_radius=10,
            border_width=1,
            border_color=self.THEME["border"],
            fg_color=self.THEME["card"],
            text_color=self.THEME["text"],
            placeholder_text="Search tasks...",
            placeholder_text_color=self.THEME["muted"],
            font=("Segoe UI", 11),
        )
        task_search_entry.pack(side="left", fill="x", expand=True)
        task_search_entry.bind(
            "<KeyRelease>", lambda e: self.task_search_var.set(task_search_entry.get())
        )
        self.task_search_var.trace_add("write", lambda *args: self.refresh_task_table())

        task_filter_frame = tk.Frame(task_top_row, bg="white")
        task_filter_frame.grid(row=0, column=1, sticky="w", padx=(5, 0))
        tk.Label(task_filter_frame, text="Show Tasks:", bg="white", fg=self.THEME["text"], font=("Segoe UI", 10, "bold")).pack(
            side="left", padx=(0, 5)
        )
        self.task_committee_filter = ModernDropdown(
            task_filter_frame, width=18, state="readonly"
        )
        self.task_committee_filter["values"] = ["All Committees"]
        self.task_committee_filter.set("All Committees")
        self.task_committee_filter.pack(side="left")
        self.task_committee_filter.bind(
            "<<ComboboxSelected>>",
            lambda e: (self.refresh_task_table(), self._clear_combo_highlight(e)),
        )

        task_body = tk.Frame(tasks_page, bg="white")
        task_body.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        task_body.columnconfigure(0, weight=3, minsize=520)
        task_body.columnconfigure(1, weight=2, minsize=340)
        task_body.rowconfigure(0, weight=1)

        task_tree_frame = tk.LabelFrame(
            task_body,
            text="Task List",
            bg="white",
            fg=self.THEME["navy"],
            font=("Segoe UI", 11, "bold"),
            bd=1,
            relief="solid",
        )
        task_tree_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.tasks_tree = self._build_task_tree(task_tree_frame)
        self.tasks_tree.bind(
            "<<TreeviewSelect>>", lambda e: self._on_update_task_selected()
        )

        task_form_frame = tk.LabelFrame(
            task_body,
            text="Update Task",
            bg="white",
            fg=self.THEME["navy"],
            font=("Segoe UI", 11, "bold"),
            bd=1,
            relief="solid",
        )
        task_form_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0), ipadx=8)
        self._build_update_tasks(task_form_frame)
        task_filter_frame.grid(sticky="ew")

        def align_task_toolbar(event=None):
            task_top_row.columnconfigure(0, weight=0)
            task_top_row.columnconfigure(1, weight=1)
            task_top_row.columnconfigure(
                0, minsize=task_tree_frame.winfo_width() + 5
            )

        task_body.bind("<Configure>", align_task_toolbar, add="+")
        task_tree_frame.bind("<Configure>", align_task_toolbar, add="+")
        task_form_frame.bind("<Configure>", align_task_toolbar, add="+")
        self.root.after_idle(align_task_toolbar)

        # --- ASSIGNMENTS SUBTAB ---
        assignments_page.columnconfigure(0, weight=1)
        assignments_page.rowconfigure(1, weight=1)

        assign_top_row = tk.Frame(assignments_page, bg="white")
        assign_top_row.grid(row=0, column=0, sticky="ew", padx=8, pady=8)
        assign_top_row.columnconfigure(0, weight=1)

        self.assignment_search_var = tk.StringVar()
        assignment_search_wrap = tk.Frame(assign_top_row, bg="white")
        assignment_search_wrap.grid(row=0, column=0, sticky="ew", padx=(0, 12))
        tk.Label(
            assignment_search_wrap,
            text="🔍",
            bg="white",
            fg=self.THEME["text"],
            font=("Segoe UI", 12),
        ).pack(side="left", padx=(0, 6))
        assignment_search_entry = ctk.CTkEntry(
            assignment_search_wrap,
            height=40,
            corner_radius=10,
            border_width=1,
            border_color=self.THEME["border"],
            fg_color=self.THEME["card"],
            text_color=self.THEME["text"],
            placeholder_text="Search assignments...",
            placeholder_text_color=self.THEME["muted"],
            font=("Segoe UI", 11),
        )
        assignment_search_entry.pack(side="left", fill="x", expand=True)
        assignment_search_entry.bind(
            "<KeyRelease>",
            lambda e: self.assignment_search_var.set(assignment_search_entry.get()),
        )
        self.assignment_search_var.trace_add(
            "write", lambda *args: self.refresh_assignment_table()
        )

        assignment_filter_frame = tk.Frame(assign_top_row, bg="white")
        assignment_filter_frame.grid(row=0, column=1, sticky="w", padx=(5, 0))
        tk.Label(
            assignment_filter_frame,
            text="Show Tasks:",
            bg="white",
            fg=self.THEME["text"],
            font=("Segoe UI", 10, "bold"),
        ).pack(side="left", padx=(0, 5))
        self.assignment_task_filter = ModernDropdown(
            assignment_filter_frame, width=18, state="readonly"
        )
        self.assignment_task_filter["values"] = ["All Tasks"]
        self.assignment_task_filter.set("All Tasks")
        self.assignment_task_filter.pack(side="left")
        self.assignment_task_filter.bind(
            "<<ComboboxSelected>>",
            lambda e: (self.refresh_assignment_table(), self._clear_combo_highlight(e)),
        )

        assign_body = tk.Frame(assignments_page, bg="white")
        assign_body.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        assign_body.columnconfigure(0, weight=3, minsize=620)
        assign_body.columnconfigure(1, weight=2, minsize=340)
        assign_body.rowconfigure(0, weight=1)

        assign_tree_frame = tk.LabelFrame(
            assign_body,
            text="Assignment List",
            bg="white",
            fg=self.THEME["navy"],
            font=("Segoe UI", 11, "bold"),
            bd=1,
            relief="solid",
        )
        assign_tree_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.assignments_tree = self._build_assignment_tree(assign_tree_frame)
        self.assignments_tree.bind(
            "<<TreeviewSelect>>", lambda e: self._on_update_assignment_selected()
        )

        assign_form_frame = tk.LabelFrame(
            assign_body,
            text="Update Assignment",
            bg="white",
            fg=self.THEME["navy"],
            font=("Segoe UI", 11, "bold"),
            bd=1,
            relief="solid",
        )
        assign_form_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0), ipadx=8)
        self._build_update_assignments(assign_form_frame)

        def align_assignment_toolbar(event=None):
            assign_top_row.columnconfigure(0, weight=0)
            assign_top_row.columnconfigure(1, weight=1)
            assign_top_row.columnconfigure(
                0, minsize=assign_tree_frame.winfo_width() + 5
            )

        assign_body.bind("<Configure>", align_assignment_toolbar, add="+")
        assign_tree_frame.bind("<Configure>", align_assignment_toolbar, add="+")
        assign_form_frame.bind("<Configure>", align_assignment_toolbar, add="+")
        self.root.after_idle(align_assignment_toolbar)

        self.task_lock_frame.tkraise()

        self.load_tasks()
        self.load_assignments()

    def _build_update_tasks(self, parent):
        parent.columnconfigure(0, weight=0, minsize=110)
        parent.columnconfigure(1, weight=1)
        field_width = 20
        row_pady = 6

        tk.Label(parent, text="Task Name:", bg="white", fg=self.THEME["text"], font=("Segoe UI", 10, "bold")).grid(
            row=0, column=0, padx=10, pady=row_pady, sticky="w"
        )
        self.update_task_name_entry = ctk.CTkEntry(
            parent,
            width=200,
            height=38,
            corner_radius=10,
            border_color="#B8CBD8",
            placeholder_text="e.g. Prepare event proposal",
        )
        self.update_task_name_entry.grid(
            row=0, column=1, padx=10, pady=row_pady, sticky="ew"
        )

        tk.Label(parent, text="Committee:", bg="white", fg=self.THEME["text"], font=("Segoe UI", 10, "bold")).grid(
            row=1, column=0, padx=10, pady=row_pady, sticky="w"
        )
        self.update_task_committee_combo = ModernDropdown(
            parent, width=field_width, state="readonly"
        )
        self.update_task_committee_combo["values"] = [
            name for (_id, name) in self.committees_list
        ]
        self.update_task_committee_combo.grid(
            row=1, column=1, padx=10, pady=row_pady, sticky="ew"
        )

        tk.Label(parent, text="Due Date:", bg="white", fg=self.THEME["text"], font=("Segoe UI", 10, "bold")).grid(
            row=2, column=0, padx=10, pady=row_pady, sticky="w"
        )
        date_row = tk.Frame(parent, bg="white")
        date_row.grid(row=2, column=1, padx=10, pady=row_pady, sticky="ew")
        self.update_task_due_date_entry = ctk.CTkEntry(
            date_row,
            width=140,
            height=38,
            corner_radius=10,
            border_color="#B8CBD8",
            placeholder_text="YYYY-MM-DD",
        )
        self.update_task_due_date_entry.pack(side="left")
        self._calendar_btn(date_row, self.update_task_due_date_entry).pack(
            side="left", padx=(4, 0)
        )

        self.task_update_btn = ModernButton(
            parent,
            text="🔼 Update Task",
            style="Update.TButton",
            command=self.update_task,
            state="disabled",
            width=140,
            height=38,
        )
        self.task_update_btn.grid(row=3, column=1, padx=10, pady=(14, 8), sticky="w")

        self.task_delete_btn = ModernButton(
            parent,
            text="🗑 Delete Task",
            style="Delete.TButton",
            command=self.delete_task,
            state="disabled",
            width=140,
            height=38,
        )
        self.task_delete_btn.grid(row=4, column=1, padx=10, pady=(0, 16), sticky="w")

    def _build_update_assignments(self, parent):
        parent.columnconfigure(0, weight=0, minsize=110)
        parent.columnconfigure(1, weight=1)
        field_width = 20
        row_pady = 6

        tk.Label(parent, text="Task:", bg="white", fg=self.THEME["text"], font=("Segoe UI", 10, "bold")).grid(
            row=0, column=0, padx=10, pady=row_pady, sticky="w"
        )
        self.update_assignment_task_entry = ModernDropdown(
            parent, width=field_width, state="readonly"
        )
        self.update_assignment_task_entry["values"] = [
            name for (_id, name) in self.tasks_list
        ]
        self.update_assignment_task_entry.grid(
            row=0, column=1, padx=10, pady=row_pady, sticky="ew"
        )

        tk.Label(parent, text="Member:", bg="white", fg=self.THEME["text"], font=("Segoe UI", 10, "bold")).grid(
            row=1, column=0, padx=10, pady=row_pady, sticky="w"
        )
        self.update_assignment_member_combo = ModernDropdown(
            parent, width=field_width, state="readonly"
        )
        self.update_assignment_member_combo["values"] = [
            name for (_id, name) in self.members_list
        ]
        self.update_assignment_member_combo.grid(
            row=1, column=1, padx=10, pady=row_pady, sticky="ew"
        )

        tk.Label(parent, text="Date Assigned:", bg="white", fg=self.THEME["text"], font=("Segoe UI", 10, "bold")).grid(
            row=2, column=0, padx=10, pady=row_pady, sticky="w"
        )
        date_row = tk.Frame(parent, bg="white")
        date_row.grid(row=2, column=1, padx=10, pady=row_pady, sticky="ew")
        self.update_assignment_date_entry = ctk.CTkEntry(
            date_row,
            width=140,
            height=38,
            corner_radius=10,
            border_color="#B8CBD8",
            placeholder_text="YYYY-MM-DD",
        )
        self.update_assignment_date_entry.pack(side="left")
        self._calendar_btn(date_row, self.update_assignment_date_entry).pack(
            side="left", padx=(4, 0)
        )

        tk.Label(parent, text="Status:", bg="white", fg=self.THEME["text"], font=("Segoe UI", 10, "bold")).grid(
            row=3, column=0, padx=10, pady=row_pady, sticky="w"
        )
        self.update_assignment_status_combo = ModernDropdown(
            parent,
            width=field_width,
            state="readonly",
            values=["Pending", "In Progress", "Completed", "Cancelled"],
        )
        self.update_assignment_status_combo.grid(
            row=3, column=1, padx=10, pady=row_pady, sticky="ew"
        )

        self.assignment_update_btn = ModernButton(
            parent,
            text="🔼 Update Assignment",
            style="Update.TButton",
            command=self.update_assignment,
            state="disabled",
            width=140,
            height=38,
        )
        self.assignment_update_btn.grid(row=4, column=1, padx=10, pady=(14, 8), sticky="w")

        self.assignment_delete_btn = ModernButton(
            parent,
            text="🗑 Delete Assignment",
            style="Delete.TButton",
            command=self.delete_assignment,
            state="disabled",
            width=140,
            height=38,
        )
        self.assignment_delete_btn.grid(row=5, column=1, padx=10, pady=(0, 16), sticky="w")

    def _on_update_task_selected(self):
        selected = self.tasks_tree.focus()
        if not selected:
            return

        values = self.tasks_tree.item(selected, "values")
        if not values:
            return

        self.update_task_name_entry.delete(0, tk.END)
        self.update_task_name_entry.insert(0, values[1] if values[1] else "")
        self.update_task_committee_combo.set(values[2] if values[2] else "")
        self.update_task_due_date_entry.delete(0, tk.END)
        self.update_task_due_date_entry.insert(0, values[3] if values[3] else "")
        self._selected_task_id = values[0]
        self._selected_task_original = (
            values[1] or "",
            values[2] or "",
            values[3] or "",
        )
        self.task_update_btn.config(state="normal")
        self.task_delete_btn.config(state="normal")

    def _on_update_assignment_selected(self):
        selected = self.assignments_tree.focus()
        if not selected:
            return

        values = self.assignments_tree.item(selected, "values")
        if not values:
            return

        self.update_assignment_task_entry.set(values[1] if values[1] else "")
        self.update_assignment_member_combo.set(values[2] if values[2] else "")
        self.update_assignment_date_entry.delete(0, tk.END)
        self.update_assignment_date_entry.insert(0, values[3] if values[3] else "")
        self.update_assignment_status_combo.set(values[4] if values[4] else "")
        self._selected_assignment_id = values[0]
        self._selected_assignment_original = (
            values[1] or "",
            values[2] or "",
            values[3] or "",
            values[4] or "",
        )
        self.assignment_update_btn.config(state="normal")
        self.assignment_delete_btn.config(state="normal")

    def _build_task_update_form(self, parent):
        form_frame = ttk.Frame(parent)
        form_frame.pack(side="right", fill="y", padx=(8, 0), pady=8)
        form_frame.columnconfigure(1, weight=1)
        form_frame.columnconfigure(3, weight=1)

        ttk.Label(form_frame, text="Task Name:").grid(
            row=0, column=0, padx=(0, 5), pady=3, sticky="w"
        )
        self.task_update_name_entry = ctk.CTkEntry(form_frame, width=200, height=38, corner_radius=10, border_color="#B8CBD8")
        self.task_update_name_entry.grid(
            row=0, column=1, padx=(0, 10), pady=3, sticky="ew"
        )

        ttk.Label(form_frame, text="Committee:").grid(
            row=1, column=0, padx=(0, 5), pady=3, sticky="w"
        )
        self.task_update_committee_combo = ModernDropdown(
            form_frame, width=18, state="readonly"
        )
        self.task_update_committee_combo["values"] = [
            name for (_id, name) in self.committees_list
        ]
        self.task_update_committee_combo.grid(
            row=1, column=1, padx=(0, 10), pady=3, sticky="ew"
        )

        ttk.Label(form_frame, text="Due Date:").grid(
            row=2, column=0, padx=(0, 5), pady=3, sticky="w"
        )
        self.task_update_due_date_entry = ctk.CTkEntry(form_frame, width=140, height=38, corner_radius=10, border_color="#B8CBD8")
        self.task_update_due_date_entry.grid(
            row=2, column=1, padx=(0, 10), pady=3, sticky="ew"
        )

        search_wrap = tk.Frame(form_frame, bg="#7ED985", bd=0)
        search_wrap.grid(
            row=3, column=0, columnspan=2, padx=(0, 0), pady=3, sticky="ew"
        )
        search_inner = tk.Frame(search_wrap, bg="white")
        search_inner.pack(fill="both", expand=True, padx=1, pady=1)
        tk.Label(
            search_inner, text="🔍", bg="white", fg="#6B6B6B", font=("Segoe UI", 10)
        ).pack(side="left", padx=(8, 4), pady=3)
        self.task_search_var = tk.StringVar()
        task_search_entry = ctk.CTkEntry(
            search_inner,
            placeholder_text="Search tasks...",
            placeholder_text_color="#6B6B6B",
            height=32,
            fg_color="white",
            text_color="#0F1A0F",
            border_width=0,
            font=("Segoe UI", 10),
        )
        task_search_entry.pack(side="left", fill="x", expand=True, ipady=3, padx=(0, 8))
        task_search_entry.bind(
            "<KeyRelease>", lambda e: self.task_search_var.set(task_search_entry.get())
        )
        self.task_search_var.trace_add("write", lambda *args: self.refresh_task_table())

    def _build_assignment_update_form(self, parent):
        form_frame = ttk.Frame(parent)
        form_frame.pack(side="right", fill="y", padx=(8, 0), pady=8)
        form_frame.columnconfigure(1, weight=1)
        form_frame.columnconfigure(3, weight=1)

        ttk.Label(form_frame, text="Task:").grid(
            row=0, column=0, padx=(0, 5), pady=3, sticky="w"
        )
        self.assignment_update_task_combo = ModernDropdown(
            form_frame, width=18, state="readonly"
        )
        self.assignment_update_task_combo["values"] = [
            name for (_id, name) in self.tasks_list
        ]
        self.assignment_update_task_combo.grid(
            row=0, column=1, padx=(0, 10), pady=3, sticky="ew"
        )

        ttk.Label(form_frame, text="Member:").grid(
            row=1, column=0, padx=(0, 5), pady=3, sticky="w"
        )
        self.assignment_update_member_combo = ModernDropdown(
            form_frame, width=18, state="readonly"
        )
        self.assignment_update_member_combo["values"] = [
            name for (_id, name) in self.members_list
        ]
        self.assignment_update_member_combo.grid(
            row=1, column=1, padx=(0, 10), pady=3, sticky="ew"
        )

        ttk.Label(form_frame, text="Date:").grid(
            row=2, column=0, padx=(0, 5), pady=3, sticky="w"
        )
        self.assignment_update_date_entry = ctk.CTkEntry(form_frame, width=140, height=38, corner_radius=10, border_color="#B8CBD8")
        self.assignment_update_date_entry.grid(
            row=2, column=1, padx=(0, 10), pady=3, sticky="ew"
        )

        ttk.Label(form_frame, text="Status:").grid(
            row=3, column=0, padx=(0, 5), pady=3, sticky="w"
        )
        self.assignment_update_status_combo = ModernDropdown(
            form_frame,
            width=14,
            state="readonly",
            values=["Pending", "In Progress", "Completed", "Cancelled"],
        )
        self.assignment_update_status_combo.grid(
            row=3, column=1, padx=(0, 10), pady=3, sticky="ew"
        )

        search_wrap = tk.Frame(form_frame, bg="#7ED985", bd=0)
        search_wrap.grid(row=4, column=0, columnspan=2, pady=3, sticky="ew")
        search_inner = tk.Frame(search_wrap, bg="white")
        search_inner.pack(fill="both", expand=True, padx=1, pady=1)
        tk.Label(
            search_inner, text="🔍", bg="white", fg="#6B6B6B", font=("Segoe UI", 10)
        ).pack(side="left", padx=(8, 4), pady=3)
        self.assignment_search_var = tk.StringVar()
        assignment_search_entry = ctk.CTkEntry(
            search_inner,
            placeholder_text="Search assignments...",
            placeholder_text_color="#6B6B6B",
            height=32,
            fg_color="white",
            text_color="#0F1A0F",
            border_width=0,
            font=("Segoe UI", 10),
        )
        assignment_search_entry.pack(
            side="left", fill="x", expand=True, ipady=3, padx=(0, 8)
        )
        assignment_search_entry.bind(
            "<KeyRelease>",
            lambda e: self.assignment_search_var.set(assignment_search_entry.get()),
        )
        self.assignment_search_var.trace_add(
            "write", lambda *args: self.refresh_assignment_table()
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

    def _build_assignment_tree(self, parent):
        tree_frame = ctk.CTkFrame(
            parent,
            fg_color=self.THEME["card"],
            corner_radius=12,
            border_width=1,
            border_color=self.THEME["border"],
        )
        tree_frame.pack(fill="both", expand=True, padx=4, pady=4)

        tree_scroll_y = ctk.CTkScrollbar(
            tree_frame,
            orientation="vertical",
            width=12,
            corner_radius=6,
            fg_color="#E6EDF2",
            button_color="#9FB0BE",
            button_hover_color=self.THEME["green"],
        )
        tree_scroll_y.pack(side="right", fill="y", padx=(0, 6), pady=6)
        tree_scroll_x = ctk.CTkScrollbar(
            tree_frame,
            orientation="horizontal",
            height=12,
            corner_radius=6,
            fg_color="#E6EDF2",
            button_color="#9FB0BE",
            button_hover_color=self.THEME["green"],
        )
        tree_scroll_x.pack(side="bottom", fill="x", padx=6, pady=(0, 6))

        tree = ttk.Treeview(
            tree_frame,
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set,
            selectmode="browse",
            height=18,
        )
        tree.pack(fill="both", expand=True, padx=6, pady=6)
        tree_scroll_y.configure(command=tree.yview)
        tree_scroll_x.configure(command=tree.xview)
        self.assignment_no_results_label = tk.Label(
            tree_frame,
            text="No results found.",
            bg="white",
            fg=self.THEME["muted"],
            font=("Segoe UI", 11, "italic"),
        )
        self.assignment_no_results_label.place(relx=0.5, rely=0.5, anchor="center")
        self.assignment_no_results_label.lower()

        tree["columns"] = (
            "id",
            "task_name",
            "assigned_to",
            "date_assigned",
            "status",
        )
        tree.column("#0", width=0, stretch=tk.NO)
        assignment_column_widths = {
            "id": (45, 45),
            "task_name": (175, 150),
            "assigned_to": (150, 130),
            "date_assigned": (120, 115),
            "status": (125, 110),
        }
        for column, (width, minwidth) in assignment_column_widths.items():
            tree.column(
                column,
                width=width,
                minwidth=minwidth,
                anchor=tk.CENTER,
                stretch=column == "status",
            )

        tree.heading("id", text="ID", anchor=tk.CENTER)
        tree.heading("task_name", text="Task Name", anchor=tk.CENTER)
        tree.heading("assigned_to", text="Assigned To", anchor=tk.CENTER)
        tree.heading("date_assigned", text="Date Assigned", anchor=tk.CENTER)
        tree.heading("status", text="Status", anchor=tk.CENTER)

        tree.tag_configure("evenrow", background="#FFFFFF")
        tree.tag_configure("oddrow", background="#F8FAFC")
        return tree

    def load_assignments(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT a.AssignmentID, t.TaskName, s.StudentName,
                       a.DateAssigned, a.Status
                FROM Assignment a
                JOIN Task t ON a.TaskID = t.TaskID
                JOIN Member m ON a.MemberID = m.MemberID
                JOIN Student s ON m.StudentID = s.StudentID
                ORDER BY a.AssignmentID
            """)
            rows = cursor.fetchall()
            cursor.close()
            self._assignment_rows = rows
            self.refresh_assignment_table()
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to load assignments: {e}")

    def refresh_assignment_table(self):
        for item in self.assignments_tree.get_children():
            self.assignments_tree.delete(item)
        self.assignment_no_results_label.lower()

        query = (
            self.assignment_search_var.get().strip().lower()
            if hasattr(self, "assignment_search_var")
            else ""
        )
        task_filter = (
            self.assignment_task_filter.get()
            if hasattr(self, "assignment_task_filter")
            else "All Tasks"
        )
        rows = [
            row
            for row in getattr(self, "_assignment_rows", [])
            if task_filter == "All Tasks" or row[1] == task_filter
        ]
        rows = [
            row
            for row in rows
            if not query
            or any(
                query in str(row[index]).lower()
                for index in range(len(row))
                if row[index] is not None
            )
        ]
        if not rows:
            self.assignment_no_results_label.lift()
            return
        for index, row in enumerate(rows):
            tag = "evenrow" if index % 2 == 0 else "oddrow"
            self.assignments_tree.insert("", tk.END, values=row, tags=(tag,))

    def _on_task_selected(self, tree):
        selected = tree.focus()
        if not selected:
            return
        values = tree.item(selected, "values")
        if not values:
            return

        self.task_update_name_entry.delete(0, tk.END)
        self.task_update_name_entry.insert(0, values[1])
        self.task_update_committee_combo.set(values[2] if values[2] else "")
        self.task_update_due_date_entry.delete(0, tk.END)
        self.task_update_due_date_entry.insert(0, values[3] if values[3] else "")
        self._selected_task_id = values[0]

    def _on_assignment_selected(self, tree):
        selected = tree.focus()
        if not selected:
            return
        values = tree.item(selected, "values")
        if not values:
            return

        self.assignment_update_task_combo.set(values[1] if values[1] else "")
        self.assignment_update_member_combo.set(values[2] if values[2] else "")
        self.assignment_update_date_entry.delete(0, tk.END)
        self.assignment_update_date_entry.insert(0, values[3] if values[3] else "")
        self.assignment_update_status_combo.set(values[4] if values[4] else "")
        self._selected_assignment_id = values[0]

    def update_task(self):
        if not hasattr(self, "_selected_task_id"):
            messagebox.showwarning("Selection Error", "Please select a task to update.")
            return

        task_name = self.update_task_name_entry.get().strip()
        committee_name = self.update_task_committee_combo.get()
        due_date = self.update_task_due_date_entry.get().strip()
        if (task_name, committee_name, due_date) == getattr(
            self, "_selected_task_original", None
        ):
            messagebox.showinfo("No Changes", "No task fields were changed.")
            return
        committee_id = next(
            (cid for cid, name in self.committees_list if name == committee_name),
            None,
        )

        if not task_name or not committee_id or not due_date:
            messagebox.showwarning("Input Error", "All task fields are required.")
            return

        import re

        if not re.match(r"^\d{4}-\d{2}-\d{2}$", due_date):
            messagebox.showwarning(
                "Input Error", "Due date must be in YYYY-MM-DD format."
            )
            return

        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                UPDATE Task
                SET TaskName=%s, CommitteeID=%s, DueDate=%s
                WHERE TaskID=%s
                """,
                (task_name, committee_id, due_date, self._selected_task_id),
            )
            self.connection.commit()
            cursor.close()
            self.load_tasks()
            self._load_tasks_for_assignment()
            self.load_assignments()
            self.task_update_btn.config(state="disabled")
            self.task_delete_btn.config(state="disabled")
            messagebox.showinfo("Success", "Task updated successfully.")
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to update task: {e}")

    def update_assignment(self):
        if not hasattr(self, "_selected_assignment_id"):
            messagebox.showwarning(
                "Selection Error", "Please select an assignment to update."
            )
            return

        task_name = self.update_assignment_task_entry.get()
        member_name = self.update_assignment_member_combo.get()
        date_assigned = self.update_assignment_date_entry.get().strip()
        status = self.update_assignment_status_combo.get()
        if (task_name, member_name, date_assigned, status) == getattr(
            self, "_selected_assignment_original", None
        ):
            messagebox.showinfo("No Changes", "No assignment fields were changed.")
            return
        task_id = next(
            (tid for tid, name in self.tasks_list if name == task_name), None
        )
        member_id = next(
            (mid for mid, name in self.members_list if name == member_name), None
        )

        if not task_id or not member_id or not date_assigned or not status:
            messagebox.showwarning("Input Error", "All assignment fields are required.")
            return

        import re

        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_assigned):
            messagebox.showwarning(
                "Input Error", "Date assigned must be in YYYY-MM-DD format."
            )
            return

        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                UPDATE Assignment
                SET TaskID=%s, MemberID=%s, DateAssigned=%s, Status=%s
                WHERE AssignmentID=%s
                """,
                (
                    task_id,
                    member_id,
                    date_assigned,
                    status,
                    self._selected_assignment_id,
                ),
            )
            self.connection.commit()
            cursor.close()
            self.load_assignments()
            self.assignment_update_btn.config(state="disabled")
            self.assignment_delete_btn.config(state="disabled")
            messagebox.showinfo("Success", "Assignment updated successfully.")
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to update assignment: {e}")

    def delete_task(self):
        if not hasattr(self, "_selected_task_id"):
            messagebox.showwarning("Selection Error", "Please select a task to delete.")
            return

        task_id = self._selected_task_id
        if not messagebox.askyesno(
            "Confirm Delete", f"Are you sure you want to delete Task #{task_id}?"
        ):
            return

        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM Assignment WHERE TaskID=%s", (task_id,))
            cursor.execute("DELETE FROM Task WHERE TaskID=%s", (task_id,))
            self.connection.commit()
            cursor.close()
            self._tasks_rows = [
                row for row in getattr(self, "_tasks_rows", []) if row[0] != task_id
            ]
            self.load_tasks()
            self._load_tasks_for_assignment()
            self.load_assignments()
            self.update_task_name_entry.delete(0, tk.END)
            self.update_task_committee_combo.set("")
            self.update_task_due_date_entry.delete(0, tk.END)
            self._selected_task_id = None
            self._selected_task_original = None
            self.task_update_btn.config(state="disabled")
            self.task_delete_btn.config(state="disabled")
            messagebox.showinfo("Success", "Task deleted successfully.")
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to delete task: {e}")

    def delete_assignment(self):
        if not hasattr(self, "_selected_assignment_id"):
            messagebox.showwarning(
                "Selection Error", "Please select an assignment to delete."
            )
            return

        assignment_id = self._selected_assignment_id
        if not messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete Assignment #{assignment_id}?",
        ):
            return

        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "DELETE FROM Assignment WHERE AssignmentID=%s", (assignment_id,)
            )
            self.connection.commit()
            cursor.close()
            self._assignment_rows = [
                row
                for row in getattr(self, "_assignment_rows", [])
                if row[0] != assignment_id
            ]
            self.load_assignments()
            self.update_assignment_task_entry.set("")
            self.update_assignment_member_combo.set("")
            self.update_assignment_date_entry.delete(0, tk.END)
            self.update_assignment_status_combo.set("")
            self._selected_assignment_id = None
            self._selected_assignment_original = None
            self.assignment_update_btn.config(state="disabled")
            self.assignment_delete_btn.config(state="disabled")
            messagebox.showinfo("Success", "Assignment deleted successfully.")
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to delete assignment: {e}")

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
            if hasattr(self, "task_committee_filter"):
                committee_names = sorted(set(r[2] for r in rows if r[2]))
                self.task_committee_filter["values"] = [
                    "All Committees"
                ] + committee_names
            if hasattr(self, "assignment_task_filter"):
                task_names = [r[1] for r in rows if r[1]]
                self.assignment_task_filter["values"] = [
                    "All Tasks"
                ] + task_names
                self.assignment_task_filter.set("All Tasks")
            self.refresh_task_table()
            if hasattr(self, "update_assignment_task_entry"):
                self.update_assignment_task_entry["values"] = [
                    name for (_id, name, _committee, _due_date) in rows
                ]
            if hasattr(self, "assignment_update_task_combo"):
                self.assignment_update_task_combo["values"] = [
                    name for (_id, name, _committee, _due_date) in rows
                ]
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to load tasks: {e}")

    def refresh_task_table(self):
        for item in self.tasks_tree.get_children():
            self.tasks_tree.delete(item)
        self.task_no_results_label.lower()

        rows = getattr(self, "_tasks_rows", [])

        committee_filter = (
            self.task_committee_filter.get()
            if hasattr(self, "task_committee_filter")
            else "All Committees"
        )
        if committee_filter and committee_filter != "All Committees":
            rows = [r for r in rows if r[2] == committee_filter]

        query = (
            self.task_search_var.get().strip().lower()
            if hasattr(self, "task_search_var")
            else ""
        )
        if query:
            rows = [
                row
                for row in rows
                if any(
                    query in str(value).lower()
                    for value in row
                    if value is not None
                )
            ]

        if not rows:
            self.task_no_results_label.lift()
            return

        for index, row in enumerate(rows):
            tag = "evenrow" if index % 2 == 0 else "oddrow"
            self.tasks_tree.insert("", tk.END, values=row, tags=(tag,))

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

        query = (
            self.search_var.get().strip().lower() if hasattr(self, "search_var") else ""
        )
        if query:
            data = [
                row
                for row in data
                if any(
                    query in str(value).lower()
                    for value in row
                    if value is not None
                )
            ]

        if not data:
            self.no_results_label.lift()
            return

        self.no_results_label.lower()

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
    def add_student(self, button_requested=False):
        if not button_requested:
            return

        name = self.name_entry.get().strip()
        grade = self.grade_entry.get().strip()
        section = self.section_entry.get().strip()
        email_username = self.email_entry.get().strip()
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
        if not email_username:
            messagebox.showwarning("Input Error", "Email is required.")
            return
        if not committee_name:
            messagebox.showwarning("Input Error", "Committee is required.")
            return
        if not role:
            messagebox.showwarning("Input Error", "Role is required.")
            return

        email = email_username + "@addu.edu.ph"

        if not self._verify_pin("add this student"):
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
            self._load_members_for_assignment()
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
        self._selected_student_id = None
        self._selected_student_original = None

    def _prompt_unlock(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Enter Passkey")
        dialog.configure(bg="#F7FFF9")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)

        dialog.update_idletasks()
        w, h = 320, 230
        try:
            rx = self.root.winfo_rootx()
            ry = self.root.winfo_rooty()
            rw = self.root.winfo_width()
            rh = self.root.winfo_height()
            x = rx + (rw // 2 - w // 2)
            y = ry + (rh // 2 - h // 2)
            sw = dialog.winfo_screenwidth()
            sh = dialog.winfo_screenheight()
            x = max(0, min(x, sw - w - 10))
            y = max(0, min(y, sh - h - 10))
        except Exception:
            x = (dialog.winfo_screenwidth() // 2) - (w // 2)
            y = (dialog.winfo_screenheight() // 2) - (h // 2)
        dialog.geometry(f"{w}x{h}+{x}+{y}")
        content = tk.Frame(dialog, bg="#F7FFF9")
        content.pack(fill="both", expand=True, padx=20, pady=15)

        tk.Label(
            content,
            text="Enter passkey to view student records:",
            bg="#F7FFF9",
            fg=self.THEME["text"],
            font=("Segoe UI", 10, "bold"),
            justify="center",
        ).pack(fill="x", pady=(0, 8))

        entry_var = tk.StringVar()
        entry = ctk.CTkEntry(
            content,
            textvariable=entry_var,
            height=42,
            corner_radius=10,
            border_width=1,
            border_color=self.THEME["border"],
            fg_color=self.THEME["card"],
            text_color=self.THEME["text"],
            show="•",
            font=("Segoe UI", 14),
            justify="center",
        )
        entry.pack(anchor="center", pady=(0, 10))
        entry.focus_set()

        show_var = tk.BooleanVar(value=False)

        def toggle_show():
            entry.configure(show="" if show_var.get() else "•")

        ctk.CTkCheckBox(
            content,
            text="Show passkey",
            variable=show_var,
            command=toggle_show,
            text_color=self.THEME["text"],
            fg_color=self.THEME["green"],
            hover_color=self.THEME["green_dark"],
            border_color=self.THEME["border"],
            border_width=1,
            corner_radius=4,
            checkbox_width=20,
            checkbox_height=20,
            font=("Segoe UI", 12),
        ).pack(anchor="center", pady=(0, 15))

        error_label = tk.Label(
            content,
            text="",
            bg="#F7FFF9",
            fg=self.THEME["danger"],
            font=("Segoe UI", 9),
            anchor="center",
            justify="center",
        )
        error_label.pack(fill="x", pady=(0, 8))

        result = {"value": None}

        def confirm():
            if entry_var.get() == self.STUDENT_PASSKEY:
                result["value"] = entry_var.get()
                dialog.destroy()
            else:
                error_label.config(text="Incorrect passkey. Please try again.")
                entry.selection_range(0, tk.END)
                entry.focus_set()

        def cancel():
            dialog.destroy()

        btn_row = tk.Frame(content, bg="#F7FFF9")
        btn_row.pack(anchor="center")
        ModernButton(
            btn_row, text="Confirm", style="Add.TButton", command=confirm, width=96
        ).pack(side="left", padx=(0, 8))
        ModernButton(
            btn_row, text="Cancel", style="Update.TButton", command=cancel, width=96
        ).pack(side="left")

        entry.bind("<Return>", lambda e: confirm())
        dialog.bind("<Escape>", lambda e: cancel())
        dialog.wait_window()

        entered = result["value"]
        if entered is None:
            return
        if entered == self.STUDENT_PASSKEY:
            self.data_frame.tkraise()
            self.load_students()
        else:
            return

    def _prompt_unlock_tasks(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Enter Passkey")
        dialog.configure(bg="#F7FFF9")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)
        dialog.update_idletasks()
        w, h = 320, 230
        try:
            rx = self.root.winfo_rootx()
            ry = self.root.winfo_rooty()
            rw = self.root.winfo_width()
            rh = self.root.winfo_height()
            x = rx + (rw // 2 - w // 2)
            y = ry + (rh // 2 - h // 2)
            sw = dialog.winfo_screenwidth()
            sh = dialog.winfo_screenheight()
            x = max(0, min(x, sw - w - 10))
            y = max(0, min(y, sh - h - 10))
        except Exception:
            x = (dialog.winfo_screenwidth() // 2) - (w // 2)
            y = (dialog.winfo_screenheight() // 2) - (h // 2)
        dialog.geometry(f"{w}x{h}+{x}+{y}")
        content = tk.Frame(dialog, bg="#F7FFF9")
        content.pack(fill="both", expand=True, padx=20, pady=15)
        tk.Label(
            content,
            text="Enter passkey to view tasks:",
            bg="#F7FFF9",
            fg=self.THEME["text"],
            font=("Segoe UI", 10, "bold"),
            justify="center",
        ).pack(fill="x", pady=(0, 8))
        entry_var = tk.StringVar()
        entry = ctk.CTkEntry(
            content,
            textvariable=entry_var,
            height=42,
            corner_radius=10,
            border_width=1,
            border_color=self.THEME["border"],
            fg_color=self.THEME["card"],
            text_color=self.THEME["text"],
            show="•",
            font=("Segoe UI", 14),
            justify="center",
        )
        entry.pack(anchor="center", pady=(0, 10))
        entry.focus_set()
        show_var = tk.BooleanVar(value=False)

        def toggle_show():
            entry.configure(show="" if show_var.get() else "•")

        ctk.CTkCheckBox(
            content,
            text="Show passkey",
            variable=show_var,
            command=toggle_show,
            text_color=self.THEME["text"],
            fg_color=self.THEME["green"],
            hover_color=self.THEME["green_dark"],
            border_color=self.THEME["border"],
            border_width=1,
            corner_radius=4,
            checkbox_width=20,
            checkbox_height=20,
            font=("Segoe UI", 12),
        ).pack(anchor="center", pady=(0, 15))
        error_label = tk.Label(
            content,
            text=" ",
            bg="#F7FFF9",
            fg=self.THEME["danger"],
            font=("Segoe UI", 9),
            anchor="center",
            justify="center",
        )
        error_label.pack(fill="x", pady=(0, 8))
        result = {"value": None}

        def confirm():
            if entry_var.get() == self.STUDENT_PASSKEY:
                result["value"] = entry_var.get()
                dialog.destroy()
            else:
                error_label.config(text="Incorrect passkey. Please try again.")
                entry.selection_range(0, tk.END)
                entry.focus_set()

        def cancel():
            dialog.destroy()

        btn_row = tk.Frame(content, bg="#F7FFF9")
        btn_row.pack(anchor="center")
        ModernButton(
            btn_row, text="Confirm", style="Add.TButton", command=confirm, width=96
        ).pack(side="left", padx=(0, 8))
        ModernButton(
            btn_row, text="Cancel", style="Update.TButton", command=cancel, width=96
        ).pack(side="left")
        entry.bind("<Return>", lambda e: confirm())
        dialog.bind("<Escape>", lambda e: cancel())
        dialog.wait_window()
        entered = result["value"]
        if entered is None:
            return
        if entered == self.STUDENT_PASSKEY:
            self.task_data_frame.tkraise()
            self.load_tasks()
            self.load_assignments()
        else:
            return

    def _verify_pin(self, action_label="perform this action"):
        dialog = tk.Toplevel(self.root)
        dialog.title("Verify PIN")
        dialog.configure(bg="#F7FFF9")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)

        dialog.update_idletasks()
        w, h = 300, 215
        try:
            rx = self.root.winfo_rootx()
            ry = self.root.winfo_rooty()
            rw = self.root.winfo_width()
            rh = self.root.winfo_height()
            x = rx + (rw // 2 - w // 2)
            y = ry + (rh // 2 - h // 2)
            sw = dialog.winfo_screenwidth()
            sh = dialog.winfo_screenheight()
            x = max(0, min(x, sw - w - 10))
            y = max(0, min(y, sh - h - 10))
        except Exception:
            x = (dialog.winfo_screenwidth() // 2) - (w // 2)
            y = (dialog.winfo_screenheight() // 2) - (h // 2)
        dialog.geometry(f"{w}x{h}+{x}+{y}")

        content = tk.Frame(dialog, bg="#F7FFF9")
        content.pack(fill="both", expand=True, padx=20, pady=15)

        tk.Label(
            content,
            text=f"Enter 4-digit PIN to {action_label}:",
            bg="#F7FFF9",
            fg=self.THEME["text"],
            font=("Segoe UI", 10),
            wraplength=260,
            justify="center",
        ).pack(fill="x", pady=(0, 8))

        vcmd = (dialog.register(lambda s: s.isdigit() and len(s) <= 4 or s == ""), "%P")

        pin_var = tk.StringVar()
        entry = ttk.Entry(
            content,
            textvariable=pin_var,
            width=10,
            show="•",
            justify="center",
            font=("Segoe UI", 14),
            validate="key",
            validatecommand=vcmd,
        )
        entry.pack(pady=(0, 15))
        entry.focus_set()

        show_var = tk.BooleanVar(value=False)

        def toggle_show():
            entry.configure(show="" if show_var.get() else "•")

        ctk.CTkCheckBox(
            content,
            text="Show passkey",
            variable=show_var,
            command=toggle_show,
            text_color=self.THEME["text"],
            fg_color=self.THEME["green"],
            hover_color=self.THEME["green_dark"],
            border_color=self.THEME["border"],
            border_width=1,
            corner_radius=4,
            checkbox_width=20,
            checkbox_height=20,
            font=("Segoe UI", 11),
        ).pack(anchor="center", pady=(0, 15))

        result = {"value": None}

        def confirm():
            result["value"] = pin_var.get()
            dialog.destroy()

        def cancel():
            dialog.destroy()

        btn_row = tk.Frame(content, bg="#F7FFF9")
        btn_row.pack(anchor="center")
        ModernButton(
            btn_row, text="Confirm", style="Add.TButton", command=confirm, width=96
        ).pack(side="left", padx=(0, 8))
        ModernButton(
            btn_row, text="Cancel", style="Update.TButton", command=cancel, width=96
        ).pack(side="left")

        entry.bind("<Return>", lambda e: confirm())
        dialog.wait_window()

        entered = result["value"]
        if entered is None:
            return False
        if entered == self.ACTION_PIN:
            return True
        messagebox.showerror("Access Denied", "Incorrect PIN.")
        return False

    def on_student_select(self, tree):
        selected = tree.focus()
        if selected:
            if "no_results" in tree.item(selected, "tags"):
                tree.selection_remove(selected)
                tree.focus("")
                return
            values = tree.item(selected, "values")
            if values:
                self.edit_name_entry.delete(0, tk.END)
                self.edit_name_entry.insert(0, values[1])
                grade_value = values[2] if values[2] else ""
                self.edit_grade_entry.set(grade_value)
                self.edit_section_entry["values"] = GRADE_SECTIONS.get(grade_value, [])
                self.edit_section_entry.set(values[3] if values[3] else "")
                self.edit_email_entry.delete(0, tk.END)
                self.edit_email_entry.insert(
                    0, values[4].replace("@addu.edu.ph", "") if values[4] else ""
                )
                self.edit_committee_combo.set(values[5] if values[5] else "")
                self.edit_role_combo.set(values[6] if values[6] else "")
                self._selected_student_id = values[0]
                self._selected_student_original = (
                    values[1] or "",
                    grade_value,
                    values[3] or "",
                    values[4].replace("@addu.edu.ph", "") if values[4] else "",
                    values[5] or "",
                    values[6] or "",
                )
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
        email = self.edit_email_entry.get().strip() + "@addu.edu.ph"
        committee_name = self.edit_committee_combo.get()
        role = self.edit_role_combo.get()

        current_values = (
            name,
            grade,
            section,
            self.edit_email_entry.get().strip(),
            committee_name,
            role,
        )
        if current_values == getattr(self, "_selected_student_original", None):
            messagebox.showinfo("No Changes", "No student fields were changed.")
            return

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

        if not self._verify_pin("add this task"):
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
            self.load_tasks()
            self._load_tasks_for_assignment()

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
            if hasattr(self, "assignment_task_filter"):
                self.assignment_task_filter["values"] = ["All Tasks"] + task_names
                self.assignment_task_filter.set("All Tasks")
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
            if hasattr(self, "assignment_update_member_combo"):
                self.assignment_update_member_combo["values"] = member_names
            if hasattr(self, "update_assignment_member_combo"):
                self.update_assignment_member_combo["values"] = member_names
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

        if not self._verify_pin("assign this task"):
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
            self.load_assignments()

        except Error as e:
            messagebox.showerror("Database Error", f"Failed to assign task: {e}")


if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    app = AshscomGUI(root)
    root.mainloop()
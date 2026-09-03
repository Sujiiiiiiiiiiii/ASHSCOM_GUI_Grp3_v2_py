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

        header_frame = tk.Frame(self.root, bg="#ADFFB1")
        header_frame.pack(fill="x")
        header_frame.columnconfigure(0, weight=0)
        header_frame.columnconfigure(1, weight=1)

        logo1_img = Image.open("ateneo1.png").resize((60, 60))
        self.logo1 = ImageTk.PhotoImage(logo1_img)
        
        logo2_img = Image.open("ashscom.png").resize((80, 80))
        self.logo2 = ImageTk.PhotoImage(logo2_img)

        logo_frame = tk.Frame(header_frame, bg="#ADFFB1")
        logo_frame.grid(row=0, column=0, sticky="w",padx=15, pady=10)

        tk.Label(
            logo_frame, image=self.logo1, bg="#ADFFB1").pack(side="left", padx=(5,0))
        tk.Label(
            logo_frame, image=self.logo2, bg="#ADFFB1").pack(side="left", padx=(0,5))

        text_frame = tk.Frame(header_frame, bg="#ADFFB1")
        text_frame.grid(row=0, column=1, sticky="e", padx=15, pady=10)

        tk.Label(text_frame, text="Ateneo De Davao University Senior High School\nCommission on Elections\nASHSCOM MANAGEMENT SYSTEM",
            font=("Segoe UI", 12, "bold"), bg="#ADFFB1", fg="#004202", justify="right").pack(anchor="e", pady=(0, 0))

        divider = tk.Frame(self.root, bg="darkgreen", height=3)
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

        # Add content to the Users tab
        users_label = ttk.Label(users_frame, text="Manage Users", font=("Arial", 16))
        users_label.pack(pady=20)

    def create_settings_tab(self):
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="Settings")

        # Add content to the Settings tab
        settings_label = ttk.Label(settings_frame, text="Application Settings", font=("Arial", 16))
        settings_label.pack(pady=20)


if __name__ == "__main__":
    root = tk.Tk()
    app = AshscomGUI(root)
    root.mainloop()


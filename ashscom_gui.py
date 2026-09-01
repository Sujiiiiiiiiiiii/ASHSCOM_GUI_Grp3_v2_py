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
        self.root.configure(bg="lightgreen")
        tk.Label(self.root, text="Ashscom Management System", font=("Times New Roman", 25)).pack(pady=10)
        

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


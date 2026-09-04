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
        self.notebook.add(settings_frame, text="Assignment")

        # Add content to the Assignment tab
        settings_label = ttk.Label(settings_frame, text="Assign Members to Task", font=("Arial", 16))
        settings_label.pack(pady=20)


if __name__ == "__main__":
    root = tk.Tk()
    app = AshscomGUI(root)
    root.mainloop()


import tkinter as tk

class GUIManager:
    """
    Minimal GUI Manager for Cherry AI Assistant
    """

    def __init__(self, cherry_brain=None, config=None):
        self.cherry_brain = cherry_brain
        self.config = config
        self.root = None

    def show(self):
        print("Opening Cherry GUI window...")
        self._create_gui()

    def _create_gui(self):
        print("Creating Tkinter root window...")
        self.root = tk.Tk()
        self.root.title("🍒 Cherry AI Assistant")
        self.root.geometry("400x400")
        
        # Simple label
        label = tk.Label(self.root, text="Hello from Cherry!", font=("Arial", 16))
        label.pack(pady=40)

        # Exit button
        exit_btn = tk.Button(self.root, text="Exit", command=self.root.quit)
        exit_btn.pack(pady=15)

        print("Starting Tkinter mainloop...")
        self.root.mainloop()
        print("Cherry GUI closed.")

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class JuiceMakerApp:
    def __init__(self, root):
        detection="None"
        conf=0
        img_path="streamlit.png"
        self.root = root
        self.root.title("Robotic Juice Maker")
        self.root.geometry("700x600")
        self.root.configure(bg="#f0f2f6")
        
        # State variables
        self.msg = ""
        self.status = "Waiting for selection"
        
        # Main title
        title = tk.Label(
            root, 
            text="Welcome to the Robotic Juice maker!", 
            font=("Arial", 20, "bold"),
            bg="#f0f2f6",
            fg="#262730"
        )
        title.pack(pady=20)
        
        # Subtitle
        subtitle = tk.Label(
            root, 
            text="Choose a juice from our selection", 
            font=("Arial", 14),
            bg="#f0f2f6",
            fg="#262730"
        )
        subtitle.pack(pady=5)
        
        # Frame for buttons
        button_frame = tk.Frame(root, bg="#f0f2f6")
        button_frame.pack(pady=20)
        
        # Juice options
        juices = [
            ("Kiwi Berry Splash", "Kiwi\n Strawberry\n Green apple", 1),
            ("Garden Duo Juice", "Tomato\n Carrot\n", 2),
            ("Carrot Kiwi Citrus Mix", "Carrot\n Kiwi\n Lemon", 3)
        ]
        
        for i, (name, ingredients, preset) in enumerate(juices):
            frame = tk.Frame(button_frame, bg="#f0f2f6")
            frame.grid(row=0, column=i, padx=15)
            
            btn = tk.Button(
                frame,
                text=name,
                command=lambda p=preset: self.make_smoothie(p),
                font=("Arial", 11, "bold"),
                bg="#ff4b4b",
                fg="white",
                width=18,
                height=2,
                relief=tk.RAISED,
                cursor="hand2"
            )
            btn.pack(pady=5)
            
            ingredients_label = tk.Label(
                frame,
                text=f"Ingredients:\n {ingredients}",
                font=("Arial", 10),
                bg="#f0f2f6",
                fg="#262730"
            )
            ingredients_label.pack()
        
        # Status label
        self.status_label = tk.Label(
            root,
            text=self.status,
            font=("Arial", 11),
            bg="#f0f2f6",
            fg="#262730"
        )
        self.status_label.pack(pady=10)
        
        # Success message label
        self.msg_label = tk.Label(
            root,
            text="",
            font=("Arial", 11, "bold"),
            bg="#d4edda",
            fg="#155724",
            pady=10
        )
        
        # Image section
        img_title = tk.Label(
            root,
            text=f"Last detection: {detection} Confidence: {conf}% ",
            font=("Arial", 11),
            bg="#f0f2f6",
            fg="#262730"
        )
        img_title.pack(pady=(20, 5))
        
        # Load and display image
        try:
            img = Image.open(img_path)
            img = img.resize((200, 150), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            img_label = tk.Label(root, image=photo, bg="#f0f2f6")
            img_label.image = photo  
            img_label.pack()
        except FileNotFoundError:
            placeholder = tk.Label(
                root,
                text="[Image: streamlit.png not found]",
                font=("Arial", 10),
                bg="#e0e0e0",
                fg="#666666",
                width=30,
                height=8
            )
            placeholder.pack()
    
    def make_smoothie(self, preset):
        self.status = "Preparing your juice..."
        self.update_display()
        
        # Simulate preparation time
        self.root.after(1000, lambda: self.finish_smoothie(preset))
    
    def finish_smoothie(self, preset):
        self.status = "Waiting for next selection"
        
        if preset == 1:
            self.msg = "Kiwi Berry Splash ready!"
        elif preset == 2:
            self.msg = "Garden Duo Juice ready!"
        elif preset == 3:
            self.msg = "Carrot Kiwi Citrus Mix ready!"
        
        self.update_display()
    
    def update_display(self):
        self.status_label.config(text=self.status)
        
        if self.msg:
            self.msg_label.config(text=self.msg)
            self.msg_label.pack(pady=10)
        else:
            self.msg_label.pack_forget()

if __name__ == "__main__":
    root = tk.Tk()
    app = JuiceMakerApp(root)
    root.mainloop()
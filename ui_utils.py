import tkinter as tk

def create_modern_button(parent, text, command, bg_color, width=15, height=2):
    # If the background color is light, use a darker text color for better contrast
    fg_color = "white"
    
    btn = tk.Button(parent, text=text, command=command, bg=bg_color, fg=fg_color,
                     font=("Helvetica", 12, "bold"), width=width, height=height,
                     relief="flat", cursor="hand2", borderwidth=0,
                     activebackground="#3b82f6", activeforeground="white",
                     highlightthickness=0, pady=5)
    
    def on_enter(e):
        e.widget.config(bg="#475569", fg="white") # slate-600 on hover

    def on_leave(e):
        e.widget.config(bg=bg_color, fg=fg_color)

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

    return btn

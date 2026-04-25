import tkinter as tk
from tkinter import ttk, messagebox, font
import os
import platform
import shutil
import subprocess
import getpass
import psutil
import threading

# Paletas y contastes

BG        = "#0d1117"
BG2       = "#161b22"
BG3       = "#21262d"
ACCENT    = "#58a6ff"
ACCENT2   = "#3fb950"
DANGER    = "#f85149"
WARNING   = "#d29922"
TEXT      = "#e6edf3"
TEXT_DIM  = "#8b949e"
BORDER    = "#30363d"
FONT_MONO = ("Courier New", 11)
FONT_UI   = ("Segoe UI", 10) if platform.system() == "Windows" else ("Helvetica", 10)
FONT_H1   = ("Segoe UI", 14, "bold") if platform.system() == "Windows" else ("Helvetica", 14, "bold")
FONT_H2   = ("Segoe UI", 12, "bold") if platform.system() == "Windows" else ("Helvetica", 12, "bold")

# modo oscuro
def apply_dark(widget):
    try:
        widget.configure(bg=BG)
    except Exception:
        pass
    for child in widget.winfo_children():
        apply_dark(child)

# ventana secundaria con estilo conscitente
def make_window(title: str, width: int = 700, height: int = 500) -> tk.Toplevel:
    win = tk.Toplevel(bg=BG)
    win.title(title)
    win.geometry(f"{width}x{height}")
    win.resizable(True, True)
    # Centrar
    win.update_idletasks()
    x = (win.winfo_screenwidth() - width) // 2
    y = (win.winfo_screenheight() - height) // 2
    win.geometry(f"{width}x{height}+{x}+{y}")
    return win

def styled_button(parent, text, command, color=ACCENT, fg=BG, **kw):
    btn = tk.Button(
        parent, text=text, command=command,
        bg=color, fg=fg, activebackground=color,
        activeforeground=fg, relief="flat", cursor="hand2",
        font=FONT_UI, padx=14, pady=6, bd=0, **kw
    )
    btn.bind("<Enter>", lambda e: btn.config(bg=_lighten(color)))
    btn.bind("<Leave>", lambda e: btn.config(bg=color))
    return btn

# aclaracion leve de color hex
def _lighten(hex_color: str) -> str:
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    r = min(255, r + 30)
    g = min(255, g + 30)
    b = min(255, b + 30)
    return f"#{r:02x}{g:02x}{b:02x}"


def label(parent, text, **kw):
    defaults = dict(bg=BG, fg=TEXT, font=FONT_UI)
    defaults.update(kw)
    return tk.Label(parent, text=text, **defaults)


def separator(parent):
    return tk.Frame(parent, bg=BORDER, height=1)
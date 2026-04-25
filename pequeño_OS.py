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

#---A. EXPLORADOR DE ARCHIVOS---
class FileExplorer:
    def __init__(self):
        self.cwd = os.path.expanduser("~")
        self.win = make_window("Explorador de Archivos", 700, 520)
        self._build()

    def _build(self):
        w = self.win

        # Barra de ruta
        top = tk.Frame(w, bg=BG2, pady=8, padx=10)
        top.pack(fill="x")
        label(top, "Ruta:", bg=BG2, fg=TEXT_DIM).pack(side="left")
        self.path_var = tk.StringVar(value=self.cwd)
        self.path_entry = tk.Entry(
            top, textvariable=self.path_var, bg=BG3, fg=TEXT,
            insertbackground=ACCENT, relief="flat", font=FONT_MONO,
            width=50
        )
        self.path_entry.pack(side="left", padx=8, fill="x", expand=True)
        self.path_entry.bind("<Return>", lambda e: self._navigate_to(self.path_var.get()))

        separator(w).pack(fill="x")

        # Botones de acción
        btn_bar = tk.Frame(w, bg=BG, pady=6, padx=10)
        btn_bar.pack(fill="x")
        styled_button(btn_bar, "Subir nivel", self._go_up, color=BG3, fg=TEXT).pack(side="left", padx=4)
        styled_button(btn_bar, "Refrescar",   self._refresh,  color=BG3, fg=TEXT).pack(side="left", padx=4)
        self.count_lbl = label(btn_bar, "", fg=TEXT_DIM)
        self.count_lbl.pack(side="right", padx=8)

        separator(w).pack(fill="x")

        # Lista de archivos
        list_frame = tk.Frame(w, bg=BG)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        cols = ("icon", "nombre", "tipo", "tamaño")
        self.tree = ttk.Treeview(list_frame, columns=cols, show="headings", selectmode="browse")
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                         background=BG2, foreground=TEXT,
                         fieldbackground=BG2, rowheight=24,
                         font=FONT_UI)
        style.configure("Treeview.Heading",
                         background=BG3, foreground=ACCENT,
                         font=(FONT_UI[0], FONT_UI[1], "bold"))
        style.map("Treeview", background=[("selected", BG3)], foreground=[("selected", ACCENT)])

        self.tree.heading("icon",   text="")
        self.tree.heading("nombre", text="Nombre")
        self.tree.heading("tipo",   text="Tipo")
        self.tree.heading("tamaño", text="Tamaño")
        self.tree.column("icon",   width=28,  stretch=False, anchor="center")
        self.tree.column("nombre", width=300, stretch=True)
        self.tree.column("tipo",   width=100, stretch=False, anchor="center")
        self.tree.column("tamaño", width=90,  stretch=False, anchor="e")

        sb = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", self._on_double_click)

        # Mensaje vacío
        self.empty_lbl = label(w, "Esta carpeta esta vacia.", fg=TEXT_DIM, font=(FONT_UI[0], 11, "italic"))

        self._refresh()

    def _refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.empty_lbl.pack_forget()

        try:
            entries = sorted(os.scandir(self.cwd), key=lambda e: (not e.is_dir(), e.name.lower()))
        except PermissionError:
            messagebox.showerror("Permiso denegado", f"No se puede acceder a:\n{self.cwd}")
            return

        self.path_var.set(self.cwd)

        if not entries:
            self.empty_lbl.pack(pady=20)
            self.count_lbl.config(text="0 elementos")
            return

        self.count_lbl.config(text=f"{len(entries)} elementos")
        for e in entries:
            if e.is_dir():
                icon, tipo, size = "[DIR]", "Carpeta", "—"
            else:
                icon = "[FILE]"
                ext  = os.path.splitext(e.name)[1].upper() or "Archivo"
                tipo = ext
                try:
                    size = self._fmt_size(e.stat().st_size)
                except OSError:
                    size = "?"
            self.tree.insert("", "end", values=(icon, e.name, tipo, size))

    def _on_double_click(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0], "values")
        name = vals[1]
        path = os.path.join(self.cwd, name)
        if os.path.isdir(path):
            self._navigate_to(path)

    def _navigate_to(self, path):
        if os.path.isdir(path):
            self.cwd = path
            self._refresh()

    def _go_up(self):
        parent = os.path.dirname(self.cwd)
        if parent != self.cwd:
            self._navigate_to(parent)

    @staticmethod
    def _fmt_size(n: int) -> str:
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if n < 1024:
                return f"{n:.1f} {unit}"
            n /= 1024
        return f"{n:.1f} PB"

#---B. GESTION DE PROCESOS---

class ProcessManager:
    def __init__(self):
        self.win = make_window("Gestion de Procesos", 750, 540)
        self._build()

    def _build(self):
        w = self.win

        # Cabecera
        hdr = tk.Frame(w, bg=BG2, pady=8, padx=12)
        hdr.pack(fill="x")
        label(hdr, "Filtrar por nombre:", bg=BG2, fg=TEXT_DIM).pack(side="left")
        self.filter_var = tk.StringVar()
        self.filter_var.trace_add("write", lambda *_: self._refresh())
        flt = tk.Entry(hdr, textvariable=self.filter_var, bg=BG3, fg=TEXT,
                       insertbackground=ACCENT, relief="flat", font=FONT_MONO, width=25)
        flt.pack(side="left", padx=8)
        styled_button(hdr, "Actualizar", self._refresh, color=BG3, fg=TEXT).pack(side="left", padx=4)
        self.count_lbl = label(hdr, "", fg=TEXT_DIM, bg=BG2)
        self.count_lbl.pack(side="right", padx=8)

        separator(w).pack(fill="x")

        # Tabla
        tbl_frame = tk.Frame(w, bg=BG)
        tbl_frame.pack(fill="both", expand=True, padx=10, pady=8)

        cols = ("pid", "nombre", "estado", "cpu%", "mem_mb")
        self.tree = ttk.Treeview(tbl_frame, columns=cols, show="headings", selectmode="browse")
        style = ttk.Style()
        style.configure("Treeview", background=BG2, foreground=TEXT,
                         fieldbackground=BG2, rowheight=22, font=FONT_UI)
        style.configure("Treeview.Heading", background=BG3, foreground=ACCENT,
                         font=(FONT_UI[0], FONT_UI[1], "bold"))
        style.map("Treeview", background=[("selected", "#1c2a3a")], foreground=[("selected", ACCENT)])

        hdrs = [("pid", "PID", 70), ("nombre", "Proceso", 280),
                ("estado", "Estado", 90), ("cpu%", "CPU %", 70), ("mem_mb", "Mem (MB)", 80)]
        for col, txt, w_ in hdrs:
            self.tree.heading(col, text=txt, command=lambda c=col: self._sort(c))
            self.tree.column(col, width=w_, stretch=(col == "nombre"), anchor="w" if col == "nombre" else "center")

        sb = ttk.Scrollbar(tbl_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # Botón terminar
        bot = tk.Frame(w, bg=BG, pady=8, padx=10)
        bot.pack(fill="x")
        styled_button(bot, "Terminar proceso seleccionado", self._kill_process, color=DANGER, fg="white").pack(side="left")
        self.status_lbl = label(bot, "", fg=TEXT_DIM)
        self.status_lbl.pack(side="left", padx=12)

        self._sort_col = "pid"
        self._sort_rev = False
        self._procs = []
        self._refresh()

    def _refresh(self):
        flt = self.filter_var.get().lower()
        self._procs = []
        for p in psutil.process_iter(["pid", "name", "status", "cpu_percent", "memory_info"]):
            try:
                info = p.info
                if flt and flt not in info["name"].lower():
                    continue
                mem = round(info["memory_info"].rss / 1024 / 1024, 1) if info["memory_info"] else 0
                self._procs.append((info["pid"], info["name"], info["status"],
                                    info["cpu_percent"], mem))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        self._procs.sort(key=lambda r: r[["pid","nombre","estado","cpu%","mem_mb"].index(self._sort_col)],
                         reverse=self._sort_rev)
        for row in self.tree.get_children():
            self.tree.delete(row)
        for p in self._procs:
            self.tree.insert("", "end", values=p)
        self.count_lbl.config(text=f"{len(self._procs)} procesos")

    def _sort(self, col):
        cols = ["pid", "nombre", "estado", "cpu%", "mem_mb"]
        if self._sort_col == col:
            self._sort_rev = not self._sort_rev
        else:
            self._sort_col = col
            self._sort_rev = False
        self._refresh()

    def _kill_process(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Selección requerida", "Selecciona un proceso primero.")
            return
        pid = int(self.tree.item(sel[0], "values")[0])
        name = self.tree.item(sel[0], "values")[1]
        if not messagebox.askyesno("Confirmar", f"¿Terminar el proceso '{name}' (PID {pid})?"):
            return
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            self.status_lbl.config(text=f"OK  Proceso {pid} terminado.", fg=ACCENT2)
        except psutil.NoSuchProcess:
            self.status_lbl.config(text="Proceso ya no existe.", fg=WARNING)
        except psutil.AccessDenied:
            self.status_lbl.config(text="Acceso denegado.", fg=DANGER)
        self._refresh()

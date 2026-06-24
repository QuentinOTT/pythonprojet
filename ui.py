"""
ui.py — Application Desktop Tkinter (Partie 1)
Données  : REST Countries API (JSON public)
DB       : SQLite via db.py
Auteur   : Quentin Ott
"""
import threading
import tkinter as tk
from tkinter import ttk, messagebox, colorchooser

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import db
import api

BG      = "#1e1e2e"
SURFACE = "#313244"
FG      = "#cdd6f4"
ACCENT  = "#89b4fa"
RED     = "#f38ba8"
REGION_COLORS = ["#89b4fa","#a6e3a1","#fab387","#f38ba8","#cba6f7","#f9e2af","#94e2d5"]


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🌍 REST Countries Explorer")
        self.geometry("1200x760")
        self.configure(bg=BG)
        self.resizable(True, True)
        db.init_db()
        self._build_menu()
        self._build_header()
        self._build_body()
        self._build_statusbar()
        self._refresh_tree()
        if db.is_empty():
            self._download_async()

    def _build_menu(self):
        bar = tk.Menu(self)
        self.config(menu=bar)
        data = tk.Menu(bar, tearoff=0, bg=SURFACE, fg=FG)
        bar.add_cascade(label="Données", menu=data)
        data.add_command(label="📥 Télécharger les données",     command=self._download_async)
        data.add_command(label="🗑️  Effacer la base de données", command=self._ask_clear)
        data.add_separator()
        data.add_command(label="❌ Quitter", command=self.destroy)
        opt = tk.Menu(bar, tearoff=0, bg=SURFACE, fg=FG)
        bar.add_cascade(label="Options", menu=opt)
        opt.add_command(label="🎨 Couleur de fond",  command=self._pick_bg)
        opt.add_command(label="🔤 Police Helvetica", command=lambda: self._set_font("Helvetica"))
        opt.add_command(label="🔤 Police Courier",   command=lambda: self._set_font("Courier"))
        opt.add_command(label="🔤 Police Arial",     command=lambda: self._set_font("Arial"))

    def _build_header(self):
        hf = tk.Frame(self, bg=BG)
        hf.pack(fill=tk.X, padx=20, pady=(12, 0))
        tk.Label(hf, text="🌍 REST Countries Explorer",
                 font=("Helvetica", 20, "bold"), bg=BG, fg=ACCENT).pack(side=tk.LEFT)
        btn = dict(bg=ACCENT, fg=BG, font=("Helvetica", 10, "bold"),
                   relief=tk.FLAT, padx=10, pady=5, cursor="hand2")
        tk.Button(hf, text="📥 Télécharger",  command=self._download_async, **btn).pack(side=tk.RIGHT, padx=4)
        tk.Button(hf, text="📊 Statistiques", command=self._show_stats,     **btn).pack(side=tk.RIGHT, padx=4)
        tk.Button(hf, text="📈 Graphique",    command=self._show_chart,     **btn).pack(side=tk.RIGHT, padx=4)
        tk.Button(hf, text="🗑️  Effacer DB",  command=self._ask_clear,
                  bg=RED, fg=BG, font=("Helvetica", 10, "bold"),
                  relief=tk.FLAT, padx=10, pady=5, cursor="hand2").pack(side=tk.RIGHT, padx=4)

    def _build_body(self):
        body = tk.Frame(self, bg=BG)
        body.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        left = tk.Frame(body, bg=BG)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tk.Label(left, text="Base de données", font=("Helvetica", 11, "bold"),
                 bg=BG, fg=FG).pack(anchor="w")

        sty = ttk.Style()
        sty.theme_use("clam")
        sty.configure("Treeview",         background=SURFACE, foreground=FG,
                       rowheight=24, fieldbackground=SURFACE, font=("Helvetica", 10))
        sty.configure("Treeview.Heading", background="#45475a", foreground=ACCENT,
                       font=("Helvetica", 10, "bold"))
        sty.map("Treeview", background=[("selected", "#45475a")])

        cols = ("Pays", "Région", "Population", "Superficie km²")
        self.tree = ttk.Treeview(left, columns=cols, show="headings", height=22)
        for col, w in zip(cols, [160, 120, 120, 130]):
            self.tree.heading(col, text=col, command=lambda c=col: self._sort_tree(c))
            self.tree.column(col, width=w, anchor="center")

        vsb = ttk.Scrollbar(left, orient="vertical",   command=self.tree.yview)
        hsb = ttk.Scrollbar(left, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side=tk.RIGHT,  fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)

        sf = tk.Frame(left, bg=BG)
        sf.pack(fill=tk.X, pady=(6, 0))
        tk.Label(sf, text="🔍 Rechercher :", bg=BG, fg=FG,
                 font=("Helvetica", 10)).pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._filter_tree())
        tk.Entry(sf, textvariable=self.search_var, bg=SURFACE, fg=FG,
                 insertbackground=FG, width=28, relief=tk.FLAT).pack(side=tk.LEFT, padx=6)

        right = tk.Frame(body, bg=BG, width=430)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(14, 0))
        right.pack_propagate(False)
        tk.Label(right, text="Résumé & Graphique", font=("Helvetica", 11, "bold"),
                 bg=BG, fg=FG).pack(anchor="w")

        self.stats_txt = tk.Text(right, height=10, bg=SURFACE, fg=FG,
                                 font=("Courier", 10), relief=tk.FLAT,
                                 state=tk.DISABLED, wrap=tk.WORD, padx=8, pady=8)
        self.stats_txt.pack(fill=tk.X, pady=(0, 8))

        self.chart_frame = tk.Frame(right, bg=BG)
        self.chart_frame.pack(fill=tk.BOTH, expand=True)

    def _build_statusbar(self):
        self.status_var = tk.StringVar(value="Prêt.")
        tk.Label(self, textvariable=self.status_var, anchor=tk.W,
                 bg="#45475a", fg=FG, font=("Helvetica", 9),
                 padx=6, relief=tk.SUNKEN).pack(side=tk.BOTTOM, fill=tk.X)

    def _set_status(self, msg):
        self.status_var.set(msg)
        self.update_idletasks()

    def _refresh_tree(self, rows=None):
        for item in self.tree.get_children():
            self.tree.delete(item)
        if rows is None:
            rows = db.fetch_all()
        for r in rows:
            self.tree.insert("", tk.END, values=(r[0], r[1], f"{r[2]:,}", f"{r[3]:,.1f}"))

    def _filter_tree(self):
        q = self.search_var.get().lower()
        rows = [r for r in db.fetch_all() if q in r[0].lower() or q in r[1].lower()]
        self._refresh_tree(rows)

    def _sort_tree(self, col):
        idx = {"Pays": 0, "Région": 1, "Population": 2, "Superficie km²": 3}.get(col, 0)
        rows = sorted(db.fetch_all(),
                      key=lambda r: (r[idx] or 0) if idx >= 2 else str(r[idx]).lower())
        self._refresh_tree(rows)

    def _download_async(self):
        if not db.is_empty():
            ans = messagebox.askyesno(
                "Base non vide",
                "La base contient déjà des données.\nVoulez-vous les remplacer ?"
            )
            if not ans:
                self._set_status("Téléchargement annulé.")
                return
        else:
            ans = True
        
        self._set_status("⏳ Téléchargement en cours…")
        threading.Thread(target=self._download_worker, args=(ans,), daemon=True).start()

    def _download_worker(self, replace_data):
        try:
            if replace_data:
                db.clear()
            rows = api.download_countries()
            db.insert_many(rows)
            self.after(0, self._download_success, rows)
        except Exception as exc:
            self.after(0, self._download_error, exc)

    def _download_success(self, rows):
        self._refresh_tree()
        self._set_status(f"✅ {len(rows)} pays téléchargés et enregistrés.")
        messagebox.showinfo("Succès", f"{len(rows)} pays enregistrés dans la base.")

    def _download_error(self, exc):
        self._set_status(f"❌ Erreur : {exc}")
        messagebox.showerror("Erreur", str(exc))

    def _ask_clear(self):
        if messagebox.askyesno("Confirmer", "Effacer toutes les données ?"):
            db.clear()
            self._refresh_tree()
            self._write_stats("Base effacée.")
            for w in self.chart_frame.winfo_children():
                w.destroy()
            self._set_status("🗑️ Base effacée.")

    def _show_stats(self):
        if db.is_empty():
            messagebox.showwarning("Base vide", "Téléchargez d'abord des données.")
            return
        total = db.total_population()
        avg   = db.avg_population()
        n     = len(db.fetch_all())
        lines = [
            f"📌 Pays enregistrés   : {n}",
            f"👥 Population totale  : {total:,.0f}",
            f"📊 Population moyenne : {avg:,.0f}",
            "",
            "🌐 Population par région :"
        ]
        for reg, pop in db.population_by_region():
            lines.append(f"  • {reg:<14} {pop:>15,.0f}")
        self._write_stats("\n".join(lines))
        self._set_status("📊 Statistiques SQL affichées.")

    def _write_stats(self, text):
        self.stats_txt.config(state=tk.NORMAL)
        self.stats_txt.delete("1.0", tk.END)
        self.stats_txt.insert(tk.END, text)
        self.stats_txt.config(state=tk.DISABLED)

    def _show_chart(self):
        if db.is_empty():
            messagebox.showwarning("Base vide", "Téléchargez d'abord des données.")
            return
        for w in self.chart_frame.winfo_children():
            w.destroy()
        data    = db.population_by_region()
        regions = [r[0] for r in data]
        pops    = [r[1] / 1e9 for r in data]
        colors  = REGION_COLORS[:len(regions)]
        fig = Figure(figsize=(5, 4.2), dpi=90, facecolor=BG)
        ax  = fig.add_subplot(111, facecolor=SURFACE)
        ax.barh(regions, pops, color=colors, edgecolor=BG, height=0.65)
        ax.set_xlabel("Population (milliards)", color=FG, fontsize=9)
        ax.set_title("Population par région", color=FG, fontsize=11, fontweight="bold")
        ax.tick_params(colors=FG, labelsize=8)
        for spine in ax.spines.values():
            spine.set_edgecolor("#45475a")
        fig.tight_layout(pad=1.2)
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self._set_status("📈 Graphique affiché.")

    def _pick_bg(self):
        color = colorchooser.askcolor(title="Couleur de fond")[1]
        if color:
            global BG
            old_bg = BG
            BG = color
            self.configure(bg=color)
            self._update_widget_bg(self, color, old_bg)
            self._set_status(f"🎨 Couleur de fond : {color}")

    def _update_widget_bg(self, widget, color, old_bg):
        if hasattr(widget, "configure"):
            try:
                bg_opt = widget.cget("bg")
                if bg_opt == old_bg:
                    widget.configure(bg=color)
            except Exception:
                pass
        for child in widget.winfo_children():
            self._update_widget_bg(child, color, old_bg)

    def _set_font(self, family):
        import tkinter.font as tkfont
        self._update_widget_font(self, family, tkfont)
        self._set_status(f"🔤 Police sélectionnée : {family}")

    def _update_widget_font(self, widget, family, tkfont):
        if isinstance(widget, ttk.Treeview):
            style = ttk.Style()
            style.configure("Treeview", font=(family, 10))
            style.configure("Treeview.Heading", font=(family, 10, "bold"))
        else:
            if hasattr(widget, "configure"):
                try:
                    current_font = widget.cget("font")
                    if current_font:
                        actual = tkfont.Font(font=current_font)
                        size = actual.actual("size")
                        weight = actual.actual("weight")
                        slant = actual.actual("slant")
                        widget.configure(font=(family, size, weight, slant))
                except Exception:
                    pass
        for child in widget.winfo_children():
            self._update_widget_font(child, family, tkfont)


if __name__ == "__main__":
    App().mainloop()
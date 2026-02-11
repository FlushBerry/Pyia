#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PYIA v0.1 - Pentest AI Helper
Interface modernisée, chat IA fonctionnel, auto-parse Nmap en temps réel.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import subprocess
import threading
import queue
import xml.etree.ElementTree as ET
import os
import math
import re
import json
import time

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


# ============================================================
#  Constantes de style
# ============================================================

FONT_MONO = ("Cascadia Code", 10)
FONT_MONO_BOLD = ("Cascadia Code", 10, "bold")
FONT_MONO_SM = ("Cascadia Code", 9)
FONT_UI = ("Segoe UI", 10)
FONT_UI_BOLD = ("Segoe UI", 10, "bold")
FONT_UI_SM = ("Segoe UI", 9)
FONT_UI_LG = ("Segoe UI", 12, "bold")
FONT_UI_TITLE = ("Segoe UI", 14, "bold")

CORNER_RADIUS = 8
PAD = 8
PAD_SM = 4
PAD_LG = 12


class PentestAIApp(tk.Tk):
    """Application principale PYIA v0.1."""

    def __init__(self):
        super().__init__()

        self.title("⚡ PYIA v0.1 — Pentest AI Helper")
        self.geometry("1500x900")
        self.minsize(1100, 700)

        # ── State ──
        self.output_queue = queue.Queue()
        self.terminal_transcript = ""
        self.cmd_history: list[str] = []
        self.cmd_history_index = 0
        self.cmd_history_queue: list[dict] = []
        self.last_cmd_text = ""
        self.last_cmd_output = ""

        # Graphique réseau
        self.hosts: dict[str, dict] = {}
        self.networks: dict[str, list] = {}
        self._host_counter = 0
        self.current_host_id = None
        self._host_positions: dict[str, tuple] = {}

        # Nmap auto-parse : file d'attente de commandes nmap en cours
        self._nmap_watch_active = True

        # API
        self.api_url = tk.StringVar(value="https://api.mammouth.ai/v1/chat/completions")
        self.api_model = tk.StringVar(value="gpt-4.1")
        self.api_key = tk.StringVar(value="")

        # Chat IA autonome (providers locaux/externes)
        self.ai_provider = tk.StringVar(value="ollama")
        self.ai_model = tk.StringVar(value="llama3.1")
        self.ai_api_key = tk.StringVar(value="")

        # Chat IA : historique de messages pour le contexte
        self._chat_messages: list[dict] = []

        # Chat IA autonome (providers locaux/externes)
        self.ai_provider = tk.StringVar(value="ollama")
        self.ai_model = tk.StringVar(value="llama3.1")
        self.ai_api_key = tk.StringVar(value="")

        # Profils
        self.profile_vars: dict[str, tk.BooleanVar] = {}
        self.profile_prompts = {
            "web": "Tu es spécialisé en pentest web (OWASP Top 10, auth bypass, injection SQL/XSS/SSTI, CSRF, SSRF, etc.).",
            "interne": "Tu es spécialisé en pentest interne (Active Directory, NTLM relay, Kerberoasting, mouvement latéral, post-exploitation).",
            "mobile": "Tu es spécialisé en pentest mobile (Android/iOS, reverse APK, interception API, stockage local, certificate pinning).",
            "infra": "Tu es spécialisé en pentest infra (scan réseau, services exposés, protocoles, firmware, IoT).",
            "opsec": "Tu aides à rester discret (OPSEC, rate-limiting, rotation de source, nettoyage de logs, évasion).",
        }

        # Thèmes modernes
        self.themes = {
            "Cyber Midnight": {
                "bg": "#05070c", "fg": "#e3f2ff", "accent": "#00bfff",
                "accent2": "#00a2ff", "surface": "#0b1220", "surface2": "#0f1828",
                "border": "#1b2a3c", "canvas_bg": "#05070c",
                "terminal_cmd": "#37c3ff", "terminal_ip": "#ff9f43",
                "terminal_uh": "#d86bff", "error": "#ff4d4d", "success": "#2dd36f",
                "muted": "#7e8ba3", "input_bg": "#0b1220",
            },
            "Hacker Neon": {
                "bg": "#030805", "fg": "#c7ffd9", "accent": "#3bff2f",
                "accent2": "#24ff6d", "surface": "#07110b", "surface2": "#0b1b12",
                "border": "#12301f", "canvas_bg": "#020603",
                "terminal_cmd": "#3bff2f", "terminal_ip": "#ff784f",
                "terminal_uh": "#4dd4ff", "error": "#ff4f6a", "success": "#35ff89",
                "muted": "#6fa080", "input_bg": "#0b1b12",
            },
            "Dracula Pro": {
                "bg": "#1b1a26", "fg": "#f8f8f2", "accent": "#ff7ac6",
                "accent2": "#c08bff", "surface": "#242635", "surface2": "#2d3040",
                "border": "#565a74", "canvas_bg": "#161621",
                "terminal_cmd": "#99e8ff", "terminal_ip": "#6bff9c",
                "terminal_uh": "#d0a6ff", "error": "#ff6b6b", "success": "#5cf38a",
                "muted": "#7a86b2", "input_bg": "#242635",
            },
            "Nord Aurora": {
                "bg": "#1d2330", "fg": "#e8f1f8", "accent": "#8fd3ff",
                "accent2": "#6ba6ff", "surface": "#253040", "surface2": "#2d3a4e",
                "border": "#3f5068", "canvas_bg": "#1a202d",
                "terminal_cmd": "#9fdcff", "terminal_ip": "#ffd76f",
                "terminal_uh": "#d8a9ff", "error": "#e57373", "success": "#a8e890",
                "muted": "#7b8aa6", "input_bg": "#253040",
            },
            "Solarized": {
                "bg": "#01212b", "fg": "#f2ead3", "accent": "#ffb400",
                "accent2": "#2aaaff", "surface": "#063746", "surface2": "#0b4558",
                "border": "#3d5560", "canvas_bg": "#021820",
                "terminal_cmd": "#33a8ff", "terminal_ip": "#ff7a3c",
                "terminal_uh": "#e655b5", "error": "#e24b4b", "success": "#97c13d",
                "muted": "#6f8c92", "input_bg": "#063746",
            },
        }
        self.theme_var = tk.StringVar(value="Cyber Midnight")

        # Liste de widgets texte pour appliquer le thème (renseignée lors de la construction)
        self.all_text_widgets: list[tk.Text] = []

        # ── Build UI ──
        self._build_ui()

        # Appliquer le thème après avoir recensé les widgets
        self.apply_theme()
        self.after(100, self._process_output_queue)

    # ============================================================
    #  UI CONSTRUCTION
    # ============================================================
    def _build_ui(self):
        """Construit toute l'interface."""
        # Menu bar
        self._build_menubar()

        # Status bar (bas)
        self._build_statusbar()

        # Notebook principal
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=PAD, pady=(PAD, 0))

        self.tab_terminal = ttk.Frame(self.notebook)
        self.tab_graph = ttk.Frame(self.notebook)
        self.tab_settings = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_terminal, text="  🖥  Terminal & IA  ")
        self.notebook.add(self.tab_graph, text="  🗺  Réseau  ")
        self.notebook.add(self.tab_settings, text="  ⚙  Paramètres  ")

        self._build_terminal_tab()
        self._build_graph_tab()
        self._build_settings_tab()

    def _build_menubar(self):
        menubar = tk.Menu(self, tearoff=0)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="💾  Sauvegarder projet", command=self.save_project,
                              accelerator="Ctrl+S")
        file_menu.add_command(label="📂  Charger projet", command=self.load_project,
                              accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="📄  Importer Nmap XML", command=self._import_nmap_xml)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.quit)
        menubar.add_cascade(label="Fichier", menu=file_menu)

        self.config(menu=menubar)
        self.bind_all("<Control-s>", lambda e: self.save_project())
        self.bind_all("<Control-o>", lambda e: self.load_project())

    def _build_statusbar(self):
        self.status_frame = tk.Frame(self, height=28)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_label = tk.Label(
            self.status_frame, text="  PYIA v0.1 — Prêt",
            anchor="w", font=FONT_UI_SM
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=PAD)

        self.hosts_count_label = tk.Label(
            self.status_frame, text="Hôtes : 0  |  Réseaux : 0",
            anchor="e", font=FONT_UI_SM
        )
        self.hosts_count_label.pack(side=tk.RIGHT, padx=PAD)

    def _update_status(self, text: str):
        self.status_label.config(text=f"  {text}")

    def _update_host_count(self):
        h = len(self.hosts)
        n = len(self.networks)
        self.hosts_count_label.config(text=f"Hôtes : {h}  |  Réseaux : {n}")

    # ──────────────────────────────────────
    #  TAB: Terminal & IA
    # ──────────────────────────────────────
    def _build_terminal_tab(self):
        main_pane = ttk.PanedWindow(self.tab_terminal, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=PAD_SM, pady=PAD_SM)

        # ── Colonne gauche : IA ──
        left = ttk.Frame(main_pane)
        left_pane = ttk.PanedWindow(left, orient=tk.VERTICAL)
        left_pane.pack(fill=tk.BOTH, expand=True)

        # Advisor
        advisor_frame = ttk.LabelFrame(left_pane, text="  🤖  Assistant IA — Analyse contextuelle  ")
        self._build_advisor_panel(advisor_frame)
        left_pane.add(advisor_frame, weight=3)

        # Chat
        chat_frame = ttk.LabelFrame(left_pane, text="  💬  Chat IA — Questions libres  ")
        self._build_chat_panel(chat_frame)
        left_pane.add(chat_frame, weight=2)

        # ── Colonne droite : Terminal ──
        right = ttk.LabelFrame(main_pane, text="  >_  Terminal  ")
        self._build_terminal_panel(right)

        main_pane.add(left, weight=2)
        main_pane.add(right, weight=3)

    def _build_advisor_panel(self, parent):
        # Profils checkboxes
        prof_bar = ttk.Frame(parent)
        prof_bar.pack(fill=tk.X, padx=PAD, pady=(PAD, PAD_SM))

        ttk.Label(prof_bar, text="Profils :", font=FONT_UI_BOLD).pack(side=tk.LEFT, padx=(0, PAD))

        for name in ["web", "interne", "mobile", "infra", "opsec"]:
            var = tk.BooleanVar(value=False)
            cb = ttk.Checkbutton(prof_bar, text=name.capitalize(), variable=var)
            cb.pack(side=tk.LEFT, padx=3)
            self.profile_vars[name] = var

        # Boutons
        btn_bar = ttk.Frame(parent)
        btn_bar.pack(fill=tk.X, padx=PAD, pady=(0, PAD_SM))

        ttk.Button(btn_bar, text="🔍  Analyser dernière commande",
                   command=self._on_advisor_button_click).pack(side=tk.LEFT, padx=(0, PAD_SM))
        ttk.Button(btn_bar, text="✏️  Modifier profils",
                   command=self._open_profile_editor).pack(side=tk.LEFT)

        # Zone texte
        self.advisor_text = scrolledtext.ScrolledText(parent, wrap=tk.WORD, font=FONT_MONO_SM)
        self.advisor_text.pack(fill=tk.BOTH, expand=True, padx=PAD, pady=(0, PAD))
        self._set_text_readonly(self.advisor_text)
        self.all_text_widgets.append(self.advisor_text)
        self._append_to_text(
            self.advisor_text,
            "🤖 Assistant IA prêt.\n"
            "→ Lance une commande, puis clique sur « Analyser dernière commande ».\n"
            "→ Coche les profils pour adapter les conseils.\n\n"
        )

    def _build_chat_panel(self, parent):
        # Zone historique chat IA (nouveau ScrolledText)
        self.ai_chat_display = scrolledtext.ScrolledText(parent, wrap=tk.WORD, font=FONT_MONO_SM)
        self.ai_chat_display.pack(fill=tk.BOTH, expand=True, padx=PAD, pady=(PAD, PAD_SM))
        self.ai_chat_display.config(state="disabled")
        self.ai_chat_display.tag_config("user", foreground="#5dade2")
        self.ai_chat_display.tag_config("assistant", foreground="#58d68d")
        self.all_text_widgets.append(self.ai_chat_display)
        # Alias pour compatibilité avec les fonctions existantes
        self.chat_history = self.ai_chat_display
        self._append_to_text(
            self.ai_chat_display,
            "💬 Chat IA prêt. Pose ta question ci-dessous.\n\n"
        )

        # Frame de saisie en bas du chat
        input_frame = ttk.Frame(parent)
        input_frame.pack(fill="x", padx=PAD, pady=(0, PAD))

        # Champ d'entrée (tk.Entry pour pouvoir styler bg/fg facilement)
        self.ai_input = tk.Entry(input_frame, font=("Consolas", 11))
        self.ai_input.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.ai_input.bind("<Return>", lambda e: self._send_ai_message())
        # Compat : réutiliser les anciennes références de champ de chat
        self.chat_entry = self.ai_input
        self._chat_placeholder_active = False
        self._ai_placeholder_active = True
        self._set_ai_placeholder()
        self.ai_input.bind("<FocusIn>", self._on_ai_focus_in)

        self.ai_send_btn = ttk.Button(input_frame, text="📤 Envoyer", command=self._send_ai_message)
        self.ai_send_btn.pack(side="right")

        # Obsolète : placeholder géré par _send_ai_message, plus de champ legacy

    def _build_terminal_panel(self, parent):
        # Shell selector
        shell_bar = ttk.Frame(parent)
        shell_bar.pack(fill=tk.X, padx=PAD, pady=(PAD, PAD_SM))

        ttk.Label(shell_bar, text="Shell :", font=FONT_UI_BOLD).pack(side=tk.LEFT, padx=(0, PAD))

        self.shell_var = tk.StringVar(value="bash")
        for s in ("bash", "zsh", "sh"):
            ttk.Radiobutton(shell_bar, text=s, variable=self.shell_var, value=s).pack(
                side=tk.LEFT, padx=3)

        # Terminal area
        self.terminal_output = scrolledtext.ScrolledText(
            parent, wrap=tk.WORD, font=FONT_MONO, state=tk.DISABLED
        )
        self.terminal_output.pack(fill=tk.BOTH, expand=True, padx=PAD, pady=(0, PAD_SM))
        self.all_text_widgets.append(self.terminal_output)

        # Command entry
        cmd_frame = ttk.Frame(parent)
        cmd_frame.pack(fill=tk.X, padx=PAD, pady=(0, PAD))

        prompt_label = tk.Label(cmd_frame, text=" $ ", font=FONT_MONO_BOLD)
        prompt_label.pack(side=tk.LEFT)
        self._prompt_label = prompt_label

        self.cmd_entry = tk.Entry(cmd_frame, font=FONT_MONO)
        self.cmd_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)
        self.cmd_entry.bind("<Return>", self._on_send_command)
        self.cmd_entry.bind("<Up>", self._on_history_up)
        self.cmd_entry.bind("<Down>", self._on_history_down)

        ttk.Button(cmd_frame, text="Exécuter ▶", command=self._on_send_command).pack(
            side=tk.LEFT, padx=(PAD_SM, 0))
        ttk.Button(cmd_frame, text="🗑  Clear", command=self._on_clear_terminal).pack(
            side=tk.LEFT, padx=(PAD_SM, 0))

    def _on_clear_terminal(self):
        self.terminal_output.config(state=tk.NORMAL)
        self.terminal_output.delete("1.0", tk.END)
        self.terminal_output.config(state=tk.DISABLED)
        self.terminal_transcript = ""
        self._update_status("Terminal vidé")

    def _on_clear_chat(self):
        self._chat_messages.clear()
        self.chat_history.config(state=tk.NORMAL)
        self.chat_history.delete("1.0", tk.END)
        self.chat_history.config(state=tk.DISABLED)
        self._append_to_text(self.chat_history, "💬 Chat vidé. Pose ta question ci-dessous.\n\n")

    # ──────────────────────────────────────
    #  TAB: Graphique Réseau
    # ──────────────────────────────────────
    def _build_graph_tab(self):
        graph_pane = ttk.PanedWindow(self.tab_graph, orient=tk.HORIZONTAL)
        graph_pane.pack(fill=tk.BOTH, expand=True, padx=PAD_SM, pady=PAD_SM)

        # Canvas
        canvas_frame = ttk.Frame(graph_pane)

        toolbar = ttk.Frame(canvas_frame)
        toolbar.pack(fill=tk.X, padx=PAD, pady=PAD_SM)

        ttk.Button(toolbar, text="📄  Importer Nmap XML",
                   command=self._import_nmap_xml).pack(side=tk.LEFT, padx=(0, PAD_SM))
        ttk.Button(toolbar, text="🔄  Rafraîchir",
                   command=self._update_network_graph).pack(side=tk.LEFT, padx=(0, PAD_SM))
        ttk.Button(toolbar, text="🗑  Tout effacer",
                   command=self._clear_graph_data).pack(side=tk.LEFT, padx=(0, PAD_SM))

        self.auto_parse_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(toolbar, text="Auto-parse Nmap",
                        variable=self.auto_parse_var).pack(side=tk.LEFT, padx=PAD)

        self.graph_canvas = tk.Canvas(canvas_frame, highlightthickness=0)
        self.graph_canvas.pack(fill=tk.BOTH, expand=True, padx=PAD, pady=(0, PAD))
        self.graph_canvas.bind("<Button-1>", self._on_canvas_click)
        self.graph_canvas.bind("<Configure>", lambda e: self._update_network_graph())

        graph_pane.add(canvas_frame, weight=3)

        # Détails hôte
        detail_outer = ttk.LabelFrame(graph_pane, text="  📋  Détails de l'hôte  ")
        graph_pane.add(detail_outer, weight=1)

        self.host_detail_text = scrolledtext.ScrolledText(
            detail_outer, wrap=tk.WORD, font=FONT_MONO_SM, height=12
        )
        self.host_detail_text.pack(fill=tk.BOTH, expand=True, padx=PAD, pady=(PAD, PAD_SM))
        self._set_text_readonly(self.host_detail_text)
        self.all_text_widgets.append(self.host_detail_text)

        # Propriétés éditables
        props = ttk.LabelFrame(detail_outer, text="  ✏️  Propriétés  ")
        props.pack(fill=tk.X, padx=PAD, pady=PAD_SM)

        ttk.Label(props, text="Nom d'hôte :").grid(row=0, column=0, sticky="w", padx=PAD_SM, pady=2)
        self.host_name_var = tk.StringVar()
        ttk.Entry(props, textvariable=self.host_name_var).grid(row=0, column=1, sticky="ew", padx=PAD_SM, pady=2)

        ttk.Label(props, text="OS :").grid(row=1, column=0, sticky="w", padx=PAD_SM, pady=2)
        self.os_choice_var = tk.StringVar(value="unknown")
        os_combo = ttk.Combobox(props, textvariable=self.os_choice_var,
                                values=["linux", "windows", "macos", "bsd", "network", "autre", "unknown"],
                                state="readonly")
        os_combo.grid(row=1, column=1, sticky="ew", padx=PAD_SM, pady=2)

        ttk.Label(props, text="Notes :").grid(row=2, column=0, sticky="w", padx=PAD_SM, pady=2)
        self.host_notes_var = tk.StringVar()
        ttk.Entry(props, textvariable=self.host_notes_var).grid(row=2, column=1, sticky="ew", padx=PAD_SM, pady=2)

        props.columnconfigure(1, weight=1)

        ttk.Button(detail_outer, text="💾  Sauvegarder modifications",
                   command=self._on_update_host_properties).pack(anchor="w", padx=PAD, pady=PAD)

    def _clear_graph_data(self):
        self.hosts.clear()
        self.networks.clear()
        self._host_counter = 0
        self.current_host_id = None
        self._update_network_graph()
        self._update_host_count()
        self._update_status("Données réseau effacées")

    # ──────────────────────────────────────
    #  TAB: Paramètres
    # ──────────────────────────────────────
    def _build_settings_tab(self):
        canvas = tk.Canvas(self.tab_settings, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.tab_settings, orient=tk.VERTICAL, command=canvas.yview)
        inner = ttk.Frame(canvas)

        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._settings_canvas = canvas

        # API
        api_frame = ttk.LabelFrame(inner, text="  🔑  Configuration API  ")
        api_frame.pack(fill=tk.X, padx=PAD_LG, pady=PAD_LG)

        labels = [("URL API :", self.api_url), ("Modèle :", self.api_model), ("Clé API :", self.api_key)]
        for i, (label, var) in enumerate(labels):
            ttk.Label(api_frame, text=label, font=FONT_UI).grid(
                row=i, column=0, sticky="w", padx=PAD, pady=PAD_SM)
            show = "*" if "Clé" in label else ""
            ttk.Entry(api_frame, textvariable=var, width=70, show=show).grid(
                row=i, column=1, sticky="ew", padx=PAD, pady=PAD_SM)
        api_frame.columnconfigure(1, weight=1)

        ttk.Button(api_frame, text="🧪  Tester la connexion",
                   command=self._test_api_connection).grid(
            row=len(labels), column=0, columnspan=2, sticky="w", padx=PAD, pady=PAD)

        # Thème
        theme_frame = ttk.LabelFrame(inner, text="  🎨  Thème  ")
        theme_frame.pack(fill=tk.X, padx=PAD_LG, pady=PAD_LG)

        theme_row = ttk.Frame(theme_frame)
        theme_row.pack(fill=tk.X, padx=PAD, pady=PAD)

        for tn in self.themes:
            t = self.themes[tn]
            rb = ttk.Radiobutton(theme_row, text=tn, variable=self.theme_var,
                                 value=tn, command=self.apply_theme)
            rb.pack(side=tk.LEFT, padx=PAD_SM)

    def _test_api_connection(self):
        if not HAS_REQUESTS:
            messagebox.showerror("Erreur", "Le module 'requests' n'est pas installé.\npip install requests")
            return

        key = self.api_key.get().strip()
        if not key:
            messagebox.showwarning("Attention", "Clé API vide.")
            return

        self._update_status("Test de connexion API en cours...")

        def _test():
            try:
                answer = self._call_mammouth_chat([
                    {"role": "system", "content": "Réponds OK."},
                    {"role": "user", "content": "Test de connexion. Réponds juste OK."}
                ])
                self.output_queue.put(("STATUS", f"✅ API OK : {answer[:100]}"))
            except Exception as e:
                self.output_queue.put(("STATUS", f"❌ Erreur API : {e}"))

        threading.Thread(target=_test, daemon=True).start()

    # ============================================================
    #  COMMANDES TERMINAL
    # ============================================================
    def _on_send_command(self, event=None):
        cmd = self.cmd_entry.get().strip()
        if not cmd:
            return

        self.cmd_entry.delete(0, tk.END)
        self.cmd_history.append(cmd)
        self.cmd_history_index = len(self.cmd_history)

        display = f"$ {cmd}\n"
        self._append_to_terminal(display, is_command=True)
        self.terminal_transcript += display

        start_index = len(self.terminal_transcript)
        self.cmd_history_queue.append({"cmd": cmd, "start_index": start_index})

        shell_path = self._find_shell(self.shell_var.get())
        if not shell_path:
            err = f"[ERREUR] Shell '{self.shell_var.get()}' introuvable.\n"
            self._append_to_terminal(err, is_command=False)
            self.terminal_transcript += err
            return

        self._update_status(f"Exécution : {cmd[:60]}...")
        threading.Thread(target=self._run_command_thread, args=(shell_path, cmd), daemon=True).start()

    def _on_history_up(self, event=None):
        if not self.cmd_history:
            return "break"
        if self.cmd_history_index > 0:
            self.cmd_history_index -= 1
        self.cmd_entry.delete(0, tk.END)
        self.cmd_entry.insert(0, self.cmd_history[self.cmd_history_index])
        return "break"

    def _on_history_down(self, event=None):
        if not self.cmd_history:
            return "break"
        if self.cmd_history_index < len(self.cmd_history) - 1:
            self.cmd_history_index += 1
            self.cmd_entry.delete(0, tk.END)
            self.cmd_entry.insert(0, self.cmd_history[self.cmd_history_index])
        else:
            self.cmd_history_index = len(self.cmd_history)
            self.cmd_entry.delete(0, tk.END)
        return "break"

    def _find_shell(self, name: str):
        for p in (f"/bin/{name}", f"/usr/bin/{name}", f"/usr/local/bin/{name}"):
            if os.path.exists(p):
                return p
        # Windows fallback
        if os.name == "nt":
            if name == "bash":
                wsl = r"C:\Windows\System32\bash.exe"
                if os.path.exists(wsl):
                    return wsl
            return os.environ.get("COMSPEC", "cmd.exe")
        return None

    def _run_command_thread(self, shell_path: str, cmd: str):
        try:
            if os.name == "nt" and "cmd" in shell_path.lower():
                proc = subprocess.Popen(
                    [shell_path, "/c", cmd],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, bufsize=1
                )
            else:
                proc = subprocess.Popen(
                    [shell_path, "-c", cmd],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, bufsize=1
                )
            for line in proc.stdout:
                self.output_queue.put(("OUT", line))
            proc.wait()
        except Exception as e:
            self.output_queue.put(("OUT", f"[ERREUR] {e}\n"))
        finally:
            self.output_queue.put(("DONE", cmd))

    # ============================================================
    #  OUTPUT QUEUE
    # ============================================================
    def _process_output_queue(self):
        try:
            while True:
                kind, payload = self.output_queue.get_nowait()

                if kind == "OUT":
                    self._append_to_terminal(payload, is_command=False)
                    self.terminal_transcript += payload

                elif kind == "DONE":
                    if self.cmd_history_queue:
                        entry = self.cmd_history_queue.pop(0)
                        cmd_text = entry["cmd"]
                        start_index = entry["start_index"]
                    else:
                        cmd_text = payload
                        start_index = 0

                    cmd_output = self.terminal_transcript[start_index:]
                    self.last_cmd_text = cmd_text
                    self.last_cmd_output = cmd_output

                    self._update_status(f"Terminé : {cmd_text[:60]}")

                    # Auto-parse nmap
                    if self.auto_parse_var.get():
                        self._maybe_parse_nmap_result(cmd_text, cmd_output)

                elif kind == "ADVISOR":
                    self._append_to_text(self.advisor_text, payload + "\n\n")

                elif kind == "CHAT":
                    self._append_to_text(self.chat_history, f"🤖 IA :\n{payload}\n\n")

                elif kind == "STATUS":
                    self._update_status(payload)

        except queue.Empty:
            pass

        self.after(80, self._process_output_queue)

    # ============================================================
    #  IA CONSEILLER (Advisor)
    # ============================================================
    def _on_advisor_button_click(self):
        if not self.last_cmd_text and not self.last_cmd_output:
            self.last_cmd_text = "(aucune commande)"
            self.last_cmd_output = self.terminal_transcript[-4000:]

        self._update_ai_advisor(self.last_cmd_text, self.last_cmd_output)

    def _update_ai_advisor(self, last_cmd: str, cmd_output: str):
        context = self.terminal_transcript[-8000:]
        profiles = [n for n, v in self.profile_vars.items() if v.get()]

        if self.api_key.get().strip() and HAS_REQUESTS:
            self._append_to_text(self.advisor_text, "⏳ Analyse IA en cours...\n")
            threading.Thread(
                target=self._advisor_ai_thread,
                args=(context, last_cmd, profiles),
                daemon=True
            ).start()
        else:
            advice = self._generate_ai_advice_stub(context, last_cmd, profiles)
            self.output_queue.put(("ADVISOR", advice))

    def _advisor_ai_thread(self, context: str, last_cmd: str, profiles: list):
        try:
            system_parts = [
                "Tu es un assistant expert en pentest / ethical hacking. "
                "Tu analyses le terminal d'un pentesteur et tu donnes des conseils "
                "pertinents, techniques et actionnables. Réponds en français. "
                "Structure ta réponse avec des sections claires."
            ]
            for prof in profiles:
                p = self.profile_prompts.get(prof, "")
                if p:
                    system_parts.append(p)

            messages = [
                {"role": "system", "content": "\n".join(system_parts)},
                {"role": "user", "content": (
                    f"Voici le contexte terminal (derniers 8000 chars) :\n"
                    f"```\n{context[-6000:]}\n```\n\n"
                    f"Dernière commande : `{last_cmd}`\n\n"
                    f"Analyse cette commande et sa sortie. Donne :\n"
                    f"1. Ce que tu observes (résultats importants)\n"
                    f"2. Les prochaines étapes recommandées\n"
                    f"3. Les commandes suggérées\n"
                    f"4. Les points d'attention (OPSEC, erreurs courantes)"
                )}
            ]

            answer = self._call_mammouth_chat(messages)
            self.output_queue.put(("ADVISOR", f"🤖 Analyse IA :\n{answer}"))
        except Exception as e:
            self.output_queue.put(("ADVISOR", f"❌ Erreur IA : {e}"))

    def _generate_ai_advice_stub(self, context: str, last_cmd: str, profiles: list):
        profiles_str = ", ".join(profiles) if profiles else "général"
        msg = [f"📋 Conseiller (mode hors-ligne) — profil {profiles_str}"]
        msg.append(f"Dernière commande : `{last_cmd}`\n")

        lc = last_cmd.lower()

        if "nmap" in lc:
            msg.append("🔍 Scan Nmap détecté :")
            msg.append("  → Pense à sauvegarder en XML (-oX) pour l'import graphique")
            if "-sV" not in lc and "-A" not in lc:
                msg.append("  → Ajoute `-sV` pour la détection de version")
            if "-sC" not in lc and "-A" not in lc:
                msg.append("  → Ajoute `-sC` pour les scripts NSE par défaut")
            if "--script vuln" not in lc:
                msg.append("  → Essaie `--script vuln` pour un scan de vulnérabilités")

        if any(x in lc for x in ("http", "curl", "wget", "gobuster", "dirb", "nikto", "ffuf")):
            msg.append("🌐 Phase d'énumération web :")
            msg.append("  → Vérifie les en-têtes de sécurité (X-Frame-Options, CSP, etc.)")
            msg.append("  → Teste les chemins courants (/admin, /api, /backup, etc.)")

        if any(x in lc for x in ("smb", "rpcclient", "smbclient", "impacket", "crackmapexec")):
            msg.append("🔐 Services SMB/AD :")
            msg.append("  → Vérifie les shares accessibles anonymement")
            msg.append("  → Teste null session et anonymous bind")

        if any(x in lc for x in ("ssh", "hydra", "medusa", "patator")):
            msg.append("🔑 Authentification :")
            msg.append("  → Attention au verrouillage de compte (OPSEC)")
            msg.append("  → Essaie les credentials par défaut d'abord")

        msg.append("\n⚙️ Configure une clé API dans Paramètres pour l'analyse IA complète.")
        return "\n".join(msg)

    # ============================================================
    #  CHAT IA
    # ============================================================
    def _on_send_chat(self, event=None):
        if self._chat_placeholder_active:
            return

        question = self.chat_entry.get().strip()
        if not question:
            return

        self.chat_entry.delete(0, tk.END)
        self._append_to_text(self.chat_history, f"👤 Toi :\n{question}\n\n")

        if self.api_key.get().strip() and HAS_REQUESTS:
            self._append_to_text(self.chat_history, "⏳ Réflexion en cours...\n")
            threading.Thread(
                target=self._chat_ai_thread,
                args=(question,),
                daemon=True
            ).start()
        else:
            self.output_queue.put(("CHAT",
                                   "⚠️ Pas de clé API configurée.\n"
                                   "→ Va dans l'onglet Paramètres pour configurer l'API.\n"
                                   "→ Le chat IA nécessite une clé API valide."))

    def _chat_ai_thread(self, question: str):
        try:
            context_snippet = self.terminal_transcript[-4000:]

            system_msg = (
                "Tu es un assistant expert en cybersécurité et pentest. "
                "Tu aides un pentesteur pendant un engagement. "
                "Réponds en français, de manière technique et concise. "
                "Si pertinent, propose des commandes exactes à exécuter."
            )
            if context_snippet.strip():
                system_msg += (
                    f"\n\nVoici le contexte terminal récent du pentesteur :\n"
                    f"```\n{context_snippet[-3000:]}\n```"
                )

            # Ajouter le message utilisateur à l'historique
            self._chat_messages.append({"role": "user", "content": question})

            # Construire les messages pour l'API (garder les 20 derniers)
            messages = [{"role": "system", "content": system_msg}]
            messages.extend(self._chat_messages[-20:])

            answer = self._call_mammouth_chat(messages)

            # Sauvegarder la réponse dans l'historique
            self._chat_messages.append({"role": "assistant", "content": answer})

            self.output_queue.put(("CHAT", answer))

        except Exception as e:
            self.output_queue.put(("CHAT", f"❌ Erreur : {e}"))

    # ============================================================
    #  CHAT IA AUTONOME (providers multiples)
    # ============================================================
    def _send_ai_message(self):
        """Envoie le message utilisateur au chat IA autonome."""
        msg = self.ai_input.get().strip()
        if self._ai_placeholder_active:
            return
        if not msg:
            return

        # Affiche le message utilisateur
        self.ai_chat_display.config(state="normal")
        self.ai_chat_display.insert("end", f"\n🧑 Vous : {msg}\n", "user")
        self.ai_chat_display.config(state="disabled")
        self.ai_chat_display.see("end")

        # Vide le champ
        self.ai_input.delete(0, "end")
        self._set_ai_placeholder()

        # Appel IA dans un thread
        threading.Thread(target=self._query_ai, args=(msg,), daemon=True).start()

    def _query_ai(self, message: str):
        """Interroge l'IA selon le provider configuré."""
        try:
            provider = self.ai_provider.get() if hasattr(self, "ai_provider") else "ollama"
            response = ""

            if provider == "ollama":
                if not HAS_REQUESTS:
                    raise ImportError("Le module requests est requis pour interroger Ollama.")
                url = "http://localhost:11434/api/generate"
                model = self.ai_model.get() if hasattr(self, "ai_model") else "llama3.1"
                payload = {
                    "model": model,
                    "prompt": message,
                    "stream": False
                }
                r = requests.post(url, json=payload, timeout=120)
                if r.status_code == 200:
                    response = r.json().get("response", "Pas de réponse")
                else:
                    response = f"Erreur Ollama: {r.status_code}"

            elif provider == "openai":
                if not HAS_REQUESTS:
                    raise ImportError("Le module requests est requis pour interroger l'API OpenAI.")
                api_key = self.ai_api_key.get() if hasattr(self, "ai_api_key") else ""
                url = "https://api.openai.com/v1/chat/completions"
                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                payload = {
                    "model": "gpt-4",
                    "messages": [
                        {"role": "system", "content": "Tu es un assistant pentest expert en cybersécurité."},
                        {"role": "user", "content": message}
                    ]
                }
                r = requests.post(url, json=payload, headers=headers, timeout=120)
                if r.status_code == 200:
                    response = r.json()["choices"][0]["message"]["content"]
                else:
                    response = f"Erreur OpenAI: {r.status_code} - {r.text}"

            elif provider == "anthropic":
                if not HAS_REQUESTS:
                    raise ImportError("Le module requests est requis pour interroger l'API Anthropic.")
                api_key = self.ai_api_key.get() if hasattr(self, "ai_api_key") else ""
                url = "https://api.anthropic.com/v1/messages"
                headers = {
                    "x-api-key": api_key,
                    "content-type": "application/json",
                    "anthropic-version": "2023-06-01"
                }
                payload = {
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 4096,
                    "messages": [{"role": "user", "content": message}]
                }
                r = requests.post(url, json=payload, headers=headers, timeout=120)
                if r.status_code == 200:
                    response = r.json()["content"][0]["text"]
                else:
                    response = f"Erreur Anthropic: {r.status_code} - {r.text}"
            else:
                response = "Provider IA non reconnu."

        except requests.exceptions.ConnectionError:
            response = "❌ Connexion impossible. Vérifiez que le service IA est démarré."
        except Exception as e:
            response = f"❌ Erreur: {str(e)}"

        # Affiche la réponse dans le chat (thread-safe)
        self.after(0, self._display_ai_response, response)

    def _display_ai_response(self, response: str):
        """Affiche la réponse IA dans le chat autonome."""
        self.ai_chat_display.config(state="normal")
        self.ai_chat_display.insert("end", f"\n🤖 IA : {response}\n", "assistant")
        self.ai_chat_display.config(state="disabled")
        self.ai_chat_display.see("end")

    def _set_ai_placeholder(self):
        """Affiche le placeholder dans le champ chat IA autonome."""
        self.ai_input.delete(0, tk.END)
        self.ai_input.insert(0, "Écris ton message pour l'IA…")
        self.ai_input.config(fg="#6c7a89")
        self._ai_placeholder_active = True

    def _on_ai_focus_in(self, event=None):
        if self._ai_placeholder_active:
            theme = self._current_theme()
            self.ai_input.delete(0, tk.END)
            self.ai_input.config(fg=theme["fg"])
            self._ai_placeholder_active = False

    # ============================================================
    #  APPEL API MAMMOUTH AI
    # ============================================================
    def _call_mammouth_chat(self, messages: list) -> str:
        url = self.api_url.get().strip()
        key = self.api_key.get().strip()
        model = self.api_model.get().strip()

        if not url:
            raise ValueError("URL API vide.")
        if not key:
            raise ValueError("Clé API non renseignée.")
        if not model:
            raise ValueError("Modèle non renseigné.")

        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000,
        }

        resp = requests.post(url, headers=headers, json=data, timeout=90)
        resp.raise_for_status()
        j = resp.json()

        if "choices" in j and j["choices"]:
            content = j["choices"][0].get("message", {}).get("content", "")
            if content:
                return content

        return f"[Réponse brute] {json.dumps(j, indent=2)[:500]}"

    # ============================================================
    #  NMAP PARSING & GRAPHIQUE
    # ============================================================
    def _maybe_parse_nmap_result(self, cmd: str, cmd_output: str):
        if "nmap" not in cmd.lower():
            return

        hosts = self._parse_nmap_text_output(cmd_output)
        if not hosts:
            return

        count = 0
        for h in hosts:
            self._add_or_update_host(h)
            count += 1

        if count > 0:
            self._update_network_graph()
            self._update_host_count()
            self._update_status(f"🗺  {count} hôte(s) ajouté(s) au graphe réseau")

            # Auto-switch to graph tab si premier import
            if len(self.hosts) == count:
                self.notebook.select(self.tab_graph)

    def _parse_nmap_text_output(self, output: str) -> list:
        hosts = []
        current_header = None
        current_lines = []

        for line in output.splitlines():
            if line.startswith("Nmap scan report for"):
                if current_header is not None:
                    h = self._build_host_from_nmap_chunk(current_header, current_lines)
                    if h:
                        hosts.append(h)
                current_header = line
                current_lines = []
            else:
                if current_header is not None:
                    current_lines.append(line)

        if current_header is not None:
            h = self._build_host_from_nmap_chunk(current_header, current_lines)
            if h:
                hosts.append(h)

        return hosts

    def _build_host_from_nmap_chunk(self, header: str, lines: list) -> dict | None:
        m = re.match(r"Nmap scan report for (.+)", header)
        if not m:
            return None

        target = m.group(1).strip()
        hostname = ""
        ip_str = ""

        # "hostname (ip)" format
        m2 = re.match(r"(.+?)\s*\(([\d\.]+)\)$", target)
        if m2:
            hostname = m2.group(1).strip()
            ip_str = m2.group(2).strip()
        elif re.match(r"^\d+\.\d+\.\d+\.\d+$", target):
            ip_str = target
        else:
            hostname = target

        # Parse ports
        ports = []
        in_ports = False
        os_lines = []
        in_os = False

        for line in lines:
            stripped = line.strip()

            if stripped.startswith("PORT"):
                in_ports = True
                in_os = False
                continue
            if stripped.startswith("OS details:") or stripped.startswith("Running:"):
                in_os = True
                in_ports = False
                os_lines.append(stripped)
                continue
            if stripped.startswith("Service Info:"):
                os_lines.append(stripped)
                continue

            if in_ports:
                if not stripped or not re.match(r"^\d+/(tcp|udp)", stripped):
                    if not stripped:
                        in_ports = False
                    continue
                parts = stripped.split()
                if len(parts) >= 3:
                    port_proto = parts[0]
                    state = parts[1]
                    service = parts[2]
                    version = " ".join(parts[3:]) if len(parts) > 3 else ""
                    pnum, proto = port_proto.split("/", 1)
                    ports.append({
                        "port": pnum, "proto": proto, "state": state,
                        "service": service, "version": version,
                        "raw": stripped
                    })

            if in_os:
                os_lines.append(stripped)

        # Déterminer OS
        os_name = "unknown"
        for ol in os_lines:
            if "OS details:" in ol:
                os_name = ol.split("OS details:", 1)[1].strip()
                break
            elif "Running:" in ol:
                os_name = ol.split("Running:", 1)[1].strip()

        # Heuristique OS par services
        if os_name == "unknown":
            services_str = " ".join(p["service"] + " " + p.get("version", "") for p in ports).lower()
            if any(x in services_str for x in ("microsoft", "ms-wbt", "netbios", "msrpc")):
                os_name = "Windows (heuristique)"
            elif any(x in services_str for x in ("openssh", "apache", "nginx", "linux")):
                os_name = "Linux (heuristique)"

        os_tag = self._infer_os_tag(os_name)
        network_id = self._compute_network_id(ip_str) if ip_str else "unknown"
        host_id = self._make_host_id(ip_str, hostname)

        raw_output = header + "\n" + "\n".join(lines)

        return {
            "id": host_id,
            "ip": ip_str,
            "hostname": hostname,
            "ports": ports,
            "raw_output": raw_output,
            "network": network_id,
            "os_name": os_name,
            "os_tag": os_tag,
            "notes": "",
        }

    def _infer_os_tag(self, os_name: str) -> str:
        low = (os_name or "").lower()
        if any(k in low for k in ("windows", "microsoft", "ms-")):
            return "windows"
        if any(k in low for k in ("linux", "unix", "ubuntu", "debian", "centos",
                                   "red hat", "fedora", "kali", "arch")):
            return "linux"
        if any(k in low for k in ("mac", "darwin", "apple", "ios")):
            return "macos"
        if any(k in low for k in ("freebsd", "openbsd", "netbsd")):
            return "bsd"
        if any(k in low for k in ("cisco", "juniper", "router", "switch", "mikrotik")):
            return "network"
        return "unknown"

    def _compute_network_id(self, ip_str: str) -> str:
        try:
            parts = ip_str.split(".")
            if len(parts) == 4:
                return f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
        except Exception:
            pass
        return "unknown"

    def _make_host_id(self, ip_str: str, hostname: str) -> str:
        if ip_str:
            return f"host_{ip_str}"
        if hostname:
            return f"host_{hostname}"
        self._host_counter += 1
        return f"host_{self._host_counter}"

    def _add_or_update_host(self, hdata: dict):
        host_id = hdata["id"]
        network_id = hdata.get("network", "unknown")

        if host_id in self.hosts:
            existing = self.hosts[host_id]
            # Merge ports
            existing_ports = {f"{p['port']}/{p['proto']}" for p in existing.get("ports", [])}
            for p in hdata.get("ports", []):
                key = f"{p['port']}/{p['proto']}"
                if key not in existing_ports:
                    existing.setdefault("ports", []).append(p)
            # Mettre à jour les infos non-vides
            if hdata.get("hostname") and not existing.get("hostname"):
                existing["hostname"] = hdata["hostname"]
            if hdata.get("os_name", "unknown") != "unknown" and existing.get("os_name", "unknown") == "unknown":
                existing["os_name"] = hdata["os_name"]
                existing["os_tag"] = hdata["os_tag"]
            if hdata.get("raw_output"):
                existing["raw_output"] = existing.get("raw_output", "") + "\n---\n" + hdata["raw_output"]
        else:
            self.hosts[host_id] = hdata
            self._host_counter += 1

        # Réseaux
        if network_id not in self.networks:
            self.networks[network_id] = []
        if host_id not in self.networks[network_id]:
            self.networks[network_id].append(host_id)

    # ============================================================
    #  DESSIN DU GRAPHE RÉSEAU
    # ============================================================
    def _update_network_graph(self):
        self.graph_canvas.delete("all")
        self._host_positions.clear()

        theme = self._current_theme()

        if not self.networks:
            self.graph_canvas.create_text(
                self.graph_canvas.winfo_width() / 2,
                self.graph_canvas.winfo_height() / 2,
                text="🗺  Aucun hôte détecté\n\n"
                     "→ Lance un scan nmap dans le terminal\n"
                     "→ Ou importe un fichier XML\n\n"
                     "L'auto-parse ajoutera les hôtes automatiquement.",
                fill=theme["muted"], font=FONT_UI_LG, justify="center"
            )
            return

        canvas_w = max(self.graph_canvas.winfo_width(), 600)
        canvas_h = max(self.graph_canvas.winfo_height(), 400)

        nets = sorted(self.networks.keys())
        n_nets = len(nets)

        margin = 25
        cols = max(1, math.ceil(math.sqrt(n_nets * canvas_w / max(canvas_h, 1))))
        rows = max(1, math.ceil(n_nets / cols))

        bubble_w = (canvas_w - margin * (cols + 1)) / cols
        bubble_h = (canvas_h - margin * (rows + 1)) / rows

        for idx, net in enumerate(nets):
            row = idx // cols
            col = idx % cols

            x0 = margin + col * (bubble_w + margin)
            y0 = margin + row * (bubble_h + margin)
            x1 = x0 + bubble_w
            y1 = y0 + bubble_h

            # Fond réseau (rectangle arrondi simulé)
            self._draw_rounded_rect(x0, y0, x1, y1,
                                    radius=12,
                                    fill=theme["surface"],
                                    outline=theme["border"],
                                    width=2)

            # Titre réseau
            self.graph_canvas.create_text(
                (x0 + x1) / 2, y0 + 16,
                text=f"🌐 {net}",
                font=FONT_UI_BOLD, fill=theme["accent"]
            )

            host_ids = self.networks[net]
            if not host_ids:
                continue

            inner_m = 20
            hx0 = x0 + inner_m
            hy0 = y0 + 35
            hx1 = x1 - inner_m
            hy1 = y1 - inner_m

            area_w = max(hx1 - hx0, 10)
            area_h = max(hy1 - hy0, 10)

            h_count = len(host_ids)
            cols_h = max(1, math.ceil(math.sqrt(h_count)))
            rows_h = max(1, math.ceil(h_count / cols_h))

            cell_w = area_w / cols_h
            cell_h = area_h / rows_h

            for i, host_id in enumerate(host_ids):
                hrow = i // cols_h
                hcol = i % cols_h

                cx = hx0 + (hcol + 0.5) * cell_w
                cy = hy0 + (hrow + 0.5) * cell_h

                host = self.hosts.get(host_id, {})
                os_tag = host.get("os_tag", "unknown")

                # Couleurs et icônes par OS
                os_styles = {
                    "windows": ("#0078d4", "#004578", "🪟"),
                    "linux":   ("#f5a623", "#c47d10", "🐧"),
                    "macos":   ("#a0a0a0", "#707070", "🍎"),
                    "bsd":     ("#9b59b6", "#6c3483", "😈"),
                    "network": ("#2ecc71", "#1a9c53", "📡"),
                    "unknown": (theme["accent"], theme["accent2"], "❓"),
                }
                fill_c, outline_c, icon = os_styles.get(os_tag, os_styles["unknown"])

                radius = min(cell_w, cell_h) * 0.28
                radius = max(radius, 10)
                radius = min(radius, 28)

                # Sélection
                is_selected = (host_id == self.current_host_id)
                outline_w = 3 if is_selected else 1
                sel_outline = theme["accent"] if is_selected else outline_c

                # Cercle hôte
                self.graph_canvas.create_oval(
                    cx - radius, cy - radius, cx + radius, cy + radius,
                    fill=fill_c, outline=sel_outline, width=outline_w
                )

                # Icône OS au centre
                self.graph_canvas.create_text(
                    cx, cy, text=icon, font=("TkDefaultFont", max(8, int(radius * 0.7)))
                )

                # Label
                n_ports = len(host.get("ports", []))
                label = host.get("hostname") or host.get("ip") or host_id
                if len(label) > 18:
                    label = label[:15] + "…"
                port_txt = f"({n_ports} ports)" if n_ports else ""

                self.graph_canvas.create_text(
                    cx, cy + radius + 12,
                    text=f"{label}\n{port_txt}",
                    fill=theme["fg"], font=("TkDefaultFont", 7), justify="center"
                )

                self._host_positions[host_id] = (cx, cy, radius)

    def _draw_rounded_rect(self, x0, y0, x1, y1, radius=10, **kwargs):
        """Dessine un rectangle arrondi sur le canvas."""
        r = radius
        points = [
            x0 + r, y0,
            x1 - r, y0,
            x1, y0,
            x1, y0 + r,
            x1, y1 - r,
            x1, y1,
            x1 - r, y1,
            x0 + r, y1,
            x0, y1,
            x0, y1 - r,
            x0, y0 + r,
            x0, y0,
        ]
        return self.graph_canvas.create_polygon(points, smooth=True, **kwargs)

    def _on_canvas_click(self, event):
        x, y = event.x, event.y
        clicked = None
        for host_id, (cx, cy, radius) in self._host_positions.items():
            if math.sqrt((x - cx) ** 2 + (y - cy) ** 2) <= radius + 8:
                clicked = host_id
                break

        if clicked:
            self._select_host(clicked)
        else:
            self.current_host_id = None
            self._update_network_graph()

    def _select_host(self, host_id: str):
        self.current_host_id = host_id
        host = self.hosts.get(host_id)
        if not host:
            return

        self.host_name_var.set(host.get("hostname", ""))
        self.os_choice_var.set(host.get("os_tag", "unknown"))
        self.host_notes_var.set(host.get("notes", ""))

        # Remplir le détail texte
        lines = []
        lines.append(f"{'═' * 40}")
        lines.append(f"  Hôte : {host.get('hostname') or host.get('ip') or host_id}")
        lines.append(f"{'═' * 40}")
        lines.append(f"  IP        : {host.get('ip') or '-'}")
        lines.append(f"  Hostname  : {host.get('hostname') or '-'}")
        lines.append(f"  Réseau    : {host.get('network')}")
        lines.append(f"  OS        : {host.get('os_name')}")
        lines.append(f"  Catégorie : {host.get('os_tag')}")
        lines.append(f"  Notes     : {host.get('notes') or '-'}")
        lines.append(f"{'─' * 40}")
        lines.append(f"  Ports ouverts ({len(host.get('ports', []))}) :")

        ports = host.get("ports") or []
        if not ports:
            lines.append("    (aucun)")
        else:
            for p in sorted(ports, key=lambda x: int(x.get("port", 0))):
                ver = p.get("version", "")
                ver_str = f" — {ver}" if ver else ""
                lines.append(
                    f"    {p['port']}/{p['proto']}  {p['state']:8s}  {p['service']}{ver_str}"
                )

        lines.append(f"{'─' * 40}")
        lines.append("  Extrait Nmap brut :")
        lines.append(host.get("raw_output") or "  (aucune donnée brute)")

        text = "\n".join(lines)
        self.host_detail_text.config(state=tk.NORMAL)
        self.host_detail_text.delete("1.0", tk.END)
        self.host_detail_text.insert(tk.END, text)
        self.host_detail_text.config(state=tk.DISABLED)
        self.host_detail_text.see("1.0")

        self._update_network_graph()

    def _on_update_host_properties(self):
        if not self.current_host_id:
            return
        host = self.hosts.get(self.current_host_id)
        if not host:
            return

        new_name = self.host_name_var.get().strip()
        host["hostname"] = new_name

        os_tag = self.os_choice_var.get()
        host["os_tag"] = os_tag
        host["os_name"] = {
            "linux": "Linux (manuel)",
            "windows": "Windows (manuel)",
            "unknown": host.get("os_name", "unknown"),
        }.get(os_tag, host.get("os_name", "unknown"))

        notes = self.host_notes_var.get().strip()
        host["notes"] = notes

        self._update_network_graph()
        self._select_host(self.current_host_id)

    def _on_delete_host(self):
        if not self.current_host_id:
            return
        host = self.hosts.get(self.current_host_id)
        if not host:
            return

        confirm = messagebox.askyesno(
            "Supprimer l'hôte",
            f"Supprimer l'hôte {host.get('hostname') or host.get('ip') or self.current_host_id} ?"
        )
        if not confirm:
            return

        net = host.get("network")
        if net and net in self.networks:
            if self.current_host_id in self.networks[net]:
                self.networks[net].remove(self.current_host_id)
            if not self.networks[net]:
                del self.networks[net]

        del self.hosts[self.current_host_id]
        self.current_host_id = None

        self.host_detail_text.config(state=tk.NORMAL)
        self.host_detail_text.delete("1.0", tk.END)
        self.host_detail_text.config(state=tk.DISABLED)
        self.host_name_var.set("")
        self.os_choice_var.set("unknown")
        self.host_notes_var.set("")

        self._update_network_graph()

    # =========================
    #  Import Nmap XML
    # =========================
    def _import_nmap_xml(self):
        """Ouvre un fichier Nmap XML et importe les hôtes."""
        return self._load_nmap_file()

    def _load_nmap_file(self):
        filetypes = [("Nmap XML", "*.xml"), ("Tous fichiers", "*.*")]
        filename = filedialog.askopenfilename(
            title="Sélectionne un fichier Nmap XML",
            filetypes=filetypes
        )
        if not filename:
            return

        try:
            tree = ET.parse(filename)
            root = tree.getroot()
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de parser le fichier XML :\n{e}")
            return

        count = 0
        for host_el in root.findall("host"):
            ip_str = ""
            for addr in host_el.findall("address"):
                if addr.get("addrtype") in ("ipv4", "ipv6"):
                    ip_str = addr.get("addr")
                    break

            hostname = ""
            hn = host_el.find("hostnames/hostname")
            if hn is not None:
                hostname = hn.get("name", "")

            ports_list = []
            for port_el in host_el.findall("ports/port"):
                state_el = port_el.find("state")
                service_el = port_el.find("service")
                port_num = port_el.get("portid", "")
                proto = port_el.get("protocol", "tcp")
                state = state_el.get("state", "") if state_el is not None else ""
                service = service_el.get("name", "") if service_el is not None else ""
                version = ""
                if service_el is not None:
                    product = service_el.get("product", "")
                    ver = service_el.get("version", "")
                    extra = service_el.get("extrainfo", "")
                    version = " ".join(filter(None, [product, ver, extra]))

                ports_list.append({
                    "port": port_num,
                    "proto": proto,
                    "state": state,
                    "service": service,
                    "version": version,
                    "raw": f"{port_num}/{proto} {state} {service} {version}".strip()
                })

            os_name = "unknown"
            os_tag = "unknown"
            osmatch = host_el.find("os/osmatch")
            if osmatch is not None:
                os_name = osmatch.get("name", "unknown")
                os_tag = self._infer_os_tag(os_name)

            if ip_str:
                parts = ip_str.split(".")
                if len(parts) == 4:
                    network_id = f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
                else:
                    network_id = "unknown_net"
            else:
                network_id = "unknown_net"

            raw_output = f"[Import XML] {hostname} ({ip_str}) - {len(ports_list)} port(s)"

            host_id = f"host_{self._host_counter}"
            self._host_counter += 1

            hdata = {
                "id": host_id,
                "ip": ip_str,
                "hostname": hostname,
                "ports": ports_list,
                "raw_output": raw_output,
                "network": network_id,
                "os_name": os_name,
                "os_tag": os_tag,
                "notes": "",
            }
            self._add_or_update_host(hdata)
            count += 1

        self._update_network_graph()
        messagebox.showinfo("Import terminé", f"{count} hôte(s) importé(s) depuis le fichier XML.")

    # =========================
    #  Éditeur de profils IA
    # =========================
    def _open_profile_editor(self):
        win = tk.Toplevel(self)
        win.title("Éditeur de profils IA")
        win.geometry("650x450")
        win.configure(bg=self._current_theme()["bg"])
        win.transient(self)
        win.grab_set()

        theme = self._current_theme()

        main_frame = ttk.Frame(win)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=PAD_LG, pady=PAD_LG)

        ttk.Label(main_frame, text="Profil à modifier :", font=FONT_UI_BOLD).pack(
            anchor="w", pady=(0, PAD_SM)
        )

        prof_names = list(self.profile_prompts.keys())
        prof_var = tk.StringVar(value=prof_names[0])

        combo = ttk.Combobox(main_frame, values=prof_names, textvariable=prof_var, state="readonly",
                             font=FONT_UI)
        combo.pack(fill=tk.X, pady=(0, PAD))

        ttk.Label(main_frame, text="Prompt système associé :", font=FONT_UI_BOLD).pack(
            anchor="w", pady=(0, PAD_SM)
        )

        prompt_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, font=FONT_MONO_SM,
                                                 height=12)
        prompt_text.pack(fill=tk.BOTH, expand=True, pady=(0, PAD))

        def load_prompt(*_):
            name = prof_var.get()
            prompt_text.delete("1.0", tk.END)
            prompt_text.insert("1.0", self.profile_prompts.get(name, ""))

        combo.bind("<<ComboboxSelected>>", load_prompt)
        load_prompt()

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(PAD_SM, 0))

        def save_prompt():
            name = prof_var.get()
            new_prompt = prompt_text.get("1.0", tk.END).strip()
            self.profile_prompts[name] = new_prompt
            messagebox.showinfo("Sauvegardé", f"Prompt du profil « {name} » mis à jour.", parent=win)

        ttk.Button(btn_frame, text="💾 Sauvegarder", command=save_prompt).pack(side=tk.LEFT, padx=(0, PAD))
        ttk.Button(btn_frame, text="Fermer", command=win.destroy).pack(side=tk.RIGHT)

    # =========================
    #  Sauvegarde / Chargement projet
    # =========================
    def save_project(self):
        filename = filedialog.asksaveasfilename(
            title="Sauvegarder le projet PYIA",
            defaultextension=".pyia",
            filetypes=[("Projet PYIA", "*.pyia"), ("JSON", "*.json"), ("Tous", "*.*")]
        )
        if not filename:
            return

        advisor_text = self.advisor_text.get("1.0", tk.END)
        chat_text = self.chat_history.get("1.0", tk.END)

        project = {
            "version": "2.0",
            "hosts": self.hosts,
            "networks": self.networks,
            "terminal_transcript": self.terminal_transcript,
            "profile_prompts": self.profile_prompts,
            "theme": self.theme_var.get(),
            "advisor_history": advisor_text,
            "chat_history": chat_text,
            "chat_messages": self._chat_messages,
            "api_url": self.api_url.get(),
            "api_model": self.api_model.get(),
        }

        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(project, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("Projet sauvegardé", f"Sauvegardé dans :\n{filename}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de sauvegarder :\n{e}")

    def load_project(self):
        filename = filedialog.askopenfilename(
            title="Charger un projet PYIA",
            filetypes=[("Projet PYIA", "*.pyia"), ("JSON", "*.json"), ("Tous", "*.*")]
        )
        if not filename:
            return

        try:
            with open(filename, "r", encoding="utf-8") as f:
                project = json.load(f)
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger :\n{e}")
            return

        self.hosts = project.get("hosts", {})
        self.networks = project.get("networks", {})
        self.terminal_transcript = project.get("terminal_transcript", "")
        self.profile_prompts = project.get("profile_prompts", self.profile_prompts)
        self._chat_messages = project.get("chat_messages", [])

        if project.get("api_url"):
            self.api_url.set(project["api_url"])
        if project.get("api_model"):
            self.api_model.set(project["api_model"])

        theme_name = project.get("theme", self.theme_var.get())
        if theme_name in self.themes:
            self.theme_var.set(theme_name)

        # Recharger terminal
        self.terminal_output.config(state=tk.NORMAL)
        self.terminal_output.delete("1.0", tk.END)
        for line in self.terminal_transcript.splitlines(keepends=True):
            if line.startswith("$ "):
                self._append_to_terminal(line, is_command=True)
            else:
                self._append_to_terminal(line, is_command=False)
        self.terminal_output.config(state=tk.DISABLED)

        # Recharger IA advisor
        advisor_history = project.get("advisor_history", "")
        self.advisor_text.config(state=tk.NORMAL)
        self.advisor_text.delete("1.0", tk.END)
        self.advisor_text.insert("1.0", advisor_history)
        self.advisor_text.config(state=tk.DISABLED)

        # Recharger chat
        chat_history = project.get("chat_history", "")
        self.chat_history.config(state=tk.NORMAL)
        self.chat_history.delete("1.0", tk.END)
        self.chat_history.insert("1.0", chat_history)
        self.chat_history.config(state=tk.DISABLED)

        # Recalculer host counter
        self._host_counter = len(self.hosts)

        # Réappliquer
        self.apply_theme()
        self._update_network_graph()

        messagebox.showinfo("Projet chargé", f"Projet chargé depuis :\n{filename}")

    # =========================
    #  Thèmes & couleurs
    # =========================
    def apply_theme(self):
        """Applique le thème sélectionné à l'interface."""
        theme = self._current_theme()

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure("TFrame", background=theme["bg"])
        style.configure("TLabel", background=theme["bg"], foreground=theme["fg"])
        style.configure("TNotebook", background=theme["bg"])
        style.configure(
            "TNotebook.Tab",
            background=theme["surface"],
            foreground=theme["fg"],
            padding=6,
        )
        style.map("TNotebook.Tab", background=[("selected", theme["surface2"])])
        style.configure("TLabelframe", background=theme["bg"], foreground=theme["fg"])
        style.configure("TLabelframe.Label", background=theme["bg"], foreground=theme["fg"])
        style.configure("TButton", background=theme["surface"], foreground=theme["fg"])
        style.configure("TEntry", fieldbackground=theme["input_bg"], foreground=theme["fg"])
        style.configure("TCombobox", fieldbackground=theme["input_bg"], foreground=theme["fg"], background=theme["input_bg"])

        self.configure(bg=theme["bg"])

        # Text widgets
        for txt in self.all_text_widgets:
            try:
                txt.config(bg=theme["surface"], fg=theme["fg"], insertbackground=theme["fg"])
            except Exception:
                pass

        # Canvas et entrées tk.Entry (non ttk)
        self.graph_canvas.config(bg=theme.get("canvas_bg", theme["bg"]))
        self.cmd_entry.config(bg=theme["input_bg"], fg=theme["fg"], insertbackground=theme["fg"], relief="flat")
        self.chat_entry.config(bg=theme["input_bg"], fg=theme["fg"], insertbackground=theme["fg"], relief="flat")

        # Styles colorés du terminal
        self.terminal_output.tag_configure("cmd", foreground=theme.get("terminal_cmd", theme["accent"]))
        self.terminal_output.tag_configure("ip", foreground=theme.get("terminal_ip", theme["accent2"]))
        self.terminal_output.tag_configure("uh", foreground=theme.get("terminal_uh", theme["accent"]))

        # Rafraîchir le graphe avec les nouvelles couleurs
        self._update_network_graph()

    # =========================
    #  Helpers UI
    # =========================
    @staticmethod
    def _set_text_readonly(text_widget):
        text_widget.config(state=tk.DISABLED)

    @staticmethod
    def _set_text_normal(text_widget):
        text_widget.config(state=tk.NORMAL)

    def _append_to_text(self, text_widget, content: str):
        self._set_text_normal(text_widget)
        text_widget.insert(tk.END, content)
        text_widget.see(tk.END)
        self._set_text_readonly(text_widget)

    def _append_to_terminal(self, content: str, is_command: bool):
        self.terminal_output.config(state=tk.NORMAL)

        start_index = self.terminal_output.index("end-1c")
        self.terminal_output.insert(tk.END, content)
        end_index = self.terminal_output.index("end-1c")

        text = content

        if is_command:
            self.terminal_output.tag_add("cmd", start_index, end_index)

        # IPs
        ip_pattern = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
        for m in re.finditer(ip_pattern, text):
            ip_start = f"{start_index}+{m.start()}c"
            ip_end = f"{start_index}+{m.end()}c"
            self.terminal_output.tag_add("ip", ip_start, ip_end)

        # user@host
        uh_pattern = r"\b[\w\.-]+@[\w\.-]+\b"
        for m in re.finditer(uh_pattern, text):
            uh_start = f"{start_index}+{m.start()}c"
            uh_end = f"{start_index}+{m.end()}c"
            self.terminal_output.tag_add("uh", uh_start, uh_end)

        self.terminal_output.see(tk.END)
        self.terminal_output.config(state=tk.DISABLED)

    def _current_theme(self) -> dict:
        return self.themes.get(self.theme_var.get(), list(self.themes.values())[0])


if __name__ == "__main__":
    app = PentestAIApp()
    app.mainloop()

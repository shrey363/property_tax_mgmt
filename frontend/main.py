# ============================================================
#  Property Tax Management System
#  File: frontend/main.py
#  Description: Application entry point – Login window
# ============================================================

import tkinter as tk
from tkinter import ttk, messagebox
import hashlib
from db_config import execute_query, verify_connection

# ── Theme colours ──────────────────────────────────────────
BG_DARK      = "#f8fafc"
BG_CARD      = "#ffffff"
BG_FIELD     = "#f1f5f9"
ACCENT       = "#d97706"
ACCENT_HOVER = "#b45309"
TEXT_LIGHT   = "#1e293b"
TEXT_MUTED   = "#64748b"
DANGER       = "#ef4444"
SUCCESS      = "#10b981"
FONT_TITLE   = ("Georgia", 26, "bold")
FONT_LABEL   = ("Segoe UI", 10)
FONT_BUTTON  = ("Segoe UI", 10, "bold")
FONT_SMALL   = ("Segoe UI", 8)
# ───────────────────────────────────────────────────────────


class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Property Tax Management System – Login")
        self.geometry("480x580")
        self.resizable(False, False)
        self.configure(bg=BG_DARK)
        self._center_window(480, 580)
        self._build_ui()

    def _center_window(self, w, h):
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def _build_ui(self):
        # ── Header banner ──────────────────────────────────
        header = tk.Frame(self, bg=ACCENT, height=8)
        header.pack(fill="x")

        # ── Logo area ──────────────────────────────────────
        logo_frame = tk.Frame(self, bg=BG_DARK, pady=30)
        logo_frame.pack(fill="x")

        tk.Label(logo_frame, text="⚖", font=("Segoe UI Emoji", 48),
                 bg=BG_DARK, fg=ACCENT).pack()
        tk.Label(logo_frame, text="PROPERTY TAX",
                 font=("Georgia", 20, "bold"),
                 bg=BG_DARK, fg=TEXT_LIGHT).pack()
        tk.Label(logo_frame, text="MANAGEMENT SYSTEM",
                 font=("Georgia", 11),
                 bg=BG_DARK, fg=ACCENT).pack()
        tk.Label(logo_frame, text="Municipal Corporation Portal",
                 font=FONT_SMALL, bg=BG_DARK, fg=TEXT_MUTED).pack(pady=(4, 0))

        # ── Card ───────────────────────────────────────────
        card = tk.Frame(self, bg=BG_CARD, padx=40, pady=30,
                        highlightbackground=ACCENT,
                        highlightthickness=1)
        card.pack(padx=40, fill="x")

        tk.Label(card, text="Sign In", font=("Georgia", 16, "bold"),
                 bg=BG_CARD, fg=TEXT_LIGHT).grid(row=0, column=0,
                 columnspan=2, pady=(0, 20), sticky="w")

        # Username
        tk.Label(card, text="Username", font=FONT_LABEL,
                 bg=BG_CARD, fg=TEXT_MUTED).grid(row=1, column=0,
                 sticky="w", pady=(0, 4))
        self.username_var = tk.StringVar()
        username_entry = tk.Entry(card, textvariable=self.username_var,
                                  font=FONT_LABEL,
                                  bg=BG_FIELD, fg=TEXT_LIGHT,
                                  insertbackground=ACCENT,
                                  relief="flat", bd=6, width=28)
        username_entry.grid(row=2, column=0, columnspan=2,
                            sticky="ew", pady=(0, 14), ipady=6)

        # Password
        tk.Label(card, text="Password", font=FONT_LABEL,
                 bg=BG_CARD, fg=TEXT_MUTED).grid(row=3, column=0,
                 sticky="w", pady=(0, 4))
        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(card, textvariable=self.password_var,
                                       show="●", font=FONT_LABEL,
                                       bg=BG_FIELD, fg=TEXT_LIGHT,
                                       insertbackground=ACCENT,
                                       relief="flat", bd=6, width=28)
        self.password_entry.grid(row=4, column=0, columnspan=2,
                                 sticky="ew", pady=(0, 4), ipady=6)

        # Show/hide
        self.show_pw = tk.BooleanVar(value=False)
        tk.Checkbutton(card, text="Show password",
                       variable=self.show_pw,
                       command=self._toggle_pw,
                       bg=BG_CARD, fg=TEXT_MUTED,
                       activebackground=BG_CARD,
                       selectcolor=BG_FIELD,
                       font=FONT_SMALL).grid(row=5, column=0,
                       columnspan=2, sticky="w", pady=(0, 16))

        # Login button
        self.login_btn = tk.Button(card, text="LOGIN",
                                   font=FONT_BUTTON,
                                   bg=ACCENT, fg="#ffffff",
                                   activebackground=ACCENT_HOVER,
                                   relief="flat", bd=0,
                                   cursor="hand2",
                                   command=self._login)
        self.login_btn.grid(row=6, column=0, columnspan=2,
                            sticky="ew", ipady=10)

        # Status label
        self.status_var = tk.StringVar()
        self.status_lbl = tk.Label(card, textvariable=self.status_var,
                                   font=FONT_SMALL, bg=BG_CARD,
                                   fg=DANGER, wraplength=300)
        self.status_lbl.grid(row=7, column=0, columnspan=2, pady=(10, 0))

        # ── Footer ─────────────────────────────────────────
        footer = tk.Frame(self, bg=BG_DARK)
        footer.pack(fill="x", pady=12)
        tk.Label(footer,
                 text="Default: admin / admin123  |  clerk1 / Clerk@123",
                 font=FONT_SMALL, bg=BG_DARK, fg=TEXT_MUTED).pack()

        # Bind Enter key
        self.bind("<Return>", lambda e: self._login())
        username_entry.focus()

        # Check DB connectivity
        if not verify_connection():
            self.status_var.set(
                "⚠ Cannot reach database. Check db_config.py settings.")

    def _toggle_pw(self):
        self.password_entry.config(
            show="" if self.show_pw.get() else "●")

    def _login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        if not username or not password:
            self.status_var.set("Please enter username and password.")
            return

        pw_hash = hashlib.sha256(password.encode()).hexdigest()

        try:
            rows = execute_query(
                "SELECT user_id, full_name, role FROM users "
                "WHERE username=%s AND password_hash=%s AND is_active=1",
                (username, pw_hash),
                fetch=True
            )

            if not rows:
                self.status_var.set("❌ Invalid credentials. Please try again.")
                return

            user = rows[0]
            # Update last_login
            execute_query(
                "UPDATE users SET last_login=NOW() WHERE user_id=%s",
                (user["user_id"],)
            )
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to connect or login: {e}")
            return

        self.withdraw()
        from dashboard import DashboardWindow
        dash = DashboardWindow(self, user)
        dash.protocol("WM_DELETE_WINDOW", self._on_dash_close)

    def _on_dash_close(self):
        self.destroy()


if __name__ == "__main__":
    app = LoginWindow()
    app.mainloop()

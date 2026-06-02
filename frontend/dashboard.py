# ============================================================
#  Property Tax Management System
#  File: frontend/dashboard.py
#  Description: Main dashboard / navigation hub
# ============================================================

import tkinter as tk
from tkinter import ttk, messagebox
from db_config import execute_query

BG_DARK    = "#0f1923"
BG_CARD    = "#1a2535"
BG_SIDEBAR = "#111e2c"
ACCENT     = "#f0a500"
ACCENT2    = "#3dcc7e"
TEXT_LIGHT = "#e8edf3"
TEXT_MUTED = "#7a8fa6"
DANGER     = "#e05252"
FONT_H1    = ("Georgia", 18, "bold")
FONT_H2    = ("Georgia", 13, "bold")
FONT_BODY  = ("Segoe UI", 10)
FONT_SMALL = ("Segoe UI", 8)
FONT_BOLD  = ("Segoe UI", 10, "bold")


class DashboardWindow(tk.Toplevel):
    def __init__(self, parent, user: dict):
        super().__init__(parent)
        self.parent = parent
        self.user   = user
        self.title(f"PTMS Dashboard – {user['full_name']} ({user['role'].title()})")
        self.geometry("1100x680")
        self.configure(bg=BG_DARK)
        self._center()
        self._build()

    def _center(self):
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"1100x680+{(sw-1100)//2}+{(sh-680)//2}")

    # ─── Build layout ────────────────────────────────────
    def _build(self):
        # Top bar
        topbar = tk.Frame(self, bg=ACCENT, height=6)
        topbar.pack(fill="x")

        main = tk.Frame(self, bg=BG_DARK)
        main.pack(fill="both", expand=True)

        # Sidebar
        sidebar = tk.Frame(main, bg=BG_SIDEBAR, width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Content area
        self.content = tk.Frame(main, bg=BG_DARK)
        self.content.pack(side="left", fill="both", expand=True)

        self._build_sidebar(sidebar)
        self._show_home()

    def _build_sidebar(self, sidebar):
        # Logo
        tk.Label(sidebar, text="⚖ PTMS", font=("Georgia", 16, "bold"),
                 bg=BG_SIDEBAR, fg=ACCENT).pack(pady=(20, 4))
        tk.Label(sidebar, text="Municipal Corporation",
                 font=FONT_SMALL, bg=BG_SIDEBAR, fg=TEXT_MUTED).pack()

        ttk.Separator(sidebar, orient="horizontal").pack(fill="x", pady=14)

        # User info
        tk.Label(sidebar, text=f"👤 {self.user['full_name']}",
                 font=FONT_BOLD, bg=BG_SIDEBAR, fg=TEXT_LIGHT,
                 wraplength=180).pack(padx=12, anchor="w")
        role_color = ACCENT if self.user['role'] == 'admin' else ACCENT2
        tk.Label(sidebar, text=self.user['role'].upper(),
                 font=FONT_SMALL, bg=BG_SIDEBAR,
                 fg=role_color).pack(padx=12, anchor="w", pady=(0, 14))

        ttk.Separator(sidebar, orient="horizontal").pack(fill="x", pady=4)

        # Navigation items  (icon, label, command, required_roles)
        nav_items = [
            ("🏠", "Dashboard",        self._show_home,         None),
            ("🏘", "Properties",       self._show_properties,   None),
            ("👤", "Owners",           self._show_owners,       None),
            ("🗂", "Tax Records",      self._show_tax_records,  None),
            ("💳", "Payments",         self._show_payments,     None),
            ("📊", "Reports",          self._show_reports,      None),
            ("🔧", "Admin Panel",      self._show_admin,        ["admin"]),
        ]

        self.nav_buttons = []
        for icon, label, cmd, roles in nav_items:
            if roles and self.user["role"] not in roles:
                continue
            btn = tk.Button(
                sidebar,
                text=f"  {icon}  {label}",
                font=FONT_BODY,
                bg=BG_SIDEBAR, fg=TEXT_LIGHT,
                activebackground=BG_CARD,
                activeforeground=ACCENT,
                relief="flat", bd=0,
                anchor="w", cursor="hand2",
                command=cmd
            )
            btn.pack(fill="x", padx=8, pady=2, ipady=8)
            self.nav_buttons.append(btn)

        # Logout at bottom
        tk.Frame(sidebar, bg=BG_SIDEBAR).pack(fill="y", expand=True)
        ttk.Separator(sidebar, orient="horizontal").pack(fill="x", pady=4)
        tk.Button(sidebar, text="  🚪  Logout",
                  font=FONT_BODY, bg=BG_SIDEBAR, fg=DANGER,
                  activebackground=BG_CARD, relief="flat", bd=0,
                  anchor="w", cursor="hand2",
                  command=self._logout).pack(fill="x", padx=8,
                  pady=8, ipady=8)

    # ─── Navigation helpers ──────────────────────────────
    def _clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    def _page_header(self, icon, title, subtitle=""):
        hf = tk.Frame(self.content, bg=BG_CARD, padx=24, pady=14)
        hf.pack(fill="x")
        tk.Label(hf, text=f"{icon} {title}", font=FONT_H1,
                 bg=BG_CARD, fg=TEXT_LIGHT).pack(side="left")
        if subtitle:
            tk.Label(hf, text=subtitle, font=FONT_SMALL,
                     bg=BG_CARD, fg=TEXT_MUTED).pack(side="left", padx=12)
        tk.Frame(self.content, bg=ACCENT, height=2).pack(fill="x")

    # ─── Home / KPI cards ────────────────────────────────
    def _show_home(self):
        self._clear_content()
        self._page_header("🏠", "Dashboard", "Overview & Key Metrics")

        # KPI row
        kpi_frame = tk.Frame(self.content, bg=BG_DARK, pady=16)
        kpi_frame.pack(fill="x", padx=20)

        try:
            kpis = self._get_kpis()
            for i, (label, value, color) in enumerate(kpis):
                card = tk.Frame(kpi_frame, bg=BG_CARD, padx=18, pady=14,
                                highlightbackground=color, highlightthickness=2)
                card.grid(row=0, column=i, padx=8, sticky="nsew")
                kpi_frame.columnconfigure(i, weight=1)
                tk.Label(card, text=str(value), font=("Georgia", 22, "bold"),
                         bg=BG_CARD, fg=color).pack()
                tk.Label(card, text=label, font=FONT_SMALL,
                         bg=BG_CARD, fg=TEXT_MUTED).pack()

            # Recent payments table
            tk.Label(self.content, text="Recent Payments",
                     font=FONT_H2, bg=BG_DARK, fg=TEXT_LIGHT).pack(
                     anchor="w", padx=24, pady=(12, 4))
            self._build_treeview(
                self.content,
                columns=["Receipt", "Date", "Owner", "Property", "Amount", "Mode"],
                rows=self._get_recent_payments(),
                height=8
            )
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load dashboard: {e}")

    def _get_kpis(self):
        rows = execute_query(
            "SELECT COUNT(*) AS cnt FROM property WHERE is_active=1", fetch=True)
        props = rows[0]["cnt"] if rows else 0

        rows = execute_query(
            "SELECT COUNT(*) AS cnt FROM tax_record WHERE status IN ('Overdue','Pending')",
            fetch=True)
        defaulters = rows[0]["cnt"] if rows else 0

        rows = execute_query(
            "SELECT COALESCE(SUM(amount_paid),0) AS total FROM payment", fetch=True)
        collected = f"₹{rows[0]['total']:,.0f}" if rows else "₹0"

        rows = execute_query(
            "SELECT COUNT(*) AS cnt FROM tax_record WHERE status='Overdue'", fetch=True)
        overdue = rows[0]["cnt"] if rows else 0

        return [
            ("Total Properties",   props,      ACCENT),
            ("Total Collected",    collected,  ACCENT2),
            ("Defaulters",         defaulters, DANGER),
            ("Overdue Records",    overdue,    "#e07a52"),
        ]

    def _get_recent_payments(self):
        rows = execute_query(
            "SELECT pay.receipt_number, DATE(pay.payment_date) AS dt, "
            "CONCAT(o.first_name,' ',o.last_name) AS owner, "
            "p.property_number, pay.amount_paid, pay.payment_mode "
            "FROM payment pay "
            "JOIN tax_record t ON pay.tax_id=t.tax_id "
            "JOIN property p ON t.property_id=p.property_id "
            "JOIN owner o ON p.owner_id=o.owner_id "
            "ORDER BY pay.payment_date DESC LIMIT 10",
            fetch=True
        )
        return [[r["receipt_number"], r["dt"], r["owner"],
                 r["property_number"], f"₹{r['amount_paid']:,.2f}",
                 r["payment_mode"]] for r in rows]

    # ─── Properties page ─────────────────────────────────
    def _show_properties(self):
        self._clear_content()
        self._page_header("🏘", "Properties", "All registered properties")

        # Action bar
        actions = tk.Frame(self.content, bg=BG_DARK, pady=8)
        actions.pack(fill="x", padx=20)
        if self.user["role"] in ("admin", "clerk"):
            tk.Button(actions, text="+ Add Property",
                      font=FONT_BOLD, bg=ACCENT, fg=BG_DARK,
                      relief="flat", cursor="hand2",
                      command=self._add_property_form
                      ).pack(side="left", padx=(0, 8), ipady=4, ipadx=8)
            tk.Button(actions, text="❌ Delete Selected",
                      font=FONT_BOLD, bg=DANGER, fg=TEXT_LIGHT,
                      relief="flat", cursor="hand2",
                      command=self._delete_property
                      ).pack(side="left", padx=(0, 8), ipady=4, ipadx=8)

        # Search
        tk.Label(actions, text="Search:", font=FONT_BODY,
                 bg=BG_DARK, fg=TEXT_MUTED).pack(side="left")
        self.prop_search_var = tk.StringVar()
        se = tk.Entry(actions, textvariable=self.prop_search_var,
                      font=FONT_BODY, bg=BG_CARD, fg=TEXT_LIGHT,
                      insertbackground=ACCENT, relief="flat", bd=4, width=24)
        se.pack(side="left", padx=6, ipady=4)
        tk.Button(actions, text="🔍", font=FONT_BOLD, bg=BG_CARD,
                  fg=ACCENT, relief="flat", cursor="hand2",
                  command=self._search_properties).pack(side="left")

        try:
            rows = execute_query(
                "SELECT p.property_id, p.property_number, "
                "CONCAT(o.first_name,' ',o.last_name) AS owner, "
                "w.ward_name, p.property_type, p.area_sqft, "
                "p.annual_value, p.is_active "
                "FROM property p "
                "JOIN owner o ON p.owner_id=o.owner_id "
                "JOIN ward  w ON p.ward_id =w.ward_id "
                "ORDER BY p.property_number",
                fetch=True
            )
            data = [[r["property_number"], r["owner"], r["ward_name"],
                     r["property_type"], f"{r['area_sqft']:,.0f} sqft",
                     f"₹{r['annual_value']:,.0f}",
                     "Active" if r["is_active"] else "Inactive"] for r in rows]
            self.prop_tree = self._build_treeview(
                self.content,
                columns=["Prop #", "Owner", "Ward", "Type", "Area", "Annual Value", "Status"],
                rows=data, height=18
            )
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load properties: {e}")

    def _search_properties(self):
        q = self.prop_search_var.get().strip()
        try:
            rows = execute_query(
                "SELECT p.property_number, "
                "CONCAT(o.first_name,' ',o.last_name) AS owner, "
                "w.ward_name, p.property_type, p.area_sqft, p.annual_value, p.is_active "
                "FROM property p "
                "JOIN owner o ON p.owner_id=o.owner_id "
                "JOIN ward  w ON p.ward_id =w.ward_id "
                "WHERE p.property_number LIKE %s OR CONCAT(o.first_name, ' ', o.last_name) LIKE %s OR w.ward_name LIKE %s",
                (f"%{q}%", f"%{q}%", f"%{q}%"), fetch=True
            )
            data = [[r["property_number"], r["owner"], r["ward_name"],
                     r["property_type"], f"{r['area_sqft']:,.0f} sqft",
                     f"₹{r['annual_value']:,.0f}",
                     "Active" if r["is_active"] else "Inactive"] for r in rows]
            # refresh tree
            if hasattr(self, "prop_tree"):
                for item in self.prop_tree.get_children():
                    self.prop_tree.delete(item)
                for row in data:
                    self.prop_tree.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Database Error", f"Search failed: {e}")

    # ─── Add Property form ───────────────────────────────
    def _add_property_form(self):
        from forms import PropertyForm
        PropertyForm(self, self.user)

    # ─── Owners page ─────────────────────────────────────
    def _show_owners(self):
        self._clear_content()
        self._page_header("👤", "Owners", "Registered property owners")

        actions = tk.Frame(self.content, bg=BG_DARK, pady=8)
        actions.pack(fill="x", padx=20)
        if self.user["role"] in ("admin", "clerk"):
            tk.Button(actions, text="+ Add Owner",
                      font=FONT_BOLD, bg=ACCENT, fg=BG_DARK,
                      relief="flat", cursor="hand2",
                      command=self._add_owner_form
                      ).pack(side="left", ipady=4, ipadx=8)
            tk.Button(actions, text="❌ Delete Selected",
                      font=FONT_BOLD, bg=DANGER, fg=TEXT_LIGHT,
                      relief="flat", cursor="hand2",
                      command=self._delete_owner
                      ).pack(side="left", padx=8, ipady=4, ipadx=8)

        try:
            rows = execute_query(
                "SELECT owner_id, CONCAT(first_name,' ',last_name) AS name, "
                "email, phone, aadhar_number, "
                "DATE(created_at) AS since FROM owner ORDER BY last_name",
                fetch=True
            )
            data = [[r["owner_id"], r["name"], r["email"],
                     r["phone"], r["aadhar_number"], str(r["since"])] for r in rows]
            self.owner_tree = self._build_treeview(
                self.content,
                columns=["ID", "Name", "Email", "Phone", "Aadhar", "Since"],
                rows=data, height=20
            )
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load owners: {e}")

    def _add_owner_form(self):
        from forms import OwnerForm
        OwnerForm(self, self.user)

    # ─── Tax Records page ────────────────────────────────
    def _show_tax_records(self):
        self._clear_content()
        self._page_header("🗂", "Tax Records", "All tax demands")

        actions = tk.Frame(self.content, bg=BG_DARK, pady=8)
        actions.pack(fill="x", padx=20)
        if self.user["role"] in ("admin", "clerk"):
            tk.Button(actions, text="+ Generate Tax",
                      font=FONT_BOLD, bg=ACCENT, fg=BG_DARK,
                      relief="flat", cursor="hand2",
                      command=self._generate_tax_form
                      ).pack(side="left", ipady=4, ipadx=8)
            tk.Button(actions, text="⚠ Apply Penalties",
                      font=FONT_BOLD, bg=DANGER, fg=TEXT_LIGHT,
                      relief="flat", cursor="hand2",
                      command=self._apply_penalties
                      ).pack(side="left", padx=8, ipady=4, ipadx=8)
            tk.Button(actions, text="❌ Delete Selected",
                      font=FONT_BOLD, bg=DANGER, fg=TEXT_LIGHT,
                      relief="flat", cursor="hand2",
                      command=self._delete_tax_record
                      ).pack(side="left", padx=8, ipady=4, ipadx=8)

        try:
            rows = execute_query(
                "SELECT t.tax_id, p.property_number, t.financial_year, "
                "t.tax_amount, t.penalty_amount, t.rebate_amount, "
                "t.total_due, t.due_date, t.status "
                "FROM tax_record t "
                "JOIN property p ON t.property_id=p.property_id "
                "ORDER BY t.financial_year DESC, p.property_number",
                fetch=True
            )
            data = [[r["tax_id"], r["property_number"], r["financial_year"],
                     f"₹{r['tax_amount']:,.2f}", f"₹{r['penalty_amount']:,.2f}",
                     f"₹{r['rebate_amount']:,.2f}", f"₹{r['total_due']:,.2f}",
                     str(r["due_date"]), r["status"]] for r in rows]
            self.tax_tree = self._build_treeview(
                self.content,
                columns=["ID", "Property", "FY", "Tax", "Penalty",
                         "Rebate", "Total Due", "Due Date", "Status"],
                rows=data, height=18
            )
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load tax records: {e}")

    def _generate_tax_form(self):
        from forms import TaxGenerateForm
        TaxGenerateForm(self, self.user)

    def _apply_penalties(self):
        if not messagebox.askyesno("Confirm", "Apply 10% penalty to all overdue records?"):
            return
        from db_config import call_procedure
        try:
            out, _ = call_procedure("sp_apply_penalty", (0, ""))
            messagebox.showinfo("Done", f"{out[0]} records updated.\n{out[1]}")
            self._show_tax_records()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ─── Payments page ───────────────────────────────────
    def _show_payments(self):
        self._clear_content()
        self._page_header("💳", "Payments", "Payment records & history")

        actions = tk.Frame(self.content, bg=BG_DARK, pady=8)
        actions.pack(fill="x", padx=20)
        if self.user["role"] in ("admin", "clerk"):
            tk.Button(actions, text="+ Record Payment",
                      font=FONT_BOLD, bg=ACCENT2, fg=BG_DARK,
                      relief="flat", cursor="hand2",
                      command=self._record_payment_form
                      ).pack(side="left", ipady=4, ipadx=8)
            tk.Button(actions, text="❌ Delete Selected",
                      font=FONT_BOLD, bg=DANGER, fg=TEXT_LIGHT,
                      relief="flat", cursor="hand2",
                      command=self._delete_payment
                      ).pack(side="left", padx=8, ipady=4, ipadx=8)

        try:
            rows = execute_query(
                "SELECT pay.receipt_number, DATE(pay.payment_date) AS dt, "
                "p.property_number, t.financial_year, "
                "CONCAT(o.first_name,' ',o.last_name) AS owner, "
                "pay.amount_paid, pay.payment_mode, pay.transaction_ref "
                "FROM payment pay "
                "JOIN tax_record t ON pay.tax_id=t.tax_id "
                "JOIN property p ON t.property_id=p.property_id "
                "JOIN owner o ON p.owner_id=o.owner_id "
                "ORDER BY pay.payment_date DESC",
                fetch=True
            )
            data = [[r["receipt_number"], str(r["dt"]), r["property_number"],
                     r["financial_year"], r["owner"],
                     f"₹{r['amount_paid']:,.2f}", r["payment_mode"],
                     r["transaction_ref"] or "—"] for r in rows]
            self.pay_tree = self._build_treeview(
                self.content,
                columns=["Receipt", "Date", "Property", "FY", "Owner",
                         "Amount", "Mode", "Transaction Ref"],
                rows=data, height=20
            )
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load payments: {e}")

    def _record_payment_form(self):
        from forms import PaymentForm
        PaymentForm(self, self.user)

    # ─── Reports page ────────────────────────────────────
    def _show_reports(self):
        self._clear_content()
        self._page_header("📊", "Reports", "Analytics & Generated Reports")

        nb = ttk.Notebook(self.content)
        nb.pack(fill="both", expand=True, padx=16, pady=12)

        # Tab 1: Defaulters
        t1 = tk.Frame(nb, bg=BG_DARK)
        nb.add(t1, text=" ⚠ Defaulters ")
        self._report_defaulters(t1)

        # Tab 2: Ward-wise collection
        t2 = tk.Frame(nb, bg=BG_DARK)
        nb.add(t2, text=" 🗺 Ward Collection ")
        self._report_ward_collection(t2)

        # Tab 3: Annual revenue
        t3 = tk.Frame(nb, bg=BG_DARK)
        nb.add(t3, text=" 📅 Annual Revenue ")
        self._report_annual_revenue(t3)

    def _report_defaulters(self, parent):
        try:
            rows = execute_query(
                "SELECT property_number, owner_name, phone, ward_name, "
                "financial_year, total_due, penalty_amount, "
                "due_date, status, days_overdue FROM v_defaulters",
                fetch=True
            )
            data = [[r["property_number"], r["owner_name"], r["phone"],
                     r["ward_name"], r["financial_year"],
                     f"₹{r['total_due']:,.2f}", str(r["due_date"]),
                     r["status"], str(r["days_overdue"])] for r in rows]
            self._build_treeview(
                parent,
                columns=["Property", "Owner", "Phone", "Ward", "FY",
                         "Due", "Due Date", "Status", "Days Overdue"],
                rows=data, height=16
            )
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load defaulters: {e}")

    def _report_ward_collection(self, parent):
        try:
            rows = execute_query(
                "SELECT ward_number, ward_name, zone, officer_name, "
                "total_properties, total_demand, total_collected, outstanding "
                "FROM v_ward_collection_summary",
                fetch=True
            )
            data = [[r["ward_number"], r["ward_name"], r["zone"],
                     r["officer_name"], r["total_properties"],
                     f"₹{(r['total_demand'] or 0):,.2f}",
                     f"₹{(r['total_collected'] or 0):,.2f}",
                     f"₹{(r['outstanding'] or 0):,.2f}"] for r in rows]
            self._build_treeview(
                parent,
                columns=["Ward #", "Ward Name", "Zone", "Officer",
                         "Properties", "Total Demand", "Collected", "Outstanding"],
                rows=data, height=16
            )
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load ward collection: {e}")

    def _report_annual_revenue(self, parent):
        try:
            rows = execute_query(
                "SELECT financial_year, properties_assessed, gross_tax_demand, "
                "total_penalties, total_rebates, net_demand, total_collected, uncollected "
                "FROM v_annual_revenue",
                fetch=True
            )
            data = [[r["financial_year"], r["properties_assessed"],
                     f"₹{(r['gross_tax_demand'] or 0):,.2f}",
                     f"₹{(r['total_penalties'] or 0):,.2f}",
                     f"₹{(r['total_rebates'] or 0):,.2f}",
                     f"₹{(r['net_demand'] or 0):,.2f}",
                     f"₹{(r['total_collected'] or 0):,.2f}",
                     f"₹{(r['uncollected'] or 0):,.2f}"] for r in rows]
            self._build_treeview(
                parent,
                columns=["FY", "Properties", "Gross Tax", "Penalties",
                         "Rebates", "Net Demand", "Collected", "Uncollected"],
                rows=data, height=16
            )
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load annual revenue: {e}")

    # ─── Admin panel ─────────────────────────────────────
    def _show_admin(self):
        self._clear_content()
        self._page_header("🔧", "Admin Panel", "System administration")

        grid = tk.Frame(self.content, bg=BG_DARK, pady=16)
        grid.pack(fill="x", padx=20)

        buttons = [
            ("👥 Manage Users",     self._manage_users,  ACCENT),
            ("🏙 Manage Wards",     self._manage_wards,  ACCENT),
            ("🔄 Run Tax Calc",     self._run_tax_calc,  ACCENT2),
            ("⚠ Apply Penalties",  self._apply_penalties, DANGER),
        ]
        for i, (label, cmd, color) in enumerate(buttons):
            tk.Button(grid, text=label, font=FONT_BOLD,
                      bg=color, fg=BG_DARK,
                      activebackground=BG_CARD,
                      relief="flat", cursor="hand2",
                      command=cmd, width=20
                      ).grid(row=0, column=i, padx=8, ipady=12)

        # User list actions frame
        user_actions = tk.Frame(self.content, bg=BG_DARK)
        user_actions.pack(fill="x", padx=20, pady=(12, 4))

        tk.Label(user_actions, text="Registered Users",
                 font=FONT_H2, bg=BG_DARK, fg=TEXT_LIGHT).pack(side="left")

        tk.Button(user_actions, text="❌ Delete Selected User",
                  font=FONT_BOLD, bg=DANGER, fg=TEXT_LIGHT,
                  relief="flat", cursor="hand2",
                  command=self._delete_user
                  ).pack(side="right", ipady=2, ipadx=8)

        try:
            rows = execute_query(
                "SELECT user_id, username, full_name, role, email, "
                "IF(is_active,'Active','Inactive') AS status, "
                "DATE(last_login) AS last_login FROM users ORDER BY role, username",
                fetch=True
            )
            data = [[r["user_id"], r["username"], r["full_name"],
                     r["role"], r["email"], r["status"],
                     str(r["last_login"] or "Never")] for r in rows]
            self.user_tree = self._build_treeview(
                self.content,
                columns=["ID", "Username", "Full Name", "Role", "Email", "Status", "Last Login"],
                rows=data, height=10
            )
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load users: {e}")

    def _manage_users(self):
        from forms import UserForm
        UserForm(self, self.user)

    def _manage_wards(self):
        from forms import WardForm
        WardForm(self, self.user)

    def _run_tax_calc(self):
        from forms import TaxGenerateForm
        TaxGenerateForm(self, self.user)

    # ─── Reusable treeview builder ───────────────────────
    def _build_treeview(self, parent, columns, rows, height=10):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Treeview",
                        background=BG_CARD,
                        foreground=TEXT_LIGHT,
                        fieldbackground=BG_CARD,
                        rowheight=26,
                        font=("Segoe UI", 9))
        style.configure("Custom.Treeview.Heading",
                        background=BG_SIDEBAR,
                        foreground=ACCENT,
                        font=("Segoe UI", 9, "bold"),
                        relief="flat")
        style.map("Custom.Treeview",
                  background=[("selected", "#2a3f5f")],
                  foreground=[("selected", ACCENT)])

        frame = tk.Frame(parent, bg=BG_DARK)
        frame.pack(fill="both", expand=True, padx=16, pady=8)

        vsb = ttk.Scrollbar(frame, orient="vertical")
        hsb = ttk.Scrollbar(frame, orient="horizontal")

        tree = ttk.Treeview(frame, columns=columns, show="headings",
                            height=height,
                            yscrollcommand=vsb.set,
                            xscrollcommand=hsb.set,
                            style="Custom.Treeview")

        vsb.config(command=tree.yview)
        hsb.config(command=tree.xview)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, minwidth=80, width=110, anchor="center")

        for row in rows:
            tree.insert("", "end", values=row)

        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        tree.pack(fill="both", expand=True)
        return tree

    def _delete_property(self):
        if not hasattr(self, "prop_tree"):
            return
        selected = self.prop_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a property from the list.")
            return
        values = self.prop_tree.item(selected[0], "values")
        prop_num = values[0]
        
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete property '{prop_num}'?"):
            return
        
        try:
            execute_query("DELETE FROM property WHERE property_number = %s", (prop_num,))
            messagebox.showinfo("Success", f"Property '{prop_num}' deleted successfully.")
            self._show_properties()
        except Exception as e:
            messagebox.showerror("Error", f"Cannot delete property. It may have associated tax records or payments.\nDetail: {e}")

    def _delete_owner(self):
        if not hasattr(self, "owner_tree"):
            return
        selected = self.owner_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select an owner from the list.")
            return
        values = self.owner_tree.item(selected[0], "values")
        owner_id = values[0]
        owner_name = values[1]
        
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete owner '{owner_name}' (ID: {owner_id})?"):
            return
        
        try:
            execute_query("DELETE FROM owner WHERE owner_id = %s", (owner_id,))
            messagebox.showinfo("Success", f"Owner '{owner_name}' deleted successfully.")
            self._show_owners()
        except Exception as e:
            messagebox.showerror("Error", f"Cannot delete owner. They may have registered properties.\nDetail: {e}")

    def _delete_tax_record(self):
        if not hasattr(self, "tax_tree"):
            return
        selected = self.tax_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a tax record from the list.")
            return
        values = self.tax_tree.item(selected[0], "values")
        tax_id = values[0]
        prop_num = values[1]
        fy = values[2]
        
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete tax record for property '{prop_num}' (FY {fy})?"):
            return
        
        try:
            execute_query("DELETE FROM tax_record WHERE tax_id = %s", (tax_id,))
            messagebox.showinfo("Success", "Tax record deleted successfully.")
            self._show_tax_records()
        except Exception as e:
            messagebox.showerror("Error", f"Cannot delete tax record. It may have associated payments.\nDetail: {e}")

    def _delete_payment(self):
        if not hasattr(self, "pay_tree"):
            return
        selected = self.pay_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a payment record from the list.")
            return
        values = self.pay_tree.item(selected[0], "values")
        receipt = values[0]
        
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete payment '{receipt}'?"):
            return
        
        try:
            execute_query("DELETE FROM payment WHERE receipt_number = %s", (receipt,))
            messagebox.showinfo("Success", "Payment record deleted successfully.")
            self._show_payments()
        except Exception as e:
            messagebox.showerror("Error", f"Cannot delete payment. It may be blocked by trigger constraints.\nDetail: {e}")

    def _delete_user(self):
        if not hasattr(self, "user_tree"):
            return
        selected = self.user_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a user from the list.")
            return
        values = self.user_tree.item(selected[0], "values")
        user_id = values[0]
        username = values[1]
        
        if str(username) == self.user["username"]:
            messagebox.showerror("Error", "You cannot delete your own account.")
            return
            
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete user '{username}' (ID: {user_id})?"):
            return
        
        try:
            execute_query("DELETE FROM users WHERE user_id = %s", (user_id,))
            messagebox.showinfo("Success", f"User '{username}' deleted successfully.")
            self._show_admin()
        except Exception as e:
            messagebox.showerror("Error", f"Cannot delete user.\nDetail: {e}")

    def _logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.destroy()
            self.parent.deiconify()

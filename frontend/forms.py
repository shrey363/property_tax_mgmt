# ============================================================
#  Property Tax Management System
#  File: frontend/forms.py
#  Description: All data-entry forms (Add/Edit dialogs)
# ============================================================

import tkinter as tk
from tkinter import ttk, messagebox
from db_config import execute_query, call_procedure
import hashlib

BG_DARK    = "#0f1923"
BG_CARD    = "#1a2535"
BG_FIELD   = "#243040"
ACCENT     = "#f0a500"
ACCENT2    = "#3dcc7e"
TEXT_LIGHT = "#e8edf3"
TEXT_MUTED = "#7a8fa6"
DANGER     = "#e05252"
FONT_BODY  = ("Segoe UI", 10)
FONT_BOLD  = ("Segoe UI", 10, "bold")
FONT_LABEL = ("Segoe UI", 9)
FONT_SMALL = ("Segoe UI", 8)


# ── Base dialog ───────────────────────────────────────────
class BaseDialog(tk.Toplevel):
    def __init__(self, parent, title, width=520, height=600):
        super().__init__(parent)
        self.parent = parent
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.configure(bg=BG_DARK)
        self.resizable(False, False)
        self.grab_set()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{width}x{height}+{(sw-width)//2}+{(sh-height)//2}")

        # Top accent bar
        tk.Frame(self, bg=ACCENT, height=5).pack(fill="x")

    def _field(self, parent, label, row, var=None, widget_type="entry",
               options=None, required=False, col=0):
        """Helper to create label + input."""
        asterisk = " *" if required else ""
        tk.Label(parent, text=label + asterisk,
                 font=FONT_LABEL, bg=BG_CARD, fg=TEXT_MUTED
                 ).grid(row=row*2, column=col, sticky="w",
                        padx=10, pady=(8, 0))

        if widget_type == "entry":
            w = tk.Entry(parent, textvariable=var,
                         font=FONT_BODY, bg=BG_FIELD,
                         fg=TEXT_LIGHT, insertbackground=ACCENT,
                         relief="flat", bd=5)
            w.grid(row=row*2+1, column=col, sticky="ew",
                   padx=10, pady=(2, 0), ipady=5)
        elif widget_type == "combo":
            w = ttk.Combobox(parent, textvariable=var,
                             values=options or [],
                             font=FONT_BODY, state="readonly")
            w.grid(row=row*2+1, column=col, sticky="ew",
                   padx=10, pady=(2, 0), ipady=3)
            if options:
                w.set(options[0])
        elif widget_type == "text":
            w = tk.Text(parent, font=FONT_BODY, bg=BG_FIELD,
                        fg=TEXT_LIGHT, insertbackground=ACCENT,
                        relief="flat", bd=5, height=3, width=30)
            w.grid(row=row*2+1, column=col, sticky="ew",
                   padx=10, pady=(2, 0))
        return w

    def _save_btn(self, parent, cmd, label="💾 Save"):
        btn_frame = tk.Frame(parent, bg=parent["bg"])
        btn_frame.pack(fill="x", padx=10, pady=14)
        tk.Button(btn_frame, text=label, font=FONT_BOLD,
                  bg=ACCENT, fg=BG_DARK,
                  activebackground="#ffbf33",
                  relief="flat", cursor="hand2",
                  command=cmd).pack(side="right", ipady=6, ipadx=16)
        tk.Button(btn_frame, text="✕ Cancel", font=FONT_BODY,
                  bg=BG_DARK, fg=TEXT_MUTED,
                  relief="flat", cursor="hand2",
                  command=self.destroy).pack(side="right", padx=8,
                  ipady=6, ipadx=10)

    def _status(self, parent, text="", color=DANGER):
        self.status_var = tk.StringVar(value=text)
        lbl = tk.Label(parent, textvariable=self.status_var,
                       font=FONT_SMALL, bg=parent["bg"], fg=color,
                       wraplength=460)
        lbl.pack(padx=10, pady=4)
        return lbl


# ── Property Form ─────────────────────────────────────────
class PropertyForm(BaseDialog):
    def __init__(self, parent, user):
        super().__init__(parent, "Add New Property", width=540, height=720)
        self.user = user
        tk.Label(self, text="Register New Property",
                 font=("Georgia", 14, "bold"),
                 bg=BG_DARK, fg=TEXT_LIGHT).pack(pady=(12, 4))

        card = tk.Frame(self, bg=BG_CARD, padx=16, pady=10)
        card.pack(fill="both", expand=False, padx=16, pady=8)
        card.columnconfigure(0, weight=1)
        card.columnconfigure(1, weight=1)

        # Fields
        self.prop_num    = tk.StringVar()
        self.address_var = tk.StringVar()
        self.area_var    = tk.StringVar()
        self.value_var   = tk.StringVar()
        self.floors_var  = tk.StringVar(value="1")
        self.year_var    = tk.StringVar()
        self.type_var    = tk.StringVar()
        self.owner_var   = tk.StringVar()
        self.ward_var    = tk.StringVar()

        self._field(card, "Property Number", 0, self.prop_num, required=True)
        self._field(card, "Address",         1, self.address_var, required=True)
        self._field(card, "Area (sqft)",     2, self.area_var, required=True)
        self._field(card, "Annual Value (₹)",3, self.value_var, required=True)
        self._field(card, "Floors",          4, self.floors_var)
        self._field(card, "Construction Year",5, self.year_var, required=True)

        # Right column
        ptypes = ["Residential", "Commercial", "Industrial", "Agricultural"]
        self._field(card, "Property Type", 0, self.type_var,
                    "combo", ptypes, col=1)

        owners = execute_query(
            "SELECT owner_id, CONCAT(first_name,' ',last_name) AS n FROM owner ORDER BY n",
            fetch=True)
        self.owner_map = {r["n"]: r["owner_id"] for r in owners}
        self._field(card, "Owner", 1, self.owner_var,
                    "combo", list(self.owner_map.keys()), required=True, col=1)

        wards = execute_query(
            "SELECT ward_id, ward_name FROM ward ORDER BY ward_name", fetch=True)
        self.ward_map = {r["ward_name"]: r["ward_id"] for r in wards}
        self._field(card, "Ward", 2, self.ward_var,
                    "combo", list(self.ward_map.keys()), required=True, col=1)

        self._status(self)
        self._save_btn(self, self._save)

    def _save(self):
        try:
            prop_num  = self.prop_num.get().strip()
            address   = self.address_var.get().strip()
            area      = float(self.area_var.get())
            value     = float(self.value_var.get())
            floors    = int(self.floors_var.get())
            year      = int(self.year_var.get())
            ptype     = self.type_var.get()
            owner_id  = self.owner_map.get(self.owner_var.get())
            ward_id   = self.ward_map.get(self.ward_var.get())

            if not all([prop_num, address, ptype, owner_id, ward_id]):
                self.status_var.set("Please fill all required fields.")
                return

            execute_query(
                "INSERT INTO property (property_number, owner_id, ward_id, address, "
                "property_type, area_sqft, floors, construction_year, annual_value) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (prop_num, owner_id, ward_id, address,
                 ptype, area, floors, year, value)
            )
            messagebox.showinfo("Success", f"Property {prop_num} added successfully!")
            self.parent._show_properties()
            self.destroy()
        except ValueError:
            self.status_var.set("Area, value, floors and year must be numbers.")
        except Exception as e:
            self.status_var.set(str(e))


# ── Owner Form ────────────────────────────────────────────
class OwnerForm(BaseDialog):
    def __init__(self, parent, user):
        super().__init__(parent, "Add New Owner", width=520, height=660)
        self.user = user
        tk.Label(self, text="Register New Owner",
                 font=("Georgia", 14, "bold"),
                 bg=BG_DARK, fg=TEXT_LIGHT).pack(pady=(12, 4))

        card = tk.Frame(self, bg=BG_CARD, padx=16, pady=10)
        card.pack(fill="both", expand=False, padx=16, pady=8)
        card.columnconfigure(0, weight=1)

        self.fname_var  = tk.StringVar()
        self.lname_var  = tk.StringVar()
        self.email_var  = tk.StringVar()
        self.phone_var  = tk.StringVar()
        self.addr_var   = tk.StringVar()
        self.aadhar_var = tk.StringVar()
        self.pan_var    = tk.StringVar()

        self._field(card, "First Name",      0, self.fname_var,  required=True)
        self._field(card, "Last Name",       1, self.lname_var,  required=True)
        self._field(card, "Email",           2, self.email_var,  required=True)
        self._field(card, "Phone",           3, self.phone_var,  required=True)
        self._field(card, "Address",         4, self.addr_var,   required=True)
        self._field(card, "Aadhar Number",   5, self.aadhar_var, required=True)
        self._field(card, "PAN Number",      6, self.pan_var)

        self._status(self)
        self._save_btn(self, self._save)

    def _save(self):
        try:
            fname  = self.fname_var.get().strip()
            lname  = self.lname_var.get().strip()
            email  = self.email_var.get().strip()
            phone  = self.phone_var.get().strip()
            addr   = self.addr_var.get().strip()
            aadhar = self.aadhar_var.get().strip()
            pan    = self.pan_var.get().strip() or None

            if not all([fname, lname, email, phone, addr, aadhar]):
                self.status_var.set("Please fill all required fields.")
                return
            if len(aadhar) != 12 or not aadhar.isdigit():
                self.status_var.set("Aadhar must be exactly 12 digits.")
                return

            execute_query(
                "INSERT INTO owner (first_name, last_name, email, phone, "
                "address, aadhar_number, pan_number) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                (fname, lname, email, phone, addr, aadhar, pan)
            )
            messagebox.showinfo("Success", f"Owner {fname} {lname} added!")
            self.parent._show_owners()
            self.destroy()
        except Exception as e:
            self.status_var.set(str(e))


# ── Tax Generate Form ────────────────────────────────────
class TaxGenerateForm(BaseDialog):
    def __init__(self, parent, user):
        super().__init__(parent, "Generate Tax Record", width=460, height=460)
        self.user = user
        tk.Label(self, text="Generate / Recalculate Tax",
                 font=("Georgia", 14, "bold"),
                 bg=BG_DARK, fg=TEXT_LIGHT).pack(pady=(12, 4))

        card = tk.Frame(self, bg=BG_CARD, padx=16, pady=10)
        card.pack(fill="both", expand=False, padx=16, pady=8)
        card.columnconfigure(0, weight=1)

        props = execute_query(
            "SELECT property_id, property_number FROM property WHERE is_active=1 ORDER BY property_number",
            fetch=True)
        self.prop_map = {r["property_number"]: r["property_id"] for r in props}

        self.prop_var = tk.StringVar()
        self.fy_var   = tk.StringVar(value="2024-2025")
        self.due_var  = tk.StringVar(value="2024-07-31")

        self._field(card, "Property", 0, self.prop_var,
                    "combo", list(self.prop_map.keys()), required=True)
        self._field(card, "Financial Year (e.g. 2024-2025)", 1, self.fy_var, required=True)
        self._field(card, "Due Date (YYYY-MM-DD)", 2, self.due_var, required=True)

        self.result_var = tk.StringVar()
        tk.Label(card, textvariable=self.result_var,
                 font=FONT_SMALL, bg=BG_CARD, fg=ACCENT2,
                 wraplength=400).grid(row=7, column=0,
                 columnspan=2, sticky="w", padx=10, pady=8)

        self._status(self)
        self._save_btn(self, self._generate, label="⚡ Generate Tax")

    def _generate(self):
        prop_num = self.prop_var.get()
        fy       = self.fy_var.get().strip()
        due      = self.due_var.get().strip()

        if not all([prop_num, fy, due]):
            self.status_var.set("Fill all fields.")
            return

        prop_id = self.prop_map.get(prop_num)
        try:
            out, _ = call_procedure("sp_calculate_tax", (prop_id, fy, due, 0, ""))
            msg = out[4]
            if "ERROR" in str(msg):
                self.status_var.set(str(msg))
            else:
                self.result_var.set(str(msg))
                messagebox.showinfo("Success", str(msg))
                self.parent._show_tax_records()
                self.destroy()
        except Exception as e:
            self.status_var.set(str(e))


# ── Payment Form ─────────────────────────────────────────
class PaymentForm(BaseDialog):
    def __init__(self, parent, user):
        super().__init__(parent, "Record Payment", width=480, height=540)
        self.user = user
        tk.Label(self, text="Record Tax Payment",
                 font=("Georgia", 14, "bold"),
                 bg=BG_DARK, fg=TEXT_LIGHT).pack(pady=(12, 4))

        card = tk.Frame(self, bg=BG_CARD, padx=16, pady=10)
        card.pack(fill="both", expand=False, padx=16, pady=8)
        card.columnconfigure(0, weight=1)

        # Get pending/partial tax records
        taxes = execute_query(
            "SELECT t.tax_id, p.property_number, t.financial_year, t.total_due, t.status "
            "FROM tax_record t "
            "JOIN property p ON t.property_id=p.property_id "
            "WHERE t.status IN ('Pending','Partial','Overdue') "
            "ORDER BY p.property_number",
            fetch=True)
        self.tax_map = {}
        tax_labels = []
        for r in taxes:
            label = f"{r['property_number']} | {r['financial_year']} | ₹{r['total_due']:,.2f} ({r['status']})"
            self.tax_map[label] = r["tax_id"]
            tax_labels.append(label)

        self.tax_var    = tk.StringVar()
        self.amount_var = tk.StringVar()
        self.mode_var   = tk.StringVar()
        self.ref_var    = tk.StringVar()

        self._field(card, "Tax Record", 0, self.tax_var,
                    "combo", tax_labels, required=True)
        self._field(card, "Amount (₹)", 1, self.amount_var, required=True)
        modes = ["Online", "UPI", "NEFT", "Cash", "Cheque", "DD"]
        self._field(card, "Payment Mode", 2, self.mode_var,
                    "combo", modes)
        self._field(card, "Transaction Reference", 3, self.ref_var)

        self.receipt_var = tk.StringVar()
        tk.Label(card, text="Generated Receipt:",
                 font=FONT_LABEL, bg=BG_CARD, fg=TEXT_MUTED
                 ).grid(row=9, column=0, sticky="w", padx=10, pady=(8, 0))
        tk.Label(card, textvariable=self.receipt_var,
                 font=FONT_BOLD, bg=BG_CARD, fg=ACCENT
                 ).grid(row=10, column=0, sticky="w", padx=10)

        self._status(self)
        self._save_btn(self, self._save, label="💳 Record Payment")

    def _save(self):
        tax_label = self.tax_var.get()
        tax_id    = self.tax_map.get(tax_label)
        ref       = self.ref_var.get().strip() or None

        try:
            amount = float(self.amount_var.get())
        except ValueError:
            self.status_var.set("Amount must be a number.")
            return

        if not tax_id:
            self.status_var.set("Select a tax record.")
            return

        try:
            out, _ = call_procedure(
                "sp_record_payment",
                (tax_id, amount, self.mode_var.get(), ref, "", "")
            )
            receipt = out[4]
            msg     = out[5]

            if "ERROR" in str(msg):
                self.status_var.set(str(msg))
            else:
                self.receipt_var.set(receipt)
                messagebox.showinfo("Payment Recorded", str(msg))
                self.parent._show_payments()
                self.destroy()
        except Exception as e:
            self.status_var.set(str(e))


# ── User Form (admin only) ────────────────────────────────
class UserForm(BaseDialog):
    def __init__(self, parent, user):
        super().__init__(parent, "Add System User", width=480, height=540)
        self.user = user
        tk.Label(self, text="Create New User",
                 font=("Georgia", 14, "bold"),
                 bg=BG_DARK, fg=TEXT_LIGHT).pack(pady=(12, 4))

        card = tk.Frame(self, bg=BG_CARD, padx=16, pady=10)
        card.pack(fill="both", expand=False, padx=16, pady=8)
        card.columnconfigure(0, weight=1)

        self.uname_var    = tk.StringVar()
        self.fname_var    = tk.StringVar()
        self.email_var    = tk.StringVar()
        self.pw_var       = tk.StringVar()
        self.role_var     = tk.StringVar()

        self._field(card, "Username",  0, self.uname_var, required=True)
        self._field(card, "Full Name", 1, self.fname_var, required=True)
        self._field(card, "Email",     2, self.email_var, required=True)
        self._field(card, "Password",  3, self.pw_var,    required=True)
        self._field(card, "Role",      4, self.role_var,
                    "combo", ["clerk", "viewer", "admin"])

        self._status(self)
        self._save_btn(self, self._save)

    def _save(self):
        try:
            uname = self.uname_var.get().strip()
            fname = self.fname_var.get().strip()
            email = self.email_var.get().strip()
            pw    = self.pw_var.get().strip()
            role  = self.role_var.get()

            if not all([uname, fname, email, pw, role]):
                self.status_var.set("All fields required.")
                return

            pw_hash = hashlib.sha256(pw.encode()).hexdigest()
            execute_query(
                "INSERT INTO users (username, password_hash, role, full_name, email) "
                "VALUES (%s,%s,%s,%s,%s)",
                (uname, pw_hash, role, fname, email)
            )
            messagebox.showinfo("Success", f"User '{uname}' created.")
            self.parent._show_admin()
            self.destroy()
        except Exception as e:
            self.status_var.set(str(e))


# ── Ward Form (admin only) ────────────────────────────────
class WardForm(BaseDialog):
    def __init__(self, parent, user):
        super().__init__(parent, "Add Ward", width=480, height=520)
        self.user = user
        tk.Label(self, text="Register New Ward",
                 font=("Georgia", 14, "bold"),
                 bg=BG_DARK, fg=TEXT_LIGHT).pack(pady=(12, 4))

        card = tk.Frame(self, bg=BG_CARD, padx=16, pady=10)
        card.pack(fill="both", expand=False, padx=16, pady=8)
        card.columnconfigure(0, weight=1)

        self.name_var    = tk.StringVar()
        self.number_var  = tk.StringVar()
        self.zone_var    = tk.StringVar()
        self.officer_var = tk.StringVar()
        self.email_var   = tk.StringVar()

        self._field(card, "Ward Name",     0, self.name_var,    required=True)
        self._field(card, "Ward Number",   1, self.number_var,  required=True)
        zones = ["North Zone", "South Zone", "East Zone", "West Zone", "Central Zone"]
        self._field(card, "Zone",          2, self.zone_var,
                    "combo", zones, required=True)
        self._field(card, "Officer Name",  3, self.officer_var, required=True)
        self._field(card, "Contact Email", 4, self.email_var,   required=True)

        self._status(self)
        self._save_btn(self, self._save)

    def _save(self):
        try:
            name    = self.name_var.get().strip()
            number  = self.number_var.get().strip()
            zone    = self.zone_var.get()
            officer = self.officer_var.get().strip()
            email   = self.email_var.get().strip()

            if not all([name, number, zone, officer, email]):
                self.status_var.set("All fields are required.")
                return

            execute_query(
                "INSERT INTO ward (ward_name, ward_number, zone, officer_name, contact_email) "
                "VALUES (%s,%s,%s,%s,%s)",
                (name, number, zone, officer, email)
            )
            messagebox.showinfo("Success", f"Ward '{name}' added.")
            self.parent._show_admin()
            self.destroy()
        except Exception as e:
            self.status_var.set(str(e))

""" 
Welcome to the Source Code of GYEON Inventory Management System Application.

Make sure to read this the notes before running:
- This file uses only Python standard library (tkinter, ttk, json, os)
- Data file is saved in ./gyeon_inventory/gyeon inventory.json relative to this script file

"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import json
import os
from functools import partial
from datetime import datetime

# --------------------------------------------------------------------------------------------------------------
# First let us configure our color palettes, this application is inspired by GYEON's branding.
# --------------------------------------------------------------------------------------------------------------
# GYEON-inspired color palette (hybrid theme)
GYEON_PURPLE = "#6A1B9A"       # deep purple accent
GYEON_LIGHT = "#F8F6FB"        # very light panel background
GYEON_TEXT = "#222222"         # primary text
GYEON_ACCENT = "#9C4DCC"       # lighter purple for hover/secondary

# This is for the creation of File Directories (New: dedicated folder + filename for GYEON inventory)
DATA_DIR = os.path.join(os.path.dirname(__file__), "gyeon_inventory")
DATA_FILE = os.path.join(DATA_DIR, "gyeon inventory.json")

# This ensures the directory exists early (safe no-op if already present)
os.makedirs(DATA_DIR, exist_ok=True)

# A Category ordering for custom sort
CATEGORY_ORDER = ["Coating & Wax", "Maintenance", "Pads", "Accessories"]

# --------------------------------------------------------------------------------------------------------------
# ALGORITHMS: These are the core algorithms that will be used in the application. (based on the project proposal)
# --------------------------------------------------------------------------------------------------------------

def linear_search(inventory, name):
    """Linear search (case-insensitive) over the inventory list.

    This returns the index of the first matching item by name, or -1 if not found.
    This demonstrates linear search as required by the project proposal.
    """
    target = name.strip().lower()
    for i, item in enumerate(inventory):
        # normalize stored name too
        if item.get("name", "").strip().lower() == target:
            return i
    return -1


def bubble_sort(inventory, key="name"):
    """In-place bubble sort on inventory by 'name', 'quantity', or 'category'.

    This demonstrates bubble sort explicitly for teaching purposes.
    For 'category' I use a custom order defined in CATEGORY_ORDER.
    """
    n = len(inventory)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            a = inventory[j].get(key)
            b = inventory[j + 1].get(key)

            if key == "name":
                if str(a).lower() > str(b).lower():
                    inventory[j], inventory[j + 1] = inventory[j + 1], inventory[j]
                    swapped = True
            elif key == "product_number":
                if str(a).lower() > str(b).lower():
                    inventory[j], inventory[j + 1] = inventory[j + 1], inventory[j]
                    swapped = True
            elif key == "quantity":
                # quantity numeric compare; ensure ints
                if int(a) > int(b):
                    inventory[j], inventory[j + 1] = inventory[j + 1], inventory[j]
                    swapped = True
            elif key == "category":
                # map categories to order indices; unknown categories go last
                def cat_index(val):
                    try:
                        return CATEGORY_ORDER.index(str(val))
                    except Exception:
                        return len(CATEGORY_ORDER)
                if cat_index(a) > cat_index(b):
                    inventory[j], inventory[j + 1] = inventory[j + 1], inventory[j]
                    swapped = True
        if not swapped:
            break

# --------------------------------------------------------------------------------------------------------------
# UTILITIES: These functions are resporible for handling storage of data to/from files.
# --------------------------------------------------------------------------------------------------------------

def save_to_file(path, inventory):
    """This saves inventory list to JSON file atomically where possible.

    This ensures the containing directory exists and writes safely via a temp file.
    """
    # This ensures the directory exists for the target path
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(inventory, f, indent=2)
        os.replace(tmp, path)
    except Exception:
        # The fallback to direct write will raise to caller if it fails
        with open(path, "w", encoding="utf-8") as f:
            json.dump(inventory, f, indent=2)

def load_from_file(path):
    """This loads the inventory from JSON file. Returns a list (may be empty).

    If the file does not exist, create it with an empty list and return [].
    """
    # This ensures directory exists
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        # This will create the file with an empty list so future saves/loads are predictable
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2)
        except Exception:
            # if creation fails, just return empty inventory
            return []
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# --------------------------------------------------------------------------------------------------------------
# MAIN APPLICATION CLASS: This class encapsulates the entire GUI application and its logic.
# --------------------------------------------------------------------------------------------------------------
class GyeonInventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GYEON Inventory Manager")
        self.root.geometry("880x700")
        # main data structure: list of dicts {"product_number","name","category","quantity"}
        self.inventory = []

        # style configuration
        self._setup_style()

        # build UI
        self._build_header()
        self._build_main_area()
        self._build_footer()

        # load saved data if present (this will create the file if missing)
        try:
            self.inventory = load_from_file(DATA_FILE)
            self.refresh_table()
        except Exception:
            # ignore load errors on startup but ensure inventory starts empty
            self.inventory = []

    # --------------------------------------------------------------------------------------------------------------
    # STYLING SETUP: This method configures the ttk styles for the application.
    # --------------------------------------------------------------------------------------------------------------
    def _setup_style(self):
        """This configure ttk styles to create the hybrid GYEON look.

        I use a light panel background with a dark purple header to match the
        requested 'hybrid' theme: white content panels + dark purple header.
        """
        style = ttk.Style(self.root)
        # Use the default theme as base
        style.theme_use("default")

        # general font
        default_font = ("Segoe UI", 12)
        self.root.option_add("Font", default_font)

        # Header style (label)
        style.configure("Header.TFrame", background=GYEON_PURPLE)
        style.configure("Header.TLabel", background=GYEON_PURPLE, foreground="white",
                        font=("Segoe UI", 16, "bold"))

        # Panel style (content frames)
        style.configure("Panel.TFrame", background=GYEON_LIGHT)

        # Treeview style
        style.configure("Treeview",
                        background="white",
                        fieldbackground="white",
                        foreground=GYEON_TEXT,
                        rowheight=28)
        style.map("Treeview", background=[("selected", GYEON_ACCENT)])

        # Button styles
        style.configure("Primary.TButton", background=GYEON_PURPLE, foreground="white",
                        font=("Segoe UI", 10, "bold"), padding=6)
        style.map("Primary.TButton",
                  background=[("active", GYEON_ACCENT)])

        style.configure("Secondary.TButton", background=GYEON_LIGHT, foreground=GYEON_TEXT,
                        font=("Segoe UI", 10), padding=6)
        style.map("Secondary.TButton",
                  background=[("active", "#EEEEEE")])

    # --------------------------------------------------------------------------------------------------------------
    # BUILD UI COMPONENTS: These methods build the various sections of the GUI.
    # --------------------------------------------------------------------------------------------------------------
    def _build_header(self):
        """Top header with brand name and tagline.

        This provides a strong GYEON brand presence while keeping the content panels
        light for readability.
        """
        header = ttk.Frame(self.root, style="Header.TFrame")
        header.pack(fill=tk.X)
        lbl = ttk.Label(header, text="GYEON — Inventory Management System", style="Header.TLabel")
        lbl.pack(side=tk.LEFT, padx=16, pady=12)

        # Live date/time on the right side of the header
        self.datetime_var = tk.StringVar()
        # initialize
        self.datetime_var.set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.datetime_label = ttk.Label(header, textvariable=self.datetime_var, style="Header.TLabel")
        self.datetime_label.pack(side=tk.RIGHT, padx=16)
        # start periodic updates
        self._update_datetime()

    def _update_datetime(self):
        try:
            self.datetime_var.set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            # update every 1s
            self.root.after(1000, self._update_datetime)
        except Exception:
            # if root is destroyed or any error occurs, silently stop updates
            pass

    def _build_main_area(self):
        """Main application area: left side form, right side inventory table.

        The layout uses a horizontal split: input form & controls on the left and
        a Treeview table on the right for a professional presentation.
        """
        main = ttk.Frame(self.root, style="Panel.TFrame", padding=(12, 12))
        main.pack(fill=tk.BOTH, expand=True)

        # Left column: inputs and action buttons
        left = ttk.Frame(main, style="Panel.TFrame")
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))

        # Input fields with labels
        _lbl_kw = {"anchor": "w"}
        ttk.Label(left, text="Product Number (required):", **_lbl_kw).pack(fill=tk.X, pady=(6, 0))
        self.product_entry = ttk.Entry(left)
        self.product_entry.pack(fill=tk.X, pady=4)

        ttk.Label(left, text="Name:", **_lbl_kw).pack(fill=tk.X, pady=(6, 0))
        self.name_entry = ttk.Entry(left)
        self.name_entry.pack(fill=tk.X, pady=4)

        ttk.Label(left, text="Category:", anchor="w").pack(fill=tk.X, pady=(6, 0))
        self.cat_entry = ttk.Combobox(left, state="readonly", values=[
            "Coating & Wax",
            "Maintenance",
            "Compounds",
            "Pads",
            "Accessories"
        ])
        self.cat_entry.pack(fill=tk.X, pady=4)

        ttk.Label(left, text="Quantity:", **_lbl_kw).pack(fill=tk.X, pady=(6, 0))
        self.qty_entry = ttk.Entry(left)
        self.qty_entry.pack(fill=tk.X, pady=4)

        # Action buttons (grouped)
        btn_frame = ttk.Frame(left, style="Panel.TFrame")
        btn_frame.pack(fill=tk.X, pady=(12, 6))

        # Primary actions
        ttk.Button(btn_frame, text="Add Item", style="Primary.TButton", command=self.add_item).pack(fill=tk.X, pady=4)
        ttk.Button(btn_frame, text="Update Selected", style="Secondary.TButton", command=self.update_selected).pack(fill=tk.X, pady=4)
        ttk.Button(btn_frame, text="Delete Selected", style="Secondary.TButton", command=self.delete_selected).pack(fill=tk.X, pady=4)

        # Sorting controls (Search button removed)
        ttk.Button(btn_frame, text="Sort by Prod #", style="Secondary.TButton", command=partial(self.sort_items, "product_number")).pack(fill=tk.X, pady=4)
        ttk.Button(btn_frame, text="Sort by Name", style="Secondary.TButton", command=partial(self.sort_items, "name")).pack(fill=tk.X, pady=4)
        ttk.Button(btn_frame, text="Sort by Quantity", style="Secondary.TButton", command=partial(self.sort_items, "quantity")).pack(fill=tk.X, pady=4)
        ttk.Button(btn_frame, text="Sort by Category", style="Secondary.TButton", command=self.filter_by_category).pack(fill=tk.X, pady=4)

        # Right column: inventory table and file operations
        right = ttk.Frame(main, style="Panel.TFrame")
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Realtime search bar
        search_frame = ttk.Frame(right, style="Panel.TFrame")
        search_frame.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 6))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_entry.bind("<KeyRelease>", self.realtime_filter)

        # Table (Treeview) with columns
        columns = ("product_number", "name", "category", "quantity")
        self.tree = ttk.Treeview(right, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("product_number", text="Prod #")
        self.tree.heading("name", text="Name")
        self.tree.heading("category", text="Category")
        self.tree.heading("quantity", text="Qty")

        # column widths
        self.tree.column("product_number", width=100, anchor="center")
        self.tree.column("name", width=220)
        self.tree.column("category", width=160)
        self.tree.column("quantity", width=80, anchor="center")

        # vertical scrollbar
        vsb = ttk.Scrollbar(right, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=(0, 6))

        # bind selection event
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def _build_footer(self):
        """Footer: file operations and utility controls.
        """
        footer = ttk.Frame(self.root, style="Panel.TFrame", padding=(8, 8))
        footer.pack(fill=tk.X)

        left = ttk.Frame(footer, style="Panel.TFrame")
        left.pack(side=tk.LEFT)
        ttk.Button(left, text="Save Inventory", style="Primary.TButton", command=self.save_inventory).pack(side=tk.LEFT, padx=4)
        ttk.Button(left, text="Load Inventory", style="Secondary.TButton", command=self.load_inventory).pack(side=tk.LEFT, padx=4)
        ttk.Button(left, text="Export As...", style="Secondary.TButton", command=self.export_as).pack(side=tk.LEFT, padx=4)

        right = ttk.Frame(footer, style="Panel.TFrame")
        right.pack(side=tk.RIGHT)
        ttk.Button(right, text="Clear All", style="Secondary.TButton", command=self.clear_all).pack(side=tk.RIGHT, padx=4)

    # --------------------------------------------------------------------------------------------------------------
    # TABLE MANAGEMENT: These methods handle populating and refreshing the Treeview table.
    # --------------------------------------------------------------------------------------------------------------
    def refresh_table(self):
        """Making it clear and repopulating the Treeview from self.inventory.

        This uses tree.delete and insert to refresh the visible table after data changes.
        """
        for r in self.tree.get_children():
            self.tree.delete(r)
        for i, item in enumerate(self.inventory):
            self.tree.insert("", tk.END, iid=str(i), values=(
                item.get("product_number", ""),
                item.get("name", ""),
                item.get("category", ""),
                item.get("quantity", "0"),
            ))

    def _get_selected_index(self):
        """Returning the index of the currently selected row in the Treeview or None.

        This handles both integer iids and cases where a filtered view may have non-integer iids.
        """
        sel = self.tree.selection()
        if not sel:
            return None
        iid = sel[0]
        try:
            return int(iid)
        except Exception:
            # fallback: try to map by unique name in the selected row
            vals = self.tree.item(iid).get("values", [])
            # expected values: [prod#, name, category, qty]
            name = ""
            if len(vals) >= 2:
                name = str(vals[1])
            elif len(vals) == 1:
                name = str(vals[0])
            if name:
                idx = linear_search(self.inventory, name)
                return idx if idx != -1 else None
            return None

    # --------------------------------------------------------------------------------------------------------------
    # CORE CRUD OPERATIONS: These methods implement the Create, Read, Update, Delete operations.
    # --------------------------------------------------------------------------------------------------------------
    def add_item(self):
        """Adds a new item or increase quantity if name already exists.

        This validates inputs, demonstrates 'add' operation on the list structure
        and uses linear_search for checking existing items.
        """
        name = self.name_entry.get().strip()
        category = self.cat_entry.get().strip()
        qty = self.qty_entry.get().strip()
        prodnum = self.product_entry.get().strip()

        if not name or not qty:
            messagebox.showwarning("Input Error", "Name and Quantity are required.")
            return
        if not qty.isdigit():
            messagebox.showwarning("Input Error", "Quantity must be an integer.")
            return
        if not prodnum:
            messagebox.showwarning("Input Error", "Product Number is required.")
            return

        idx = linear_search(self.inventory, name)
        if idx != -1:
            # Found existing item: ask to increment or cancel
            if messagebox.askyesno("Item Exists", f"'{name}' exists. Add quantity to existing item?"):
                self.inventory[idx]["quantity"] = str(int(self.inventory[idx]["quantity"]) + int(qty))
            else:
                messagebox.showinfo("Cancelled", "Add operation cancelled.")
                return
        else:
            # Before appending, ensure product number (if provided) is unique
            if prodnum:
                for itm in self.inventory:
                    if itm.get("product_number", "").strip() == prodnum:
                        messagebox.showwarning(
                            "Duplicate Product Number",
                            f"Product number '{prodnum}' already exists. Please use a unique product number."
                        )
                        return

            # Append demonstrates list 'add' behavior
            new_item = {
                "product_number": prodnum,
                "name": name,
                "category": category,
                "quantity": str(qty)
            }
            self.inventory.append(new_item)

        self.refresh_table()
        self._clear_inputs()

    def update_selected(self):
        """Updates the selected item fields. Blank inputs keep current values.

        This demonstrates in-place update of an element in the list structure.
        """
        idx = self._get_selected_index()
        if idx is None:
            messagebox.showinfo("Select Item", "Please select an item to update.")
            return

        name = self.name_entry.get().strip()
        category = self.cat_entry.get().strip()
        qty = self.qty_entry.get().strip()
        prodnum = self.product_entry.get().strip()

        item = self.inventory[idx]
        if name:
            item["name"] = name
        if category:
            item["category"] = category
        if prodnum:
            # Ensure new product number does not clash with another item
            for i, it in enumerate(self.inventory):
                if i != idx and it.get("product_number", "").strip() == prodnum:
                    messagebox.showwarning(
                        "Duplicate Product Number",
                        f"Product number '{prodnum}' already exists for another item."
                    )
                    return

            item["product_number"] = prodnum
        if qty:
            if not qty.isdigit():
                messagebox.showwarning("Input Error", "Quantity must be an integer.")
                return
            item["quantity"] = str(qty)

        # Update view and clear inputs to avoid accidental edits
        self.refresh_table()
        self._clear_inputs()

    def delete_selected(self):
        """Deletes the selected item from the list, demonstrating list deletion and shifting."""
        idx = self._get_selected_index()
        if idx is None:
            messagebox.showinfo("Select Item", "Please select an item to delete.")
            return
        item = self.inventory[idx]
        if messagebox.askyesno("Confirm Delete", f"Delete '{item.get('name')}' from inventory?"):
            # delete shifts subsequent elements left automatically in list
            del self.inventory[idx]
            self.refresh_table()

    def search_item(self):
        """Searches inventory by partial keyword and display matching items.
        This replaces the exact-match search and enables live filtering."""
        keyword = simpledialog.askstring("Search", "Enter keyword to filter:")
        if keyword is None or keyword.strip() == "":
            return

        keyword = keyword.strip().lower()
        filtered = [item for item in self.inventory
                if keyword in item.get("name", "").lower()
                or keyword in item.get("product_number", "").lower()]

        # Update tree to show filtered results
        self.refresh_treeview(filtered)

        messagebox.showinfo("Search Results", f"Found {len(filtered)} item(s) matching '{keyword}'.")

    def realtime_filter(self, event=None):
        """Filter items as user types into the search bar."""
        keyword = self.search_var.get().strip().lower()
        if keyword == "":
            self.refresh_treeview()
            return
        filtered = [item for item in self.inventory
                    if keyword in item.get("name", "").lower()
                    or keyword in item.get("product_number", "").lower()]
        self.refresh_treeview(filtered)

    def refresh_treeview(self, data=None):
        """Refresh Treeview with full inventory or filtered list.

        Ensures 4-column values and sets iids that map back to self.inventory indices.
        """
        for row in self.tree.get_children():
            self.tree.delete(row)

        if data is None:
            # full view: set iid to inventory index
            for i, item in enumerate(self.inventory):
                self.tree.insert("", tk.END, iid=str(i), values=(
                    item.get("product_number", ""),
                    item.get("name", ""),
                    item.get("category", ""),
                    item.get("quantity", "0"),
                ))
        else:
            # filtered view: try to preserve mapping by using the index in the main inventory
            for item in data:
                try:
                    i = self.inventory.index(item)
                    iid = str(i)
                except ValueError:
                    iid = None
                vals = (
                    item.get("product_number", ""),
                    item.get("name", ""),
                    item.get("category", ""),
                    item.get("quantity", "0"),
                )
                if iid is not None:
                    self.tree.insert("", tk.END, iid=iid, values=vals)
                else:
                    self.tree.insert("", tk.END, values=vals)

    def sort_items(self, key):
        """Sort inventory in-place using bubble_sort and refresh table.

        the key may be 'name', 'quantity', 'category', or 'product_number'.
        """
        if key not in ("name", "quantity", "category", "product_number"):
            return
        bubble_sort(self.inventory, key=key)
        self.refresh_table()

    def filter_by_category(self):
        """Shows a modal Combobox allowing the user to choose a category to filter by.

        The dialog lists categories from CATEGORY_ORDER first, then any additional
        categories found in the inventory. Selecting OK filters the table to that
        category; Cancel or closing the dialog keeps the current view.
        """
        # gather present categories from inventory (non-empty, stripped)
        present = sorted({(it.get("category", "") or "").strip() for it in self.inventory if it.get("category")})
        # create ordered options: CATEGORY_ORDER first, then other present categories
        options = [c for c in CATEGORY_ORDER if c] + [c for c in present if c and c not in CATEGORY_ORDER]

        if not options:
            messagebox.showinfo("No Categories", "No categories available to filter.")
            return

        dlg = tk.Toplevel(self.root)
        dlg.title("Filter by Category")
        dlg.transient(self.root)
        dlg.resizable(False, False)
        dlg.grab_set()

        frm = ttk.Frame(dlg, padding=12)
        frm.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frm, text="Select category:").pack(anchor="w")
        combo = ttk.Combobox(frm, values=options, state="readonly")
        combo.pack(fill=tk.X, pady=(6, 12))
        combo.current(0)

        result = {"sel": None}

        def on_ok():
            result["sel"] = combo.get().strip()
            dlg.destroy()

        def on_cancel():
            dlg.destroy()

        btns = ttk.Frame(frm)
        btns.pack(fill=tk.X)
        ttk.Button(btns, text="OK", command=on_ok).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0,6))
        ttk.Button(btns, text="Cancel", command=on_cancel).pack(side=tk.LEFT, expand=True, fill=tk.X)

        # center the dialog over root
        self.root.update_idletasks()
        x = self.root.winfo_rootx() + (self.root.winfo_width() // 2) - (dlg.winfo_reqwidth() // 2)
        y = self.root.winfo_rooty() + (self.root.winfo_height() // 2) - (dlg.winfo_reqheight() // 2)
        dlg.geometry(f"+{x}+{y}")

        self.root.wait_window(dlg)

        sel = result.get("sel")
        if not sel:
            return

        filtered = [item for item in self.inventory if item.get("category", "").strip().lower() == sel.lower()]
        self.refresh_treeview(filtered)
        messagebox.showinfo("Filter Results", f"Showing {len(filtered)} item(s) in category '{sel}'.")

    # --------------------------------------------------------------------------------------------------------------
    # TREE SECTION HANDLERS: These methods handle interactions with the Treeview table.
    # --------------------------------------------------------------------------------------------------------------
    def on_tree_select(self, event):
        """Populates the input fields with the selected row for convenient editing."""
        idx = self._get_selected_index()
        if idx is None:
            return
        item = self.inventory[idx]
        self.product_entry.delete(0, tk.END)
        self.product_entry.insert(0, item.get("product_number", ""))
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, item.get("name", ""))
        # Combobox uses set() to change value
        try:
            self.cat_entry.set(item.get("category", ""))
        except Exception:
            self.cat_entry.delete(0, tk.END)
            self.cat_entry.insert(0, item.get("category", ""))
        self.qty_entry.delete(0, tk.END)
        self.qty_entry.insert(0, item.get("quantity", ""))

    # --------------------------------------------------------------------------------------------------------------
    # FILE OPERATIONS: These methods handle saving, loading, and exporting inventory data.
    # --------------------------------------------------------------------------------------------------------------
    def save_inventory(self):
        """Saves current inventory to the dedicated GYEON file with atomic write."""
        try:
            # save_to_file will create the folder/file if necessary
            save_to_file(DATA_FILE, self.inventory)
            messagebox.showinfo("Saved", f"Inventory saved to: {DATA_FILE}")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def load_inventory(self):
        """Loads inventory from DATA_FILE and refresh the table.

        Any load error will be reported to the user. Loading overwrites the in-memory
        list to reflect persistent storage.
        """
        try:
            data = load_from_file(DATA_FILE)
            # Support both old-format (list) and new export-format (dict with 'inventory')
            if isinstance(data, dict) and "inventory" in data:
                loaded = data.get("inventory") or []
            elif isinstance(data, list):
                loaded = data
            else:
                messagebox.showerror("Load Error", "Unexpected data format in inventory file.")
                return

            # Validate items: keep only dict entries to avoid 'str' has no attribute 'get' errors
            cleaned = []
            skipped = 0
            for it in loaded:
                if isinstance(it, dict):
                    cleaned.append(it)
                else:
                    skipped += 1

            self.inventory = cleaned
            self.refresh_table()
            msg = f"Inventory loaded from: {DATA_FILE}."
            if skipped:
                msg += f"\n{skipped} invalid item(s) were skipped during load."
            messagebox.showinfo("Loaded", msg)
        except Exception as e:
            messagebox.showerror("Load Error", str(e))

    def export_as(self):
        """Exports the inventory to a user-specified JSON file via a save dialog."""
        path = filedialog.asksaveasfilename(defaultextension=".json",
                                            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                                            title="Export inventory as...")
        if not path:
            return
        try:
            # Build export payload with metadata summary and timestamp
            exported_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            total_items = len(self.inventory)
            total_quantity = 0
            by_category_counts = {}
            by_category_products = {}
            for it in self.inventory:
                try:
                    q = int(it.get("quantity", 0))
                except Exception:
                    q = 0
                total_quantity += q
                cat = (it.get("category") or "").strip() or "Uncategorized"
                # counts
                by_category_counts[cat] = by_category_counts.get(cat, 0) + 1
                # readable product statement per category
                prodnum = (it.get("product_number") or "").strip() or "N/A"
                name = (it.get("name") or "").strip() or "Unnamed"
                stmt = f"{prodnum} — {name} (Qty: {q})"
                by_category_products.setdefault(cat, []).append(stmt)

            export_data = {
                "Inventory updated as of": exported_at,
                "summary": {
                        "total_items": total_items,
                        "total_quantity": total_quantity,
                        "by_category_counts": by_category_counts,
                        "by_category_products": by_category_products,
                },
                "inventory": self.inventory,
            }

            save_to_file(path, export_data)
            messagebox.showinfo("Exported", f"Inventory exported to: {path}\nExport time: {exported_at}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    # --------------------------------------------------------------------------------------------------------------
    # UTILITIES: These methods provide additional utility functions.
    # --------------------------------------------------------------------------------------------------------------
    def _clear_inputs(self):
        """Clears all input entry widgets to their default empty state."""
        self.product_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        try:
            self.cat_entry.set("")
        except Exception:
            self.cat_entry.delete(0, tk.END)
        self.qty_entry.delete(0, tk.END)

    def clear_all(self):
        """Clears entire inventory after user confirmation - also removes saved file."""
        if not messagebox.askyesno("Confirm", "Clear ALL inventory? This cannot be undone."):
            return
        self.inventory = []
        self.refresh_table()
        try:
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
        except Exception:
            pass

# --------------------------------------------------------------------------------------------------------------
# RUNNING THE APPLICATION: This block starts the Tkinter main loop.
# --------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = GyeonInventoryApp(root)
    root.mainloop()
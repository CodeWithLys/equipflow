import requests
import json
from qr_scanner import scan_employee_qr
import urllib3
import time
import traceback
import threading
import customtkinter as ctk
from tkinter import messagebox, scrolledtext
import sys
from PIL import Image, ImageTk

# Suppress SSL warnings for testing only
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# API configuration
API_URL = "https://oracleapex.com/ords/nexora/api"
HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "NexoraEquipmentApp/1.0"
}

# Create a session for better performance
session = requests.Session()
session.verify = False  # Disable SSL verification for testing
session.timeout = 30

# Global variables for GUI
current_emp_id = None
root = None
text_widget = None
current_checkouts = []

# Modern color theme
THEME = {
    "primary": "#2563eb",  # Blue
    "secondary": "#64748b",  # Slate
    "success": "#16a34a",  # Green
    "warning": "#ea580c",  # Orange
    "danger": "#dc2626",  # Red
    "dark_bg": "#1e293b",  # Dark blue-gray
    "light_bg": "#f8fafc",  # Light background
    "card_bg": "#ffffff",  # White cards
    "text_light": "#f1f5f9",  # Light text
    "text_dark": "#334155",  # Dark text
    "border": "#e2e8f0",  # Border color
}

# Font settings
FONT_SETTINGS = {
    "title": ("Arial", 28, "bold"),
    "header": ("Arial", 20, "bold"),
    "subheader": ("Arial", 16, "bold"),
    "normal": ("Arial", 16),
    "small": ("Arial", 14),
    "button": ("Arial", 16, "bold")
}


def print_to_gui(message):
    """Print messages to GUI text widget instead of console"""
    if text_widget:
        text_widget.insert(ctk.END, message + "\n")
        text_widget.see(ctk.END)
    else:
        print(message)


def test_connection():
    """Test if we can connect to the API"""
    try:
        response = session.get(f"{API_URL}/employees", headers=HEADERS, timeout=10)
        if response.status_code == 200:
            print_to_gui("✅ API connection successful!")
            return True
        else:
            print_to_gui(f"❌ API returned status: {response.status_code}")
            return False
    except Exception as e:
        print_to_gui(f"❌ Connection test failed: {e}")
        return False


def make_api_request(url, method="GET", payload=None):
    """Helper function to make API requests with better error handling"""
    try:
        if method == "GET":
            response = session.get(url, headers=HEADERS, timeout=15)
        else:  # POST
            response = session.post(url, json=payload, headers=HEADERS, timeout=15)

        return response

    except requests.exceptions.Timeout:
        raise Exception("Request timed out - server may be busy")
    except requests.exceptions.ConnectionError:
        raise Exception("Connection failed - check network connection")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Request error: {e}")


def api_call_thread(target_function, *args, **kwargs):
    """Run API calls in a separate thread to avoid blocking GUI"""

    def thread_wrapper():
        try:
            target_function(*args, **kwargs)
        except Exception as e:
            print_to_gui(f"❌ Thread error: {e}")
            traceback.print_exc()

    thread = threading.Thread(target=thread_wrapper, daemon=True)
    thread.start()


def view_history(emp_id):
    """View equipment history for an employee"""
    try:
        print_to_gui("🌐 Fetching equipment history...")
        response = make_api_request(f"{API_URL}/history/{emp_id}")

        if response.status_code != 200:
            print_to_gui(f"❌ API error: {response.status_code}")
            return

        history_data = response.json()

        # Handle ORDS response structure
        if isinstance(history_data, dict) and 'items' in history_data:
            history = history_data['items']
        else:
            history = history_data

        if not history:
            print_to_gui("📋 No equipment history found.")
            print_to_gui("   This employee has not checked out any equipment yet.")
            return

        print_to_gui("\n📋 Your Equipment History:")
        print_to_gui("=" * 80)

        for h in history:
            item_name = h.get('ITEM_NAME') or h.get('item_name') or h.get('ItemName') or 'Unknown Item'
            category = h.get('CATEGORY') or h.get('category') or h.get('Category') or 'Unknown Category'
            date_booked = h.get('DATE_BOOKED') or h.get('date_booked') or h.get('DateBooked') or 'Unknown Date'
            date_returned = h.get('DATE_RETURNED') or h.get('date_returned') or h.get('DateReturned')
            status = h.get('STATUS') or h.get('status') or h.get('Status') or 'Unknown Status'
            return_notes = h.get('RETURN_NOTES') or h.get('return_notes') or h.get('ReturnNotes')
            booking_id = h.get('BOOKING_ID') or h.get('booking_id') or h.get('BookingId') or 'N/A'

            status_icon = "✅ Returned" if date_returned else "🔄 Checked Out"
            print_to_gui(f"{status_icon} | Booking ID: {booking_id}")
            print_to_gui(f"Item: {item_name} ({category})")
            print_to_gui(f"Booked: {date_booked}")
            if date_returned:
                print_to_gui(f"Returned: {date_returned}")
            if return_notes:
                print_to_gui(f"Notes: {return_notes}")
            print_to_gui("-" * 40)

    except Exception as e:
        print_to_gui(f"❌ Failed to fetch history: {e}")


def get_current_checkouts(emp_id):
    """Get currently checked out equipment"""
    global current_checkouts
    try:
        response = make_api_request(f"{API_URL}/history/{emp_id}")
        if response.status_code != 200:
            return []

        history_data = response.json()
        if isinstance(history_data, dict) and 'items' in history_data:
            history = history_data['items']
        else:
            history = history_data

        current_checkouts = [h for h in history if
                             not h.get('DATE_RETURNED') and not h.get('date_returned') and not h.get('DateReturned')]
        return current_checkouts

    except Exception as e:
        print_to_gui(f"❌ Failed to fetch current checkouts: {e}")
        return []


def show_history():
    """Wrapper for view_history to run in thread"""
    if current_emp_id:
        api_call_thread(view_history, current_emp_id)
    else:
        messagebox.showerror("Error", "Please login first")


class ReturnDialog(ctk.CTkToplevel):
    def __init__(self, parent, checkouts):
        super().__init__(parent)
        self.title("Return Equipment")
        self.geometry("600x500")  # Increased size for better readability
        self.checkouts = checkouts
        self.result = None

        self.create_widgets()

    def create_widgets(self):
        main_frame = ctk.CTkFrame(self, fg_color=THEME["card_bg"], corner_radius=12)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Header
        ctk.CTkLabel(main_frame, text="Return Equipment",
                     font=FONT_SETTINGS["header"],
                     text_color=THEME["text_dark"]).pack(pady=20)

        # Equipment selection
        ctk.CTkLabel(main_frame, text="Booking ID:",
                     font=FONT_SETTINGS["normal"],
                     text_color=THEME["text_dark"]).pack(anchor="w", padx=20, pady=(0, 10))

        self.booking_var = ctk.StringVar()
        booking_combo = ctk.CTkComboBox(main_frame, variable=self.booking_var,
                                        values=[str(item.get('BOOKING_ID') or item.get('booking_id') or item.get(
                                            'BookingId') or 'N/A') for item in self.checkouts],
                                        font=FONT_SETTINGS["normal"],
                                        dropdown_font=FONT_SETTINGS["normal"],
                                        height=40)
        booking_combo.pack(fill="x", padx=20, pady=(0, 20))

        # Notes
        ctk.CTkLabel(main_frame, text="Return Notes:",
                     font=FONT_SETTINGS["normal"],
                     text_color=THEME["text_dark"]).pack(anchor="w", padx=20, pady=(10, 10))

        self.notes_entry = ctk.CTkTextbox(main_frame, height=100, font=FONT_SETTINGS["normal"])
        self.notes_entry.pack(fill="x", padx=20, pady=(0, 20))

        # Damage status
        damage_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        damage_frame.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkLabel(damage_frame, text="Equipment Condition:",
                     font=FONT_SETTINGS["normal"],
                     text_color=THEME["text_dark"]).pack(anchor="w")

        self.damage_var = ctk.StringVar(value="N")
        ctk.CTkRadioButton(damage_frame, text="Good Condition",
                           variable=self.damage_var, value="N",
                           font=FONT_SETTINGS["normal"]).pack(anchor="w", padx=20, pady=10)

        ctk.CTkRadioButton(damage_frame, text="Damaged",
                           variable=self.damage_var, value="Y",
                           font=FONT_SETTINGS["normal"]).pack(anchor="w", padx=20, pady=10)

        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=20)

        ctk.CTkButton(button_frame, text="Confirm Return",
                      command=self.confirm_return,
                      font=FONT_SETTINGS["button"],
                      height=40,
                      fg_color=THEME["primary"]).pack(side="left", padx=10)

        ctk.CTkButton(button_frame, text="Cancel",
                      command=self.cancel,
                      font=FONT_SETTINGS["button"],
                      height=40,
                      fg_color=THEME["secondary"]).pack(side="left", padx=10)

    def confirm_return(self):
        booking_id = self.booking_var.get()
        if not booking_id or booking_id == 'N/A':
            messagebox.showerror("Error", "Please select a booking ID")
            return

        self.result = {
            "booking_id": booking_id,
            "notes": self.notes_entry.get("1.0", "end-1c"),
            "is_damaged": self.damage_var.get()
        }
        self.destroy()

    def cancel(self):
        self.destroy()


def process_return(emp_id, return_data):
    """Process equipment return"""
    try:
        # QR code verification
        print_to_gui("\n📷 Scan your employee QR code to confirm identity...")
        scanned_emp_id = scan_employee_qr()
        if not scanned_emp_id:
            print_to_gui("❌ Scan failed")
            return
        if scanned_emp_id != f"EMP{emp_id}":
            print_to_gui("❌ QR Code does not match your Employee ID")
            return

        # Prepare payload
        payload = {
            "booking_id": int(return_data["booking_id"]),
            "employee_id": int(emp_id),
            "qr_code": scanned_emp_id,
            "return_notes": return_data["notes"],
            "is_damaged": return_data["is_damaged"]
        }

        # Make API call
        print_to_gui("🔄 Processing return...")
        response = make_api_request(f"{API_URL}/return", "POST", payload)

        if response.status_code == 200:
            print_to_gui("✅ Equipment returned successfully!")
        else:
            try:
                error_data = response.json()
                print_to_gui(f"❌ Return failed: {error_data.get('error', 'Unknown error')}")
            except json.JSONDecodeError:
                print_to_gui(f"❌ Return failed: {response.text}")

    except Exception as e:
        print_to_gui(f"❌ Return request failed: {e}")


def return_equipment_gui():
    """GUI for returning equipment"""
    if not current_emp_id:
        messagebox.showerror("Error", "Please login first")
        return

    checkouts = get_current_checkouts(current_emp_id)
    if not checkouts:
        messagebox.showinfo("Info", "No equipment currently checked out")
        return

    dialog = ReturnDialog(root, checkouts)
    dialog.wait_window()

    if dialog.result:
        api_call_thread(process_return, current_emp_id, dialog.result)


class CheckoutDialog(ctk.CTkToplevel):
    def __init__(self, parent, inventory):
        super().__init__(parent)
        self.title("Checkout Equipment")
        self.geometry("700x600")  # Increased size for better readability
        self.inventory = inventory
        self.result = None

        self.create_widgets()

    def create_widgets(self):
        main_frame = ctk.CTkFrame(self, fg_color=THEME["card_bg"], corner_radius=12)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Header
        ctk.CTkLabel(main_frame, text="Checkout Equipment",
                     font=FONT_SETTINGS["header"],
                     text_color=THEME["text_dark"]).pack(pady=20)

        # Equipment selection
        ctk.CTkLabel(main_frame, text="Available Equipment:",
                     font=FONT_SETTINGS["normal"],
                     text_color=THEME["text_dark"]).pack(anchor="w", padx=20, pady=(0, 10))

        # Create a scrollable frame for equipment list
        scroll_frame = ctk.CTkScrollableFrame(main_frame, height=250)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.equipment_var = ctk.StringVar()
        for item in self.inventory:
            item_id = item.get('ITEM_ID') or item.get('item_id') or item.get('ItemId') or 'N/A'
            item_name = item.get('ITEM_NAME') or item.get('item_name') or item.get('ItemName') or 'Unknown'
            quantity = item.get('QUANTITY') or item.get('quantity') or item.get('Quantity') or 0

            frame = ctk.CTkFrame(scroll_frame, fg_color=THEME["light_bg"])
            frame.pack(fill="x", pady=5, padx=5)

            ctk.CTkRadioButton(frame,
                               text=f"{item_name} (ID: {item_id}, Qty: {quantity})",
                               variable=self.equipment_var,
                               value=item_id,
                               font=FONT_SETTINGS["normal"]).pack(anchor="w", padx=10, pady=5)

        # Notes
        ctk.CTkLabel(main_frame, text="Checkout Notes:",
                     font=FONT_SETTINGS["normal"],
                     text_color=THEME["text_dark"]).pack(anchor="w", padx=20, pady=(20, 10))

        self.notes_entry = ctk.CTkTextbox(main_frame, height=80, font=FONT_SETTINGS["normal"])
        self.notes_entry.pack(fill="x", padx=20, pady=(0, 20))

        # Damage status
        damage_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        damage_frame.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkLabel(damage_frame, text="Equipment Condition:",
                     font=FONT_SETTINGS["normal"],
                     text_color=THEME["text_dark"]).pack(anchor="w")

        self.damage_var = ctk.StringVar(value="N")
        ctk.CTkRadioButton(damage_frame, text="Good Condition",
                           variable=self.damage_var, value="N",
                           font=FONT_SETTINGS["normal"]).pack(anchor="w", padx=20, pady=10)

        ctk.CTkRadioButton(damage_frame, text="Already Damaged",
                           variable=self.damage_var, value="Y",
                           font=FONT_SETTINGS["normal"]).pack(anchor="w", padx=20, pady=10)

        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=20)

        ctk.CTkButton(button_frame, text="Confirm Checkout",
                      command=self.confirm_checkout,
                      font=FONT_SETTINGS["button"],
                      height=40,
                      fg_color=THEME["primary"]).pack(side="left", padx=10)

        ctk.CTkButton(button_frame, text="Cancel",
                      command=self.cancel,
                      font=FONT_SETTINGS["button"],
                      height=40,
                      fg_color=THEME["secondary"]).pack(side="left", padx=10)

    def confirm_checkout(self):
        item_id = self.equipment_var.get()
        if not item_id:
            messagebox.showerror("Error", "Please select equipment")
            return

        self.result = {
            "item_id": item_id,
            "notes": self.notes_entry.get("1.0", "end-1c"),
            "is_damaged": self.damage_var.get()
        }
        self.destroy()

    def cancel(self):
        self.destroy()


def get_available_inventory():
    """Get available equipment inventory"""
    try:
        response = make_api_request(f"{API_URL}/inventory")
        if response.status_code == 200:
            inventory_data = response.json()
            if isinstance(inventory_data, dict) and 'items' in inventory_data:
                inventory = inventory_data['items']
            else:
                inventory = inventory_data

            available_items = []
            for item in inventory:
                status = item.get('STATUS') or item.get('status') or item.get('Status')
                if status == 'Available':
                    available_items.append(item)
            return available_items
        return []
    except Exception as e:
        print_to_gui(f"❌ Failed to fetch inventory: {e}")
        return []


def process_checkout(emp_id, checkout_data):
    """Process equipment checkout"""
    try:
        # QR code verification
        print_to_gui("\n📷 Scan your employee QR code to confirm identity...")
        scanned_emp_id = scan_employee_qr()
        if not scanned_emp_id:
            print_to_gui("❌ Scan failed")
            return
        if scanned_emp_id != f"EMP{emp_id}":
            print_to_gui("❌ QR Code does not match your Employee ID")
            return

        # Prepare payload
        payload = {
            "item_id": checkout_data["item_id"],
            "employee_id": int(emp_id),
            "qr_code": scanned_emp_id,
            "is_damaged": checkout_data["is_damaged"],
            "checkout_notes": checkout_data["notes"]
        }

        # Make API call
        print_to_gui("🔄 Processing checkout...")
        response = make_api_request(f"{API_URL}/checkout", "POST", payload)

        if response.status_code == 200:
            print_to_gui("✅ Equipment checked out successfully!")
        else:
            try:
                error_data = response.json()
                print_to_gui(f"❌ Checkout failed: {error_data.get('error', 'Unknown error')}")
            except json.JSONDecodeError:
                print_to_gui(f"❌ Checkout failed: {response.text}")

    except Exception as e:
        print_to_gui(f"❌ Checkout request failed: {e}")


def checkout_equipment_gui():
    """GUI for checking out equipment"""
    if not current_emp_id:
        messagebox.showerror("Error", "Please login first")
        return

    inventory = get_available_inventory()
    if not inventory:
        messagebox.showinfo("Info", "No equipment available for checkout")
        return

    dialog = CheckoutDialog(root, inventory)
    dialog.wait_window()

    if dialog.result:
        api_call_thread(process_checkout, current_emp_id, dialog.result)


def create_gui():
    """Create the CustomTkinter GUI"""
    global root, text_widget

    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("Nexora Equipment Management System")
    root.geometry("1000x700")  # Increased size for better readability

    # Configure grid for responsive layout
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)

    # Main frame
    main_frame = ctk.CTkFrame(root, fg_color=THEME["light_bg"])
    main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
    main_frame.grid_columnconfigure(0, weight=1)
    main_frame.grid_rowconfigure(1, weight=1)

    # Title
    title_label = ctk.CTkLabel(main_frame,
                               text="Nexora Equipment Management",
                               font=FONT_SETTINGS["title"],
                               text_color=THEME["primary"])
    title_label.grid(row=0, column=0, pady=(0, 20))

    # Text output area
    text_widget = ctk.CTkTextbox(main_frame,
                                 font=FONT_SETTINGS["normal"],
                                 fg_color=THEME["card_bg"],
                                 text_color=THEME["text_dark"])
    text_widget.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

    # Button frame
    button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    button_frame.grid(row=2, column=0, pady=20)

    # Buttons with larger fonts and modern styling
    button_style = {
        "font": FONT_SETTINGS["button"],
        "height": 50,
        "width": 200,
        "corner_radius": 8
    }

    login_btn = ctk.CTkButton(button_frame,
                              text="📷 Login with QR",
                              command=login,
                              fg_color=THEME["primary"],
                              **button_style)
    login_btn.grid(row=0, column=0, padx=10, pady=10)

    history_btn = ctk.CTkButton(button_frame,
                                text="📋 View History",
                                command=show_history,
                                fg_color=THEME["secondary"],
                                **button_style)
    history_btn.grid(row=0, column=1, padx=10, pady=10)

    return_btn = ctk.CTkButton(button_frame,
                               text="🔄 Return Equipment",
                               command=return_equipment_gui,
                               fg_color=THEME["secondary"],
                               **button_style)
    return_btn.grid(row=0, column=2, padx=10, pady=10)

    checkout_btn = ctk.CTkButton(button_frame,
                                 text="📦 Checkout Equipment",
                                 command=checkout_equipment_gui,
                                 fg_color=THEME["secondary"],
                                 **button_style)
    checkout_btn.grid(row=0, column=3, padx=10, pady=10)

    exit_btn = ctk.CTkButton(button_frame,
                             text="🚪 Exit",
                             command=root.quit,
                             fg_color=THEME["danger"],
                             **button_style)
    exit_btn.grid(row=0, column=4, padx=10, pady=10)

    # Test connection on startup
    print_to_gui("🚀 Starting Nexora Equipment Management System...")
    api_call_thread(test_connection)

    return root


def login():
    """Handle QR login"""

    def login_thread():
        global current_emp_id
        print_to_gui("\n📷 Scan your employee QR code to login...")
        scanned_qr = scan_employee_qr()

        if not scanned_qr:
            print_to_gui("❌ Login failed.")
            return

        if scanned_qr.startswith("EMP"):
            emp_id = scanned_qr.replace("EMP", "")
            current_emp_id = emp_id
            print_to_gui(f"✅ Logged in as Employee ID: {emp_id}")

            # Get employee info
            emp_info = get_employee_info(emp_id)
            if emp_info:
                first_name = emp_info.get('FIRST_NAME') or emp_info.get('first_name') or 'User'
                last_name = emp_info.get('LAST_NAME') or emp_info.get('last_name') or ''
                department = emp_info.get('DEPARTMENT') or emp_info.get('department') or 'Unknown'

                print_to_gui(f"👋 Welcome, {first_name} {last_name}!")
                print_to_gui(f"   Department: {department}")
        else:
            print_to_gui("❌ Invalid QR code format")

    api_call_thread(login_thread)


def get_employee_info(emp_id):
    """Get employee information from API"""
    try:
        response = make_api_request(f"{API_URL}/employee/{emp_id}")
        if response.status_code == 200:
            emp_data = response.json()
            if isinstance(emp_data, dict) and 'items' in emp_data and emp_data['items']:
                return emp_data['items'][0]
            else:
                return emp_data
    except Exception as e:
        print_to_gui(f"❌ Error getting employee info: {e}")
        return None
    return None


def main():
    """Main application function"""
    global root

    # Create and run GUI
    root = create_gui()
    root.mainloop()


if __name__ == "__main__":
    main()
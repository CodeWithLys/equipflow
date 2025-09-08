import requests
import json
from qr_scanner import scan_employee_qr
import urllib3
import time

# Suppress SSL warnings for testing only
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# CORRECT API URL THAT WORKS IN POSTMAN
API_URL = "https://oracleapex.com/ords/nexora/api"

HEADERS = {"Content-Type": "application/json"}


def test_connection():
    """Test if we can connect to the API"""
    try:
        response = requests.get(f"{API_URL}/employees", headers=HEADERS, timeout=15, verify=False)
        return response.status_code == 200
    except Exception as e:
        print(f"Connection test failed: {e}")
        return False


def make_api_request(url, method="GET", payload=None):
    """Helper function to make API requests with retry logic"""
    max_retries = 2
    for attempt in range(max_retries):
        try:
            if method == "GET":
                response = requests.get(url, headers=HEADERS, timeout=20, verify=False)
            else:  # POST
                response = requests.post(url, json=payload, headers=HEADERS, timeout=20, verify=False)

            return response

        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                print(f"Timeout, retrying... ({attempt + 1}/{max_retries})")
                time.sleep(1)  # Wait before retrying
                continue
            else:
                raise Exception("Request timed out after multiple attempts")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")

    return None


def view_history(emp_id):
    try:
        response = make_api_request(f"{API_URL}/history/{emp_id}")

        print(f"API Response Status: {response.status_code}")

        if response.status_code != 200:
            print(f"❌ API returned error: {response.text}")
            return

        history_data = response.json()

        # Handle ORDS response structure
        if 'items' in history_data:
            history = history_data['items']
        else:
            history = history_data

    except Exception as e:
        print(f"❌ Failed to fetch history: {e}")
        return

    if not history:
        print("📋 No equipment history found.")
        return

    print("\n📋 Your Equipment History:")
    print("-" * 80)
    for h in history:
        status = "✅ Returned" if h.get('DATE_RETURNED') else "🔄 Checked Out"
        print(f"{status} | {h.get('ITEM_NAME')} ({h.get('CATEGORY')}) | Booked: {h.get('DATE_BOOKED')}")
        if h.get('DATE_RETURNED'):
            print(f"   Returned: {h.get('DATE_RETURNED')}")
    print("-" * 80)


def return_equipment(emp_id):
    booking_id = input("Enter Booking ID to return: ").strip()
    if not booking_id.isdigit():
        print("❌ Invalid Booking ID")
        return

    print("📷 Scan your employee QR code to confirm identity...")
    scanned_emp_id = scan_employee_qr()
    if not scanned_emp_id:
        print("❌ Scan failed")
        return
    if scanned_emp_id != f"EMP{emp_id}":
        print("❌ QR Code does not match your Employee ID")
        return

    notes = input("Return notes (optional): ").strip()

    damaged = input("Is the equipment damaged? (y/N): ").strip().lower()
    is_damaged = 'Y' if damaged in ['y', 'yes'] else 'N'

    payload = {
        "booking_id": int(booking_id),
        "employee_id": int(emp_id),
        "qr_code": scanned_emp_id,
        "return_notes": notes,
        "is_damaged": is_damaged
    }

    try:
        response = make_api_request(f"{API_URL}/return", "POST", payload)

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            print("✅ Equipment returned successfully!")
            print(f"Response: {response.text}")
        else:
            try:
                error_data = response.json()
                print("❌ Return failed:", error_data.get('error', 'Unknown error'))
            except json.JSONDecodeError:
                print("❌ Return failed:", response.text)
    except Exception as e:
        print(f"❌ Return request failed: {e}")


def checkout_equipment(emp_id):
    try:
        response = make_api_request(f"{API_URL}/inventory")

        if response.status_code != 200:
            print("❌ Failed to fetch inventory from API")
            return

        inventory_data = response.json()
        if 'items' in inventory_data:
            inventory = inventory_data['items']
        else:
            inventory = inventory_data

        print("\n📦 Available Equipment:")
        print("-" * 80)
        for item in inventory:
            if item.get('STATUS') == 'Available':
                print(
                    f"ID: {item.get('ITEM_ID')} | {item.get('ITEM_NAME')} | Qty: {item.get('QUANTITY')} | Location: {item.get('LOCATION')}")
        print("-" * 80)

    except Exception as e:
        print(f"❌ Failed to fetch inventory: {e}")
        return

    item_id = input("Enter Item ID to checkout: ").strip()

    print("📷 Scan your employee QR code to confirm identity...")
    scanned_emp_id = scan_employee_qr()
    if not scanned_emp_id:
        print("❌ Scan failed")
        return
    if scanned_emp_id != f"EMP{emp_id}":
        print("❌ QR Code does not match your Employee ID")
        return

    damaged = input("Is the equipment already damaged? (y/N): ").strip().lower()
    is_damaged = 'Y' if damaged in ['y', 'yes'] else 'N'

    payload = {
        "item_id": item_id,
        "employee_id": int(emp_id),
        "qr_code": scanned_emp_id,
        "is_damaged": is_damaged
    }

    try:
        response = make_api_request(f"{API_URL}/checkout", "POST", payload)

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            print("✅ Equipment checked out successfully!")
            print(f"Response: {response.text}")
        else:
            try:
                error_data = response.json()
                print("❌ Checkout failed:", error_data.get('error', 'Unknown error'))
            except json.JSONDecodeError:
                print("❌ Checkout failed:", response.text)
    except Exception as e:
        print(f"❌ Checkout request failed: {e}")


def main():
    print("🚀 Nexora Equipment Management")

    # Test connection first
    print("Testing connection to API...")
    if test_connection():
        print("✅ Connected to API successfully!")
    else:
        print("❌ Cannot connect to API. Continuing with limited functionality...")

    print("📷 Scan your employee QR code to login...")
    scanned_qr = scan_employee_qr()
    if not scanned_qr:
        print("❌ Scan failed. Exiting.")
        return

    if scanned_qr.startswith("EMP"):
        emp_id = scanned_qr.replace("EMP", "")
    else:
        print("❌ Invalid QR code format")
        return

    try:
        response = make_api_request(f"{API_URL}/employee/{emp_id}")
        if response.status_code == 200:
            emp_data = response.json()
            if 'items' in emp_data:
                emp = emp_data['items'][0]
            else:
                emp = emp_data

            print(f"✅ Logged in as {emp['first_name']} {emp['last_name']} ({emp['department']})")
        else:
            print(f"✅ Logged in as Employee ID: {emp_id}")
    except Exception as e:
        print(f"✅ Logged in as Employee ID: {emp_id} (API error: {e})")

    while True:
        print("\nMAIN MENU")
        print("1. View My Equipment History")
        print("2. Return Equipment")
        print("3. Checkout Equipment")
        print("4. Exit")

        choice = input("Select an option (1-4): ").strip()
        if choice == "1":
            view_history(emp_id)
        elif choice == "2":
            return_equipment(emp_id)
        elif choice == "3":
            checkout_equipment(emp_id)
        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option. Try again.")


if __name__ == "__main__":
    main()

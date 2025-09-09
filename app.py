
import json
import urllib3
import requests
import streamlit as st
from streamlit_webrtc import webrtc_streamer
import av
import cv2
from typing import List, Dict, Any

# ============================
# Basic Setup
# ============================

# Suppress SSL warnings for testing only (keep False verification only for dev)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_URL = "https://oracleapex.com/ords/nexora/api"
HEADERS = {"Content-Type": "application/json", "User-Agent": "NexoraEquipmentApp/1.0"}

session = requests.Session()
session.verify = False  # Disable SSL verification for testing
# Note: requests.Session has no global timeout attribute; pass timeout per call

# Streamlit page config
st.set_page_config(page_title="Nexora Equipment Management", layout="wide")
st.title("📦 Nexora Equipment Management System")

# A simple logger that mirrors your original print_to_gui behavior
def log(message: str):
    if "log" not in st.session_state:
        st.session_state["log"] = []
    st.session_state["log"].append(message)

def show_log():
    logs = st.session_state.get("log", [])
    with st.expander("📜 Activity Log", expanded=True):
        st.text("\n".join(logs[-300:]))  # show recent messages
        if st.button("Clear Log"):
            st.session_state["log"] = []

# ============================
# API helpers (kept close to your originals)
# ============================

def make_api_request(url: str, method: str = "GET", payload: Dict[str, Any] = None):
    try:
        if method == "GET":
            response = session.get(url, headers=HEADERS, timeout=15)
        else:
            response = session.post(url, json=payload, headers=HEADERS, timeout=15)
        return response
    except requests.exceptions.Timeout:
        raise Exception("Request timed out - server may be busy")
    except requests.exceptions.ConnectionError:
        raise Exception("Connection failed - check network connection")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Request error: {e}")

def test_connection() -> bool:
    """Test if we can connect to the API"""
    try:
        response = session.get(f"{API_URL}/employees", headers=HEADERS, timeout=10)
        if response.status_code == 200:
            log("✅ API connection successful!")
            return True
        else:
            log(f"❌ API returned status: {response.status_code}")
            return False
    except Exception as e:
        log(f"❌ Connection test failed: {e}")
        return False

def get_employee_info(emp_id: str):
    try:
        response = make_api_request(f"{API_URL}/employee/{emp_id}")
        if response.status_code == 200:
            emp_data = response.json()
            if isinstance(emp_data, dict) and "items" in emp_data and emp_data["items"]:
                return emp_data["items"][0]
            else:
                return emp_data
    except Exception as e:
        log(f"❌ Error getting employee info: {e}")
        return None
    return None

def view_history(emp_id: str):
    """View equipment history for an employee"""
    try:
        log("🌐 Fetching equipment history...")
        response = make_api_request(f"{API_URL}/history/{emp_id}")

        if response.status_code != 200:
            log(f"❌ API error: {response.status_code}")
            return

        history_data = response.json()

        # Handle ORDS response structure
        if isinstance(history_data, dict) and 'items' in history_data:
            history = history_data['items']
        else:
            history = history_data

        if not history:
            log("📋 No equipment history found.")
            log("   This employee has not checked out any equipment yet.")
            return

        log("\n📋 Your Equipment History:")
        log("=" * 80)

        for h in history:
            item_name = h.get('ITEM_NAME') or h.get('item_name') or h.get('ItemName') or 'Unknown Item'
            category = h.get('CATEGORY') or h.get('category') or h.get('Category') or 'Unknown Category'
            date_booked = h.get('DATE_BOOKED') or h.get('date_booked') or h.get('DateBooked') or 'Unknown Date'
            date_returned = h.get('DATE_RETURNED') or h.get('date_returned') or h.get('DateReturned')
            status = h.get('STATUS') or h.get('status') or h.get('Status') or 'Unknown Status'
            return_notes = h.get('RETURN_NOTES') or h.get('return_notes') or h.get('ReturnNotes')
            booking_id = h.get('BOOKING_ID') or h.get('booking_id') or h.get('BookingId') or 'N/A'

            status_icon = "✅ Returned" if date_returned else "🔄 Checked Out"
            log(f"{status_icon} | Booking ID: {booking_id}")
            log(f"Item: {item_name} ({category})")
            log(f"Booked: {date_booked}")
            if date_returned:
                log(f"Returned: {date_returned}")
            if return_notes:
                log(f"Notes: {return_notes}")
            log("-" * 40)

    except Exception as e:
        log(f"❌ Failed to fetch history: {e}")

def get_current_checkouts(emp_id: str) -> List[Dict[str, Any]]:
    """Get currently checked out equipment"""
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
        log(f"❌ Failed to fetch current checkouts: {e}")
        return []

def get_available_inventory() -> List[Dict[str, Any]]:
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
        log(f"❌ Failed to fetch inventory: {e}")
        return []

def process_return(emp_id: str, booking_id: str, notes: str, is_damaged: str, scanned_qr: str):
    """Process equipment return"""
    try:
        if not scanned_qr:
            log("❌ Scan failed")
            return
        if scanned_qr != f"EMP{emp_id}":
            log("❌ QR Code does not match your Employee ID")
            return

        payload = {
            "booking_id": int(booking_id),
            "employee_id": int(emp_id),
            "qr_code": scanned_qr,
            "return_notes": notes,
            "is_damaged": is_damaged
        }

        log("🔄 Processing return...")
        response = make_api_request(f"{API_URL}/return", "POST", payload)

        if response.status_code == 200:
            log("✅ Equipment returned successfully!")
        else:
            try:
                error_data = response.json()
                log(f"❌ Return failed: {error_data.get('error', 'Unknown error')}")
            except json.JSONDecodeError:
                log(f"❌ Return failed: {response.text}")

    except Exception as e:
        log(f"❌ Return request failed: {e}")

def process_checkout(emp_id: str, item_id: str, notes: str, is_damaged: str, scanned_qr: str):
    """Process equipment checkout"""
    try:
        if not scanned_qr:
            log("❌ Scan failed")
            return
        if scanned_qr != f"EMP{emp_id}":
            log("❌ QR Code does not match your Employee ID")
            return

        payload = {
            "item_id": item_id,
            "employee_id": int(emp_id),
            "qr_code": scanned_qr,
            "is_damaged": is_damaged,
            "checkout_notes": notes
        }

        log("🔄 Processing checkout...")
        response = make_api_request(f"{API_URL}/checkout", "POST", payload)

        if response.status_code == 200:
            log("✅ Equipment checked out successfully!")
        else:
            try:
                error_data = response.json()
                log(f"❌ Checkout failed: {error_data.get('error', 'Unknown error')}")
            except json.JSONDecodeError:
                log(f"❌ Checkout failed: {response.text}")

    except Exception as e:
        log(f"❌ Checkout request failed: {e}")

# ============================
# Webcam + QR scanning (OpenCV's QRCodeDetector to avoid external zbar dependency)
# ============================

qrdetector = cv2.QRCodeDetector()

def qr_video_frame_callback(frame):
    img = frame.to_ndarray(format="bgr24")
    # Detect & decode QR using OpenCV
    data, points, _ = qrdetector.detectAndDecode(img)
    if data:
        # Persist the last scanned QR for use in UI
        st.session_state["last_qr"] = data
        # Auto-login if it's an employee code
        if data.startswith("EMP"):
            st.session_state["emp_id"] = data.replace("EMP", "")
    return av.VideoFrame.from_ndarray(img, format="bgr24")

# ============================
# UI Flow
# ============================

# Run API connectivity check once per session
if "api_tested" not in st.session_state:
    with st.spinner("Testing API connection..."):
        test_connection()
    st.session_state["api_tested"] = True

# Left: Controls, Right: Log
left, right = st.columns([3, 2])

with left:
    # LOGIN / PROFILE
    if "emp_id" not in st.session_state:
        st.info("📷 Please scan your employee QR code to login.")
        webrtc_streamer(
            key="qr-login",
            video_frame_callback=qr_video_frame_callback,
            media_stream_constraints={"video": True, "audio": False},
        )
        last_qr = st.session_state.get("last_qr")
        if last_qr:
            st.caption(f"Last QR read: {last_qr}")
    else:
        emp_id = st.session_state["emp_id"]
        st.success(f"✅ Logged in as Employee ID: {emp_id}")
        emp_info = get_employee_info(emp_id)
        if emp_info:
            fn = emp_info.get('FIRST_NAME') or emp_info.get('first_name') or 'User'
            ln = emp_info.get('LAST_NAME') or emp_info.get('last_name') or ''
            dept = emp_info.get('DEPARTMENT') or emp_info.get('department') or 'Unknown'
            st.write(f"👋 Welcome, **{fn} {ln}**")
            st.write(f"**Department:** {dept}")

        # ACTIONS
        st.subheader("Actions")

        # View history
        if st.button("📋 View History"):
            with st.spinner("Loading history..."):
                view_history(emp_id)

        # Checkout section
        with st.expander("📦 Checkout Equipment", expanded=False):
            with st.spinner("Loading available inventory..."):
                inv = get_available_inventory()
            if not inv:
                st.info("No equipment available for checkout")
            else:
                item_map = {
                    f"{(i.get('ITEM_NAME') or i.get('item_name') or 'Unknown')} "
                    f"(ID: {(i.get('ITEM_ID') or i.get('item_id') or 'N/A')}, "
                    f"Qty: {(i.get('QUANTITY') or i.get('quantity') or 0)})":
                    str(i.get('ITEM_ID') or i.get('item_id'))
                    for i in inv
                }
                item_label = st.selectbox("Available items", list(item_map.keys()))
                item_id = item_map[item_label]
                notes = st.text_area("Checkout Notes", "")
                dmg = st.radio("Equipment Condition", ["Good Condition", "Already Damaged"], index=0)
                is_damaged = "Y" if dmg == "Already Damaged" else "N"

                st.markdown("**Scan your QR again to confirm identity before checkout**")
                webrtc_streamer(
                    key="qr-checkout",
                    video_frame_callback=qr_video_frame_callback,
                    media_stream_constraints={"video": True, "audio": False},
                )
                st.caption(f"Last QR read: {st.session_state.get('last_qr', '—')}")

                if st.button("Confirm & Checkout"):
                    with st.spinner("Processing checkout..."):
                        process_checkout(emp_id, item_id, notes, is_damaged, st.session_state.get("last_qr"))

        # Return section
        with st.expander("🔄 Return Equipment", expanded=False):
            with st.spinner("Loading your current checkouts..."):
                checkouts = get_current_checkouts(emp_id)
            if not checkouts:
                st.info("No equipment currently checked out")
            else:
                # Build label->booking_id map
                chk_map = {}
                for item in checkouts:
                    booking_id = str(item.get('BOOKING_ID') or item.get('booking_id') or item.get('BookingId') or 'N/A')
                    item_name = item.get('ITEM_NAME') or item.get('item_name') or 'Unknown'
                    date_booked = item.get('DATE_BOOKED') or item.get('date_booked') or 'Unknown'
                    chk_map[f"{item_name} • Booking {booking_id} • Booked {date_booked}"] = booking_id

                sel_label = st.selectbox("Select booking to return", list(chk_map.keys()))
                booking_id = chk_map[sel_label]
                notes_r = st.text_area("Return Notes", "")
                dmg_r = st.radio("Return Condition", ["Good Condition", "Damaged"], index=0)
                is_damaged_r = "Y" if dmg_r == "Damaged" else "N"

                st.markdown("**Scan your QR again to confirm identity before return**")
                webrtc_streamer(
                    key="qr-return",
                    video_frame_callback=qr_video_frame_callback,
                    media_stream_constraints={"video": True, "audio": False},
                )
                st.caption(f"Last QR read: {st.session_state.get('last_qr', '—')}")

                if st.button("Confirm & Return"):
                    with st.spinner("Processing return..."):
                        process_return(emp_id, booking_id, notes_r, is_damaged_r, st.session_state.get("last_qr"))

with right:
    show_log()

st.markdown("---")
st.caption("Tip: For production, enable SSL verification and move secrets (API URL, credentials) to environment variables.")

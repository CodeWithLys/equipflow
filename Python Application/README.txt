Overview
This document provides instructions to run the Python client application (equipflow_app.py) for employee equipment management.

Prerequisites
Python 3.9 or later installed on your machine.

Required Python packages installed:

text
pip install requests qrcode[pil] opencv-python pillow customtkinter
Ensure that equipflow_app.py and qr_scanner.py files are both present in the same project directory.

Running the Application
1. Start qr_scanner.py first:
This script initializes the webcam and handles QR code scanning required for user authentication and equipment transactions. It must be running to enable webcam access.

2. Run equipflow_app.py:
Launch the main application by running equipflow_app.py. This provides the GUI interface for login, viewing equipment history, checking out, and returning equipment.

3. Login via QR Code:
Use the Login via QR code button in the application interface. It will communicate with qr_scanner.py to activate the webcam and scan your employee QR code for secure login.

4. Perform Actions:
After login, you can view history, check out or return equipment via intuitive GUI options.

5. Exit:
Use the Exit button to close the application safely.

Notes
The webcam functionality depends on qr_scanner.py running alongside equipflow_app.py for scanning QR codes.

Ensure your BASE_URL in equipflow_app.py is configured to point to the correct Oracle APEX REST API endpoint.
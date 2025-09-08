import cv2

def scan_employee_qr():
    """Open webcam and scan a single QR code, then return its data."""
    # Use CAP_DSHOW for Windows (most stable)
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("❌ Cannot access webcam")
        return None

    detector = cv2.QRCodeDetector()
    emp_id = None

    print("📷 Hold your Employee QR code in front of the camera... (press 'q' to cancel)")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        data, points, _ = detector.detectAndDecode(frame)

        if points is not None:
            points = points[0].astype(int)
            for i in range(len(points)):
                pt1 = tuple(points[i])
                pt2 = tuple(points[(i + 1) % len(points)])
                cv2.line(frame, pt1, pt2, (0, 255, 0), 2)

        cv2.imshow("QR Scanner", frame)

        if data:
            emp_id = data.strip()
            print(f"✅ QR Code detected: {emp_id}")
            cv2.waitKey(500)  # brief pause so the user sees success
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("👋 Scan cancelled")
            break

    cap.release()
    cv2.destroyAllWindows()

    # Important: flush OpenCV events once
    for _ in range(3):
        cv2.waitKey(1)

    return emp_id


# If you run this file directly, test scanner
if __name__ == "__main__":
    emp_id = scan_employee_qr()
    print("Returned employee ID:", emp_id)

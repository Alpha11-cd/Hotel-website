from flask import Flask, render_template, request, jsonify
from datetime import datetime
import os
import json
import smtplib
import ssl
from email.message import EmailMessage

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/rooms')
def rooms():
    return render_template('rooms.html')

@app.route('/amenities')
def amenities():
    return render_template('amenities.html')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

@app.route('/booking')
def booking_page():
    return render_template('booking.html')

@app.route('/airport')
def airport_page():
    return render_template('airport.html')

@app.route('/thankyou')
def thankyou():
    return render_template('thankyou.html')

@app.route('/api/booking', methods=['POST'])
def booking_api():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid submission.'}), 400

    required_fields = ['fullName', 'email', 'phone', 'checkin', 'checkout', 'guests', 'roomType']
    missing = [field for field in required_fields if not data.get(field)]
    if missing:
        return jsonify({'success': False, 'message': f"Missing fields: {', '.join(missing)}"}), 400

    try:
        checkin = datetime.strptime(data['checkin'], '%Y-%m-%d')
        checkout = datetime.strptime(data['checkout'], '%Y-%m-%d')
        if checkout <= checkin:
            raise ValueError('Checkout must be after check-in.')
    except ValueError as err:
        return jsonify({'success': False, 'message': str(err)}), 400

    # Persist booking to a local file for later access
    try:
        save_submission('bookings', data)
    except Exception:
        # don't fail user if persistence has an issue; still return success
        pass
    # Email notification (best-effort)
    try:
        send_email_notification('booking', data)
    except Exception:
        pass

    return jsonify({'success': True, 'message': 'Booking request received successfully.'})

@app.route('/api/airport', methods=['POST'])
def airport_api():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid submission.'}), 400

    required_fields = ['flightNumber', 'arrivalDate', 'arrivalTime', 'passengers', 'pickupLocation', 'vehicle']
    missing = [field for field in required_fields if not data.get(field)]
    if missing:
        return jsonify({'success': False, 'message': f"Missing fields: {', '.join(missing)}"}), 400

    # Persist airport request
    try:
        save_submission('airport', data)
    except Exception:
        pass

    # Email notification (best-effort)
    try:
        send_email_notification('airport', data)
    except Exception:
        pass

    return jsonify({'success': True, 'message': 'Airport pickup request received successfully.'})

@app.route('/api/feedback', methods=['POST'])
def feedback_api():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid submission.'}), 400

    if not data.get('rating'):
        return jsonify({'success': False, 'message': 'Please provide a star rating.'}), 400

    # Persist feedback
    try:
        save_submission('feedback', data)
    except Exception:
        pass

    # Email notification (best-effort)
    try:
        send_email_notification('feedback', data)
    except Exception:
        pass

    return jsonify({'success': True, 'message': 'Thank you for your feedback.'})


def save_submission(kind: str, data: dict):
    """Append a JSON line to data/<kind>.jsonl with a timestamp."""
    data_dir = os.path.join(app.root_path, 'data')
    os.makedirs(data_dir, exist_ok=True)
    filename = os.path.join(data_dir, f"{kind}.jsonl")
    record = {
        'timestamp': datetime.utcnow().isoformat(),
        'data': data
    }
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(json.dumps(record, default=str, ensure_ascii=False) + "\n")


def send_email_notification(kind: str, data: dict):
    """Send a simple email notification with the submission contents.

    Configure via environment variables:
      SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD
      EMAIL_FROM (optional), ADMIN_EMAIL (optional)

    If these are not set the function will be a no-op.
    """
    smtp_host = os.environ.get('SMTP_HOST')
    smtp_port = os.environ.get('SMTP_PORT')
    smtp_user = os.environ.get('SMTP_USER')
    smtp_pass = os.environ.get('SMTP_PASSWORD')
    email_from = os.environ.get('EMAIL_FROM', smtp_user)
    admin_email = os.environ.get('ADMIN_EMAIL', 'naitik022511@gmail.com')

    if not (smtp_host and smtp_port and smtp_user and smtp_pass and email_from):
        # SMTP not configured; skip sending
        return

    subject_map = {
        'booking': 'New booking submitted',
        'airport': 'New airport pickup request',
        'feedback': 'New feedback received'
    }
    subject = subject_map.get(kind, 'New submission received')

    msg = EmailMessage()
    msg['From'] = email_from
    msg['To'] = admin_email
    msg['Subject'] = subject

    body_lines = [f"Timestamp: {datetime.utcnow().isoformat()}", f"Type: {kind}", "", "Submission:"]
    try:
        body_lines.append(json.dumps(data, indent=2, default=str))
    except Exception:
        body_lines.append(str(data))

    msg.set_content('\n'.join(body_lines))

    context = ssl.create_default_context()
    port = int(smtp_port)
    # try SMTP over TLS on the configured port
    with smtplib.SMTP(smtp_host, port, timeout=10) as server:
        server.starttls(context=context)
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)

if __name__ == '__main__':
    app.run(debug=True)

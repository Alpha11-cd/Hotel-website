from flask import Flask, render_template, request, jsonify
from datetime import datetime

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

    return jsonify({'success': True, 'message': 'Airport pickup request received successfully.'})

@app.route('/api/feedback', methods=['POST'])
def feedback_api():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid submission.'}), 400

    if not data.get('rating'):
        return jsonify({'success': False, 'message': 'Please provide a star rating.'}), 400

    return jsonify({'success': True, 'message': 'Thank you for your feedback.'})

if __name__ == '__main__':
    app.run(debug=True)

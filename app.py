import os
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
from flask_compress import Compress
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_folder='static', template_folder='templates')
Compress(app)
# IMPORTANT: change this secret key for production; keep it secret
app.secret_key = os.environ.get('AXIS_SECRET') or 'dev-secret-key-please-change'

DATA_DIR = 'data'
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
FEEDBACK_FILE = os.path.join(DATA_DIR, 'feedback.json')
BOOKINGS_FILE = os.path.join(DATA_DIR, 'bookings.json')
GITHUB_REPO_URL = os.environ.get('DEVELOPER_GITHUB_URL', 'https://github.com/Ravi-Patel-Builds/Auto-connect')

ROUTES = [
    {'id': 'axis-rooma', 'name': 'Axis College → Rooma', 'pickup': 'Axis College', 'dropoff': 'Rooma', 'fare': 45},
    {'id': 'axis-city', 'name': 'Axis College → Kanpur City', 'pickup': 'Axis College', 'dropoff': 'Kanpur City', 'fare': 80},
    {'id': 'axis-mall', 'name': 'Axis College → City Mall', 'pickup': 'Axis College', 'dropoff': 'City Mall', 'fare': 65}
]

FAKE_DRIVERS = [
    {'id': 'd1', 'name': 'Rajesh Kumar', 'auto_number': 'UP78 AB 1234', 'rating': 4.9, 'routes': ['axis-rooma', 'axis-city'], 'experience': '5 years', 'phone': '+91 98765 12345'},
    {'id': 'd2', 'name': 'Amit Singh', 'auto_number': 'UP78 CD 5678', 'rating': 4.7, 'routes': ['axis-rooma', 'axis-mall'], 'experience': '3 years', 'phone': '+91 98765 67890'},
    {'id': 'd3', 'name': 'Sunita Devi', 'auto_number': 'UP78 EF 9012', 'rating': 4.8, 'routes': ['axis-city', 'axis-mall'], 'experience': '4 years', 'phone': '+91 98765 43210'}
]

FAKE_PASSENGERS = [
    {'id': 'p1', 'name': 'Sneha Sharma', 'roll_no': 'AX1234', 'pickup': 'Axis College', 'dropoff': 'Rooma', 'route_id': 'axis-rooma', 'notes': 'Evening ride', 'status': 'waiting', 'phone': '+91 91234 56789'},
    {'id': 'p2', 'name': 'Karan Patel', 'roll_no': 'AX5678', 'pickup': 'Axis College', 'dropoff': 'City Mall', 'route_id': 'axis-mall', 'notes': 'Weekend shopping', 'status': 'waiting', 'phone': '+91 92345 67890'},
    {'id': 'p3', 'name': 'Nisha Verma', 'roll_no': 'AX9012', 'pickup': 'Axis College', 'dropoff': 'Kanpur City', 'route_id': 'axis-city', 'notes': 'Home drop', 'status': 'waiting', 'phone': '+91 93456 78901'}
]

# Ensure data dir and files
os.makedirs(DATA_DIR, exist_ok=True)
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump({}, f)
if not os.path.exists(FEEDBACK_FILE):
    open(FEEDBACK_FILE, 'a', encoding='utf-8').close()
if not os.path.exists(BOOKINGS_FILE):
    with open(BOOKINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f)

def load_users():
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except:
            return {}

def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def load_feedback():
    feedbacks = []
    if os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    feedbacks.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return feedbacks

def load_bookings():
    if not os.path.exists(BOOKINGS_FILE):
        return []
    with open(BOOKINGS_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except:
            return []

def save_bookings(bookings):
    with open(BOOKINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(bookings, f, ensure_ascii=False, indent=2)

def get_route(route_id):
    return next((route for route in ROUTES if route['id'] == route_id), None)

def get_drivers_for_route(route_id):
    return [driver for driver in FAKE_DRIVERS if route_id in driver['routes']]

def get_passengers_for_route(route_id):
    return [passenger for passenger in FAKE_PASSENGERS if passenger['route_id'] == route_id and passenger['status'] == 'waiting']

@app.route('/')
def home():
    user = session.get('user_email')
    return render_template('home.html', user=user)

# AUTH: Signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        role = request.form.get('role', 'student')
        if not email or not password:
            return render_template('signup.html', error='Email and password required.')
        users = load_users()
        if email in users:
            return render_template('signup.html', error='Account already exists.')
        users[email] = {
            'password_hash': generate_password_hash(password),
            'role': role,
            'created_at': datetime.utcnow().isoformat()
        }
        save_users(users)
        session['user_email'] = email
        session['user_role'] = role
        return redirect(url_for('dashboard'))
    return render_template('signup.html')

# AUTH: Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        users = load_users()
        user = users.get(email)
        if user and check_password_hash(user.get('password_hash',''), password):
            session['user_email'] = email
            session['user_role'] = user.get('role','student')
            return redirect(url_for('dashboard'))
        return render_template('login.html', error='Invalid credentials.')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_email' not in session:
        return redirect(url_for('login'))

    user = session['user_email']
    role = session['user_role']
    route_availability = []
    for route in ROUTES:
        drivers = get_drivers_for_route(route['id'])
        passengers = get_passengers_for_route(route['id'])
        route_availability.append({
            'route': route,
            'driver_count': len(drivers),
            'passenger_count': len(passengers),
            'drivers': drivers,
            'passengers': passengers
        })

    if role == 'student':
        return render_template(
            'dashboard.html',
            user=user,
            role=role,
            route_availability=route_availability,
            drivers=FAKE_DRIVERS,
            routes=ROUTES
        )

    return render_template(
        'dashboard.html',
        user=user,
        role=role,
        route_availability=route_availability,
        passengers=FAKE_PASSENGERS,
        drivers=FAKE_DRIVERS,
        routes=ROUTES
    )

@app.route('/book', methods=['GET', 'POST'])
def book():
    if 'user_email' not in session:
        return redirect(url_for('login'))

    role = session['user_role']
    bookings = load_bookings()
    message = None
    booking = None

    if request.method == 'POST':
        if role == 'student':
            route_id = request.form.get('route_id')
            driver_id = request.form.get('driver_id')
            pickup = request.form.get('pickup', '').strip()
            dropoff = request.form.get('dropoff', '').strip()
            route = get_route(route_id)
            driver = next((d for d in FAKE_DRIVERS if d['id'] == driver_id), None)
            if route and driver and pickup and dropoff:
                booking = {
                    'id': f'bk{len(bookings) + 1}',
                    'type': 'student',
                    'user_email': session['user_email'],
                    'route': route['name'],
                    'pickup': pickup,
                    'dropoff': dropoff,
                    'driver': driver['name'],
                    'auto_number': driver['auto_number'],
                    'fare': route['fare'],
                    'status': 'confirmed',
                    'timestamp': datetime.utcnow().isoformat()
                }
                bookings.append(booking)
                save_bookings(bookings)
                message = 'Ride booked successfully. Driver will connect with you shortly.'
        else:
            passenger_id = request.form.get('passenger_id')
            driver_id = request.form.get('driver_id')
            passenger = next((p for p in FAKE_PASSENGERS if p['id'] == passenger_id), None)
            driver = next((d for d in FAKE_DRIVERS if d['id'] == driver_id), None)
            if passenger and driver:
                booking = {
                    'id': f'bk{len(bookings) + 1}',
                    'type': 'driver',
                    'user_email': session['user_email'],
                    'route': get_route(passenger['route_id'])['name'],
                    'pickup': passenger['pickup'],
                    'dropoff': passenger['dropoff'],
                    'passenger': passenger['name'],
                    'roll_no': passenger['roll_no'],
                    'driver': driver['name'],
                    'auto_number': driver['auto_number'],
                    'fare': get_route(passenger['route_id'])['fare'],
                    'status': 'accepted',
                    'timestamp': datetime.utcnow().isoformat()
                }
                bookings.append(booking)
                save_bookings(bookings)
                passenger['status'] = 'accepted'
                message = 'Passenger request accepted. You can now coordinate the ride details.'

    if role == 'student':
        return render_template(
            'booking.html',
            role=role,
            routes=ROUTES,
            drivers=FAKE_DRIVERS,
            message=message,
            booking=booking
        )

    return render_template(
        'booking.html',
        role=role,
        routes=ROUTES,
        passengers=[p for p in FAKE_PASSENGERS if p['status'] == 'waiting'],
        drivers=FAKE_DRIVERS,
        message=message,
        booking=booking
    )

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# Feedback route (ajax or form)
@app.route('/feedback', methods=['GET','POST'])
def feedback():
    if request.method == 'POST':
        data = {
            'name': request.form.get('name','').strip(),
            'email': request.form.get('email','').strip(),
            'role': request.form.get('role','').strip(),
            'rating': request.form.get('rating','').strip(),
            'message': request.form.get('message','').strip(),
            'timestamp': datetime.utcnow().isoformat()
        }
        with open(FEEDBACK_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False) + '\n')
        # Return JSON for AJAX submit
        return jsonify(status='success', message='Feedback received.')
    return render_template('feedback.html')

@app.route('/feedbacks')
def feedbacks():
    feedback_list = load_feedback()
    return render_template('feedback_list.html', feedbacks=feedback_list)

@app.route('/developer')
def developer():
    return render_template('developer.html', github_repo_url=GITHUB_REPO_URL)

@app.route('/onboarding')
def onboarding():
    return render_template('onboarding.html')

@app.route('/privacy')
def privacy_policy():
    return render_template('privacy.html')

@app.route('/terms')
def terms_of_service():
    return render_template('terms.html')

# sitemap.xml generator route
@app.route('/sitemap.xml')
def sitemap():
    pages = []
    pages.append({'loc': request.url_root.rstrip('/') + url_for('home'), 'changefreq': 'daily', 'priority': '0.9'})
    pages.append({'loc': request.url_root.rstrip('/') + url_for('login'), 'changefreq': 'monthly', 'priority': '0.6'})
    pages.append({'loc': request.url_root.rstrip('/') + url_for('signup'), 'changefreq': 'monthly', 'priority': '0.6'})
    pages.append({'loc': request.url_root.rstrip('/') + url_for('privacy_policy'), 'changefreq': 'yearly', 'priority': '0.4'})
    pages.append({'loc': request.url_root.rstrip('/') + url_for('terms_of_service'), 'changefreq': 'yearly', 'priority': '0.4'})
    sitemap_xml = render_template('sitemap_template.xml', pages=pages)
    return app.response_class(sitemap_xml, mimetype='application/xml')

# robots.txt served from static
@app.route('/robots.txt')
def robots():
    return send_from_directory(app.static_folder, 'robots.txt')

# mock upcoming AI features API (for demo)
@app.route('/api/upcoming-ai')
def api_ai():
    features = [
        "AI-powered ride scheduling",
        "Voice booking assistant",
        "Predictive wait time analytics",
        "Driver heatmaps and routing optimization"
    ]
    return jsonify({'features': features})

if __name__ == '__main__':
    app.run(debug=True)

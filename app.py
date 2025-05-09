import os
import logging
from datetime import datetime, date
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key")

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///travelagency.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Define models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    full_name = db.Column(db.String(150))
    active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def is_active(self):
        return self.active

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    mobile = db.Column(db.String(20))
    email = db.Column(db.String(120))
    id_type = db.Column(db.String(20))
    id_number = db.Column(db.String(30))
    nationality = db.Column(db.String(50))
    birth_date = db.Column(db.Date)
    gender = db.Column(db.String(10))
    address = db.Column(db.String(200))
    id_issue_date = db.Column(db.Date)
    id_expiry_date = db.Column(db.Date)
    id_issue_place = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bookings = db.relationship('BusBooking', backref='customer', lazy=True)

class TransportCompany(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True)
    contact_person = db.Column(db.String(100))
    contact_number = db.Column(db.String(20))
    email = db.Column(db.String(120))
    address = db.Column(db.String(200))
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bus_routes = db.relationship('BusRoute', backref='company', lazy=True)

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), default="المملكة العربية السعودية")
    code = db.Column(db.String(10))
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    departures = db.relationship('BusRoute', foreign_keys='BusRoute.departure_city_id', backref='departure_city', lazy=True)
    destinations = db.relationship('BusRoute', foreign_keys='BusRoute.destination_city_id', backref='destination_city', lazy=True)

class BusRoute(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    departure_city_id = db.Column(db.Integer, db.ForeignKey('city.id'), nullable=False)
    destination_city_id = db.Column(db.Integer, db.ForeignKey('city.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('transport_company.id'), nullable=False)
    route_code = db.Column(db.String(20))
    distance = db.Column(db.Float)  # in kilometers
    duration = db.Column(db.Integer)  # in minutes
    base_price = db.Column(db.Float)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    schedules = db.relationship('BusSchedule', backref='route', lazy=True)

class BusType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    code = db.Column(db.String(20))
    description = db.Column(db.Text)
    seat_capacity = db.Column(db.Integer)
    has_wifi = db.Column(db.Boolean, default=False)
    has_ac = db.Column(db.Boolean, default=True)
    has_toilet = db.Column(db.Boolean, default=False)
    is_vip = db.Column(db.Boolean, default=False)
    price_multiplier = db.Column(db.Float, default=1.0)  # Factor to multiply base route price
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    schedules = db.relationship('BusSchedule', backref='bus_type', lazy=True)

class BusSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.Integer, db.ForeignKey('bus_route.id'), nullable=False)
    bus_type_id = db.Column(db.Integer, db.ForeignKey('bus_type.id'), nullable=False)
    departure_time = db.Column(db.Time, nullable=False)
    arrival_time = db.Column(db.Time)
    days_of_week = db.Column(db.String(20))  # e.g., "1,2,3,4,5" for weekdays
    price = db.Column(db.Float)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    trips = db.relationship('BusTrip', backref='schedule', lazy=True)

class BusTrip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey('bus_schedule.id'), nullable=False)
    trip_date = db.Column(db.Date, nullable=False)
    bus_number = db.Column(db.String(20))
    driver_name = db.Column(db.String(100))
    driver_contact = db.Column(db.String(20))
    available_seats = db.Column(db.Integer)
    status = db.Column(db.String(20), default="scheduled")  # scheduled, in-progress, completed, cancelled
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - without backref to avoid conflicts
    bookings = db.relationship('BusBooking', foreign_keys='BusBooking.trip_id', lazy=True)
    return_bookings = db.relationship('BusBooking', foreign_keys='BusBooking.return_trip_id', lazy=True)

class BusBooking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_number = db.Column(db.String(20), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BookingPayment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bus_booking.id'), nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)
    reference_number = db.Column(db.String(50))
    account = db.Column(db.String(50))  # cash-register, bank-account, etc.
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    booking = db.relationship('BusBooking', backref='payments')
    user = db.relationship('User', foreign_keys=[created_by])

# Create all tables
with app.app_context():
    db.create_all()

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
@app.route('/login')
def login():
    # Redirect directly to dashboard for now
    return render_template('dashboard.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/airline-tickets')
def airline_tickets():
    return render_template('airline-tickets.html')

@app.route('/bus-tickets')
def bus_tickets():
    # Get data for dropdowns
    cities = City.query.filter_by(is_active=True).all()
    companies = TransportCompany.query.filter_by(is_active=True).all()
    bus_types = BusType.query.filter_by(is_active=True).all()
    
    # Get recent bookings for the table (with minimal fields now)
    recent_bookings = BusBooking.query.order_by(BusBooking.created_at.desc()).limit(10).all()
    
    return render_template('bus-tickets.html', 
                          cities=cities,
                          companies=companies,
                          bus_types=bus_types,
                          bookings=recent_bookings)

@app.route('/api/bus-routes', methods=['GET'])
def get_bus_routes():
    departure_city_id = request.args.get('departure_city_id')
    destination_city_id = request.args.get('destination_city_id')
    
    # Query routes based on cities
    query = BusRoute.query.filter_by(is_active=True)
    
    if departure_city_id:
        query = query.filter_by(departure_city_id=departure_city_id)
    if destination_city_id:
        query = query.filter_by(destination_city_id=destination_city_id)
    
    routes = query.all()
    
    # Format for JSON response
    routes_data = [{
        'id': route.id,
        'departure_city': route.departure_city.name,
        'destination_city': route.destination_city.name,
        'company': route.company.name,
        'duration': route.duration,
        'base_price': route.base_price
    } for route in routes]
    
    return jsonify(routes_data)

@app.route('/api/bus-schedules', methods=['GET'])
def get_bus_schedules():
    route_id = request.args.get('route_id')
    date = request.args.get('date')
    
    if not route_id:
        return jsonify({'error': 'Route ID is required'}), 400
    
    # Query schedules for the route
    schedules = BusSchedule.query.filter_by(route_id=route_id, is_active=True).all()
    
    # Format for JSON response
    schedules_data = [{
        'id': schedule.id,
        'departure_time': schedule.departure_time.strftime('%H:%M'),
        'arrival_time': schedule.arrival_time.strftime('%H:%M') if schedule.arrival_time else None,
        'bus_type': schedule.bus_type.name,
        'price': schedule.price,
        'available_seats': 'Available' if schedule.is_active else 'Full'
    } for schedule in schedules]
    
    return jsonify(schedules_data)

@app.route('/api/create-bus-booking', methods=['POST'])
def create_bus_booking():
    try:
        # Get form data
        data = request.form
        logging.debug(f"Received booking data: {data}")
        
        # Basic validation
        required_fields = ['passengerName', 'sellPrice']
        
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False, 
                    'error': f'الحقل المطلوب {field} غير موجود'
                }), 400
        
        # Check if customer already exists by ID number
        id_number = data.get('idNumber')
        existing_customer = None
        
        if id_number:
            existing_customer = Customer.query.filter_by(id_number=id_number).first()
        
        if existing_customer:
            customer = existing_customer
            # Update customer information if provided
            if data.get('passengerName'):
                customer.full_name = data.get('passengerName')
            if data.get('mobileNumber'):
                customer.mobile = data.get('mobileNumber')
            if data.get('nationality'):
                customer.nationality = data.get('nationality')
            # Add more field updates as needed
        else:
            # Parse date fields properly
            birth_date = None
            issue_date = None
            
            try:
                birth_date_str = data.get('birthDate', '')
                if birth_date_str and isinstance(birth_date_str, str) and birth_date_str.strip():
                    birth_date = datetime.strptime(birth_date_str, '%d  %B , %Y').date()
            except ValueError:
                logging.warning(f"Invalid birth date format: {data.get('birthDate')}")
            
            try:
                issue_date_str = data.get('issueDate', '')
                if issue_date_str and isinstance(issue_date_str, str) and issue_date_str.strip():
                    issue_date = datetime.strptime(issue_date_str, '%d  %B , %Y').date()
            except ValueError:
                logging.warning(f"Invalid issue date format: {data.get('issueDate')}")
            
            # Create new customer record
            customer = Customer()
            customer.full_name = data.get('passengerName')
            customer.mobile = data.get('mobileNumber')
            customer.id_type = data.get('idType')
            customer.id_number = id_number
            customer.nationality = data.get('nationality')
            customer.birth_date = birth_date
            customer.gender = data.get('gender')
            customer.id_issue_date = issue_date
            customer.id_issue_place = data.get('issuePlace')
            customer.notes = data.get('notes')
            
            db.session.add(customer)
        
        # Find or create bus trip
        departure_city_id = None
        destination_city_id = None
        
        # Convert city name to ID
        departure_city_name = data.get('departureCity')
        destination_city_name = data.get('destinationCity')
        
        if departure_city_name:
            departure_city = City.query.filter_by(name=departure_city_name).first()
            if not departure_city:
                # Try to find by value instead of name
                cities = City.query.all()
                for city in cities:
                    if city.id == int(departure_city_name) if departure_city_name.isdigit() else False:
                        departure_city = city
                        break
            
            if departure_city:
                departure_city_id = departure_city.id
        
        if destination_city_name:
            destination_city = City.query.filter_by(name=destination_city_name).first()
            if not destination_city:
                # Try to find by value instead of name
                cities = City.query.all()
                for city in cities:
                    if city.id == int(destination_city_name) if destination_city_name.isdigit() else False:
                        destination_city = city
                        break
            
            if destination_city:
                destination_city_id = destination_city.id
        
        # Find bus route based on departure and destination
        bus_route = None
        if departure_city_id and destination_city_id:
            bus_route = BusRoute.query.filter_by(
                departure_city_id=departure_city_id,
                destination_city_id=destination_city_id
            ).first()
        
        if not bus_route:
            # Just use the first route as a fallback for testing
            bus_route = BusRoute.query.first()
            if not bus_route:
                return jsonify({
                    'success': False,
                    'error': 'لا توجد مسارات باص متاحة. يرجى إضافة مسارات أولاً.'
                }), 400
        
        # Find a bus schedule for this route
        bus_schedule = BusSchedule.query.filter_by(route_id=bus_route.id).first()
        if not bus_schedule:
            return jsonify({
                'success': False,
                'error': 'لا توجد جداول زمنية متاحة لهذا المسار.'
            }), 400
        
        # Parse reservation date
        travel_date = None
        try:
            reservation_date_str = data.get('reservationDate', '')
            if reservation_date_str and isinstance(reservation_date_str, str) and reservation_date_str.strip():
                travel_date = datetime.strptime(reservation_date_str, '%d  %B , %Y').date()
                # If parsing fails, use today's date
                if not travel_date:
                    travel_date = date.today()
            else:
                travel_date = date.today()
        except ValueError:
            logging.warning(f"Invalid reservation date format: {data.get('reservationDate')}")
            travel_date = date.today()
        
        # Create or find a trip for this schedule on the given date
        trip = BusTrip.query.filter_by(
            schedule_id=bus_schedule.id,
            trip_date=travel_date
        ).first()
        
        if not trip:
            # Create a new trip
            trip = BusTrip()
            trip.schedule_id = bus_schedule.id
            trip.trip_date = travel_date
            trip.bus_number = f"BUS-{bus_schedule.id}-{travel_date.strftime('%Y%m%d')}"
            trip.available_seats = bus_schedule.bus_type.seat_capacity if bus_schedule.bus_type else 45
            trip.status = 'scheduled'
            
            db.session.add(trip)
        
        # Create a unique booking number
        booking_count = BusBooking.query.count()
        booking_number = f"BUS-{booking_count + 1:06d}"
        
        # Get ticket price from form or use schedule price
        ticket_price = 0
        try:
            ticket_price = float(data.get('sellPrice', 0))
        except ValueError:
            ticket_price = bus_schedule.price or 100
        
        # Create booking record with minimal fields
        booking = BusBooking()
        booking.booking_number = booking_number
        
        # Add minimal booking to the database
        db.session.add(booking)
        
        # Commit all changes
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'booking_id': booking.id, 
            'booking_number': booking.booking_number
        })
    
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating booking: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/bus-tickets-new')
def bus_tickets_new():
    return render_template('bus-tickets-new.html')

@app.route('/new-bus-booking')
def new_bus_booking():
    # في المستقبل يمكن استرجاع العملات من قاعدة البيانات هنا
    currencies = [
        {"id": "SAR", "name": "ريال سعودي (SAR)"},
        {"id": "USD", "name": "دولار أمريكي (USD)"},
        {"id": "EUR", "name": "يورو (EUR)"},
        {"id": "YER", "name": "ريال يمني (YER)"}
    ]
    
    # ارسال قائمة العملات والبيانات الأخرى اللازمة للنموذج
    return render_template('new_bus_booking.html', currencies=currencies)

@app.route('/work-visa')
def work_visa():
    return render_template('work-visa.html')

@app.route('/family-visit')
def family_visit():
    return render_template('family-visit.html')

@app.route('/umrah-visa')
def umrah_visa():
    return render_template('umrah-visa.html')

@app.route('/umrah-guarantee')
def umrah_guarantee():
    return render_template('umrah-guarantee.html')

@app.route('/mail-tracking')
def mail_tracking():
    return render_template('mail-tracking.html')

@app.route('/customers')
def customers():
    return render_template('customers.html')

@app.route('/suppliers')
def suppliers():
    return render_template('suppliers.html')

@app.route('/banks')
def banks():
    return render_template('banks.html')

@app.route('/payment-vouchers')
def payment_vouchers():
    return render_template('payment-vouchers.html')

@app.route('/receipt-vouchers')
def receipt_vouchers():
    return render_template('receipt-vouchers.html')

@app.route('/receipts')
def receipts():
    return render_template('receipts.html')

@app.route('/users')
def users():
    return render_template('users.html')

@app.route('/currencies')
def currencies():
    return render_template('currencies.html')

@app.route('/reports')
def reports():
    return render_template('reports.html')

@app.route('/budget-profits')
def budget_profits():
    return render_template('budget-profits.html')

@app.route('/cash-journal')
def cash_journal():
    return render_template('cash-journal.html')

@app.route('/bank-journal')
def bank_journal():
    return render_template('bank-journal.html')

@app.route('/countries-cities')
def countries_cities():
    return render_template('countries-cities.html')

@app.route('/id-types')
def id_types():
    return render_template('id-types.html')

@app.route('/daily-journal')
def daily_journal():
    return render_template('daily-journal.html')

@app.route('/employees')
def employees():
    return render_template('employees.html')

@app.route('/account-statements')
def account_statements():
    return render_template('account-statements.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

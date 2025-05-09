from app import db
from flask_login import UserMixin
from datetime import datetime


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    full_name = db.Column(db.String(150))
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


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
    
    # Relationships
    bookings = db.relationship('BusBooking', backref='trip', lazy=True)


class BusBooking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_number = db.Column(db.String(20), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    trip_id = db.Column(db.Integer, db.ForeignKey('bus_trip.id'))
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    travel_date = db.Column(db.Date, nullable=False)
    seat_number = db.Column(db.String(10))
    is_round_trip = db.Column(db.Boolean, default=False)
    return_trip_id = db.Column(db.Integer, db.ForeignKey('bus_trip.id'))
    return_date = db.Column(db.Date)
    return_seat_number = db.Column(db.String(10))
    ticket_price = db.Column(db.Float, nullable=False)
    discount_amount = db.Column(db.Float, default=0)
    total_amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(20))
    payment_status = db.Column(db.String(20), default="pending")  # pending, partial, paid
    booking_status = db.Column(db.String(20), default="confirmed")  # confirmed, cancelled, completed
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    return_trip = db.relationship('BusTrip', foreign_keys=[return_trip_id])
    created_user = db.relationship('User', foreign_keys=[created_by])


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
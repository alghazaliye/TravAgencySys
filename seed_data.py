from datetime import datetime, date, time, timedelta
from werkzeug.security import generate_password_hash
from app import app, db
from app import User, Customer, TransportCompany, City, BusRoute, BusType, BusSchedule
from seed_id_types import seed_identity_types

def seed_database():
    """Populate the database with initial data for testing and demo purposes."""
    with app.app_context():
        # Create admin user
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@example.com',
                password_hash=generate_password_hash('admin123'),
                full_name='System Administrator',
                active=True,
                is_admin=True
            )
            db.session.add(admin)
            
        # Create cities
        cities_data = [
            {'name': 'الرياض', 'code': 'RUH'},
            {'name': 'مكة المكرمة', 'code': 'MKH'},
            {'name': 'المدينة المنورة', 'code': 'MDN'},
            {'name': 'جدة', 'code': 'JED'},
            {'name': 'الدمام', 'code': 'DMM'},
            {'name': 'الطائف', 'code': 'TIF'},
            {'name': 'أبها', 'code': 'ABH'}
        ]
        
        for city_data in cities_data:
            if not City.query.filter_by(name=city_data['name']).first():
                city = City(
                    name=city_data['name'],
                    code=city_data['code'],
                    country='المملكة العربية السعودية',
                    is_active=True
                )
                db.session.add(city)
        
        # Create transport companies
        companies_data = [
            {
                'name': 'الشركة السعودية للنقل الجماعي (سابتكو)',
                'code': 'SAPTCO',
                'contact_person': 'محمد العبدالله',
                'contact_number': '0512345678',
                'email': 'info@saptco.example.com'
            },
            {
                'name': 'شركة الراجحي للنقل',
                'code': 'RAJHI',
                'contact_person': 'أحمد الراجحي',
                'contact_number': '0523456789',
                'email': 'info@rajhi.example.com'
            },
            {
                'name': 'شركة المجيد للنقل',
                'code': 'MAJID',
                'contact_person': 'خالد المجيد',
                'contact_number': '0534567890',
                'email': 'info@almajid.example.com'
            }
        ]
        
        for company_data in companies_data:
            if not TransportCompany.query.filter_by(name=company_data['name']).first():
                company = TransportCompany(
                    name=company_data['name'],
                    code=company_data['code'],
                    contact_person=company_data['contact_person'],
                    contact_number=company_data['contact_number'],
                    email=company_data['email'],
                    is_active=True
                )
                db.session.add(company)
        
        # Commit the cities and companies so we can reference them
        db.session.commit()
        
        # Create bus types
        bus_types_data = [
            {
                'name': 'سياحي فاخر',
                'code': 'VIP',
                'description': 'باص سياحي فاخر مع خدمات ممتازة',
                'seat_capacity': 45,
                'has_wifi': True,
                'has_ac': True,
                'has_toilet': True,
                'is_vip': True,
                'price_multiplier': 1.5
            },
            {
                'name': 'سياحي',
                'code': 'TOURISM',
                'description': 'باص سياحي عادي',
                'seat_capacity': 50,
                'has_wifi': True,
                'has_ac': True,
                'has_toilet': True,
                'is_vip': False,
                'price_multiplier': 1.0
            },
            {
                'name': 'عادي',
                'code': 'REGULAR',
                'description': 'باص نقل عادي',
                'seat_capacity': 60,
                'has_wifi': False,
                'has_ac': True,
                'has_toilet': False,
                'is_vip': False,
                'price_multiplier': 0.8
            }
        ]
        
        for bus_type_data in bus_types_data:
            if not BusType.query.filter_by(name=bus_type_data['name']).first():
                bus_type = BusType(
                    name=bus_type_data['name'],
                    code=bus_type_data['code'],
                    description=bus_type_data['description'],
                    seat_capacity=bus_type_data['seat_capacity'],
                    has_wifi=bus_type_data['has_wifi'],
                    has_ac=bus_type_data['has_ac'],
                    has_toilet=bus_type_data['has_toilet'],
                    is_vip=bus_type_data['is_vip'],
                    price_multiplier=bus_type_data['price_multiplier'],
                    is_active=True
                )
                db.session.add(bus_type)
        
        # Commit the bus types
        db.session.commit()
        
        # Create routes between major cities
        routes_data = [
            {
                'departure_city_name': 'الرياض',
                'destination_city_name': 'مكة المكرمة',
                'company_name': 'الشركة السعودية للنقل الجماعي (سابتكو)',
                'distance': 950,
                'duration': 540,  # 9 hours in minutes
                'base_price': 150
            },
            {
                'departure_city_name': 'الرياض',
                'destination_city_name': 'المدينة المنورة',
                'company_name': 'الشركة السعودية للنقل الجماعي (سابتكو)',
                'distance': 850,
                'duration': 480,  # 8 hours in minutes
                'base_price': 140
            },
            {
                'departure_city_name': 'جدة',
                'destination_city_name': 'المدينة المنورة',
                'company_name': 'شركة الراجحي للنقل',
                'distance': 420,
                'duration': 240,  # 4 hours in minutes
                'base_price': 80
            },
            {
                'departure_city_name': 'الدمام',
                'destination_city_name': 'الرياض',
                'company_name': 'شركة المجيد للنقل',
                'distance': 400,
                'duration': 240,  # 4 hours in minutes
                'base_price': 75
            },
            {
                'departure_city_name': 'جدة',
                'destination_city_name': 'مكة المكرمة',
                'company_name': 'شركة الراجحي للنقل',
                'distance': 80,
                'duration': 60,  # 1 hour in minutes
                'base_price': 40
            }
        ]
        
        for route_data in routes_data:
            departure_city = City.query.filter_by(name=route_data['departure_city_name']).first()
            destination_city = City.query.filter_by(name=route_data['destination_city_name']).first()
            company = TransportCompany.query.filter_by(name=route_data['company_name']).first()
            
            if not BusRoute.query.filter_by(
                departure_city_id=departure_city.id,
                destination_city_id=destination_city.id,
                company_id=company.id
            ).first():
                route = BusRoute(
                    departure_city_id=departure_city.id,
                    destination_city_id=destination_city.id,
                    company_id=company.id,
                    route_code=f"{departure_city.code}-{destination_city.code}",
                    distance=route_data['distance'],
                    duration=route_data['duration'],
                    base_price=route_data['base_price'],
                    is_active=True
                )
                db.session.add(route)
        
        # Commit the routes
        db.session.commit()
        
        # Create schedules for routes
        for route in BusRoute.query.all():
            # Morning departures
            morning_time = time(6, 0)  # 6:00 AM
            
            # Afternoon departures
            afternoon_time = time(14, 0)  # 2:00 PM
            
            # Evening departures
            evening_time = time(22, 0)  # 10:00 PM
            
            for bus_type in BusType.query.all():
                # Calculate price based on route base price and bus type multiplier
                price = route.base_price * bus_type.price_multiplier
                
                # Add schedule for each departure time
                for departure_time in [morning_time, afternoon_time, evening_time]:
                    # Calculate arrival time based on route duration
                    # Note: This is a simple calculation and doesn't handle crossing days
                    hours = route.duration // 60
                    minutes = route.duration % 60
                    arrival_time_dt = datetime.combine(date.today(), departure_time) + timedelta(hours=hours, minutes=minutes)
                    arrival_time = arrival_time_dt.time()
                    
                    # Monday to Friday schedule
                    if not BusSchedule.query.filter_by(
                        route_id=route.id,
                        bus_type_id=bus_type.id,
                        departure_time=departure_time,
                        days_of_week="1,2,3,4,5"
                    ).first():
                        schedule = BusSchedule(
                            route_id=route.id,
                            bus_type_id=bus_type.id,
                            departure_time=departure_time,
                            arrival_time=arrival_time,
                            days_of_week="1,2,3,4,5",  # Monday to Friday
                            price=price,
                            is_active=True
                        )
                        db.session.add(schedule)
                    
                    # Weekend schedule (only for popular routes)
                    if departure_time in [morning_time, afternoon_time] and route.base_price > 70:
                        if not BusSchedule.query.filter_by(
                            route_id=route.id,
                            bus_type_id=bus_type.id,
                            departure_time=departure_time,
                            days_of_week="6,7"
                        ).first():
                            schedule = BusSchedule(
                                route_id=route.id,
                                bus_type_id=bus_type.id,
                                departure_time=departure_time,
                                arrival_time=arrival_time,
                                days_of_week="6,7",  # Saturday and Sunday
                                price=price * 1.1,  # 10% higher for weekends
                                is_active=True
                            )
                            db.session.add(schedule)
        
        # Commit all data
        db.session.commit()
        print("Database seeded successfully!")

if __name__ == "__main__":
    seed_database()
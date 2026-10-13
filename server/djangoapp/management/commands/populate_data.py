"""
Django management command to populate database with sample data
Run this command: python manage.py populate_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from djangoapp.models import CarMake, CarModel, Dealer, Review
from datetime import date


class Command(BaseCommand):
    help = 'Populate database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Populating database with sample data...')

        # Create car makes
        car_makes_data = [
            {'name': 'Toyota', 'description': 'Japanese automobile manufacturer'},
            {'name': 'Honda', 'description': 'Japanese automobile manufacturer'},
            {'name': 'Ford', 'description': 'American automobile manufacturer'},
            {'name': 'Chevrolet', 'description': 'American automobile manufacturer'},
            {'name': 'BMW', 'description': 'German luxury automobile manufacturer'},
            {'name': 'Mercedes-Benz', 'description': 'German luxury automobile manufacturer'},
            {'name': 'Nissan', 'description': 'Japanese automobile manufacturer'},
            {'name': 'Volkswagen', 'description': 'German automobile manufacturer'},
        ]

        for make_data in car_makes_data:
            CarMake.objects.get_or_create(name=make_data['name'], defaults=make_data)
        self.stdout.write(self.style.SUCCESS(f'Created {len(car_makes_data)} car makes'))

        # Create car models
        car_models_data = [
            {'make': 'Toyota', 'name': 'Camry', 'car_type': 'Sedan', 'year': 2023},
            {'make': 'Toyota', 'name': 'RAV4', 'car_type': 'SUV', 'year': 2023},
            {'make': 'Toyota', 'name': 'Corolla', 'car_type': 'Sedan', 'year': 2023},
            {'make': 'Honda', 'name': 'Civic', 'car_type': 'Sedan', 'year': 2023},
            {'make': 'Honda', 'name': 'CR-V', 'car_type': 'SUV', 'year': 2023},
            {'make': 'Honda', 'name': 'Accord', 'car_type': 'Sedan', 'year': 2023},
            {'make': 'Ford', 'name': 'F-150', 'car_type': 'Truck', 'year': 2023},
            {'make': 'Ford', 'name': 'Mustang', 'car_type': 'Coupe', 'year': 2023},
            {'make': 'Chevrolet', 'name': 'Silverado', 'car_type': 'Truck', 'year': 2023},
            {'make': 'BMW', 'name': '3 Series', 'car_type': 'Sedan', 'year': 2023},
        ]

        for model_data in car_models_data:
            make = CarMake.objects.get(name=model_data['make'])
            CarModel.objects.get_or_create(
                make=make,
                name=model_data['name'],
                year=model_data['year'],
                defaults={'car_type': model_data['car_type']}
            )
        self.stdout.write(self.style.SUCCESS(f'Created {len(car_models_data)} car models'))

        # Create dealers
        dealers_data = [
            {
                'name': 'Best Motors Inc',
                'address': '123 Main Street',
                'city': 'Boston',
                'state': 'Massachusetts',
                'zip_code': '02101',
                'phone': '(617) 555-0100',
                'email': 'info@bestmotors.com',
                'website': 'https://www.bestmotors.com',
                'short_desc': 'Your trusted car dealer in Boston',
                'full_desc': 'Best Motors Inc has been serving the Boston area for over 20 years with quality vehicles and exceptional customer service.'
            },
            {
                'name': 'Elite Auto Sales',
                'address': '456 Oak Avenue',
                'city': 'Kansas City',
                'state': 'Kansas',
                'zip_code': '66101',
                'phone': '(913) 555-0200',
                'email': 'sales@eliteauto.com',
                'website': 'https://www.eliteauto.com',
                'short_desc': 'Premium vehicles and exceptional service',
                'full_desc': 'Elite Auto Sales specializes in premium vehicles with a focus on customer satisfaction.'
            },
            {
                'name': 'Quality Cars',
                'address': '789 Pine Road',
                'city': 'Wichita',
                'state': 'Kansas',
                'zip_code': '67202',
                'phone': '(316) 555-0300',
                'email': 'contact@qualitycars.com',
                'website': 'https://www.qualitycars.com',
                'short_desc': 'Quality vehicles at affordable prices',
                'full_desc': 'At Quality Cars, we believe in providing quality vehicles at prices that fit your budget.'
            },
            {
                'name': 'Premier Auto Group',
                'address': '321 Elm Street',
                'city': 'San Francisco',
                'state': 'California',
                'zip_code': '94102',
                'phone': '(415) 555-0400',
                'email': 'info@premierauto.com',
                'website': 'https://www.premierauto.com',
                'short_desc': 'San Francisco\'s premier car dealership',
                'full_desc': 'Premier Auto Group offers the finest selection of vehicles in the Bay Area.'
            },
        ]

        for dealer_data in dealers_data:
            Dealer.objects.get_or_create(name=dealer_data['name'], defaults=dealer_data)
        self.stdout.write(self.style.SUCCESS(f'Created {len(dealers_data)} dealers'))

        # Create sample users
        users_data = [
            {'username': 'testuser', 'email': 'testuser@example.com', 'first_name': 'Test', 'last_name': 'User', 'password': 'testpass123'},
            {'username': 'john_doe', 'email': 'john@example.com', 'first_name': 'John', 'last_name': 'Doe', 'password': 'password123'},
            {'username': 'jane_smith', 'email': 'jane@example.com', 'first_name': 'Jane', 'last_name': 'Smith', 'password': 'password123'},
        ]

        for user_data in users_data:
            if not User.objects.filter(username=user_data['username']).exists():
                User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    password=user_data['password']
                )
        self.stdout.write(self.style.SUCCESS(f'Created {len(users_data)} users'))

        # Create sample reviews
        dealers = Dealer.objects.all()
        users = User.objects.all()
        
        reviews_data = [
            {
                'dealer': dealers[0],
                'customer': users[0],
                'purchase': True,
                'purchase_date': date(2024, 1, 15),
                'car_make': 'Toyota',
                'car_model': 'Camry',
                'car_year': 2023,
                'review_text': 'Fantastic services and great customer support! Highly recommended.',
                'sentiment': 'positive'
            },
            {
                'dealer': dealers[0],
                'customer': users[1],
                'purchase': False,
                'review_text': 'Great experience, very helpful staff.',
                'sentiment': 'positive'
            },
            {
                'dealer': dealers[1],
                'customer': users[2],
                'purchase': True,
                'purchase_date': date(2024, 1, 10),
                'car_make': 'Honda',
                'car_model': 'CR-V',
                'car_year': 2023,
                'review_text': 'Excellent dealership with a wide selection of vehicles.',
                'sentiment': 'positive'
            },
        ]

        for review_data in reviews_data:
            # Look up on (dealer, customer, review_text): a (dealer, customer)
            # pair alone is not unique — real users may post several reviews
            # for one dealer, and reseeding must neither duplicate seed rows
            # nor crash on user-created rows (MultipleObjectsReturned).
            lookup = {
                key: review_data[key]
                for key in ('dealer', 'customer', 'review_text')
            }
            seed_defaults = {
                key: value for key, value in review_data.items()
                if key not in lookup
            }
            Review.objects.get_or_create(defaults=seed_defaults, **lookup)
        self.stdout.write(self.style.SUCCESS(f'Created sample reviews'))

        self.stdout.write(self.style.SUCCESS('Database populated successfully!'))

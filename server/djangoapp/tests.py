from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from .models import CarMake, CarModel, Dealer, Review


class CarMakeTestCase(TestCase):
    def setUp(self):
        CarMake.objects.create(name="Toyota", description="Japanese automobile manufacturer")

    def test_car_make_creation(self):
        toyota = CarMake.objects.get(name="Toyota")
        self.assertEqual(toyota.description, "Japanese automobile manufacturer")


class DealerTestCase(TestCase):
    def setUp(self):
        Dealer.objects.create(
            name="Test Motors",
            address="123 Test St",
            city="Test City",
            state="Test State",
            zip_code="12345",
            phone="123-456-7890",
            email="test@testmotors.com"
        )

    def test_dealer_creation(self):
        dealer = Dealer.objects.get(name="Test Motors")
        self.assertEqual(dealer.city, "Test City")
        self.assertEqual(dealer.state, "Test State")


class ReviewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.dealer = Dealer.objects.create(
            name="Test Motors",
            address="123 Test St",
            city="Test City",
            state="Test State",
            zip_code="12345",
            phone="123-456-7890",
            email="test@testmotors.com"
        )

    def test_review_creation(self):
        review = Review.objects.create(
            dealer=self.dealer,
            customer=self.user,
            purchase=True,
            review_text="Great service!",
            sentiment="positive"
        )
        self.assertEqual(review.sentiment, "positive")
        self.assertTrue(review.purchase)


class AuthAPITestCase(APITestCase):
    """Registration / login / current-user / logout flows."""

    def test_register_creates_and_logs_in_user(self):
        resp = self.client.post('/api/register/', {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'new@example.com',
            'password': 'strongpass123',
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())
        # Registration logs the user in: current-user should be authenticated
        me = self.client.get('/api/user/')
        self.assertTrue(me.data['authenticated'])
        self.assertEqual(me.data['user']['username'], 'newuser')

    def test_register_rejects_duplicate_username(self):
        User.objects.create_user(username='dup', password='x' * 10)
        resp = self.client.post('/api/register/', {
            'username': 'dup',
            'first_name': 'A',
            'last_name': 'B',
            'email': 'a@b.com',
            'password': 'strongpass123',
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_logout_current_user_cycle(self):
        User.objects.create_user(username='cycle', password='cyclepass123')
        # unauthenticated state
        me = self.client.get('/api/user/')
        self.assertFalse(me.data['authenticated'])
        # login
        resp = self.client.post('/api/login/', {
            'username': 'cycle', 'password': 'cyclepass123',
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['user']['username'], 'cycle')
        me = self.client.get('/api/user/')
        self.assertTrue(me.data['authenticated'])
        # logout
        out = self.client.post('/api/logout/')
        self.assertEqual(out.status_code, status.HTTP_200_OK)
        me = self.client.get('/api/user/')
        self.assertFalse(me.data['authenticated'])

    def test_login_rejects_bad_credentials(self):
        resp = self.client.post('/api/login/', {
            'username': 'nobody', 'password': 'wrong',
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_requires_username_and_password(self):
        resp = self.client.post('/api/login/', {'username': 'x'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class DealerAPITestCase(APITestCase):
    def setUp(self):
        self.d1 = Dealer.objects.create(
            name="Kansas Motors", address="1 Main St", city="Wichita",
            state="Kansas", zip_code="67202", phone="111",
            email="k@k.com")
        self.d2 = Dealer.objects.create(
            name="Boston Motors", address="2 Main St", city="Boston",
            state="Massachusetts", zip_code="02101", phone="222",
            email="b@b.com")

    def test_get_all_dealers(self):
        resp = self.client.get('/api/dealers/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 2)

    def test_get_dealer_by_id(self):
        resp = self.client.get(f'/api/dealers/{self.d1.id}/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['name'], "Kansas Motors")

    def test_get_dealer_by_id_404(self):
        resp = self.client.get('/api/dealers/9999/')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_dealers_by_state(self):
        resp = self.client.get('/api/dealers/state/Kansas/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]['state'], 'Kansas')

    def test_get_dealers_by_state_case_insensitive(self):
        resp = self.client.get('/api/dealers/state/kansas/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)


class ReviewAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='rev', password='revpass123')
        self.dealer = Dealer.objects.create(
            name="Review Motors", address="1 Main St", city="Wichita",
            state="Kansas", zip_code="67202", phone="111",
            email="r@r.com")

    def test_get_reviews_empty_then_post_and_persist(self):
        resp = self.client.get(f'/api/reviews/dealer/{self.dealer.id}/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, [])
        # unauthenticated post must fail
        denied = self.client.post('/api/reviews/', {
            'dealer': self.dealer.id, 'review_text': 'Great!'}, format='json')
        self.assertIn(denied.status_code,
                      (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))
        # authenticated post succeeds with auto sentiment
        self.client.force_authenticate(user=self.user)
        created = self.client.post('/api/reviews/', {
            'dealer': self.dealer.id,
            'purchase': False,
            'review_text': 'Fantastic services, excellent staff!',
        }, format='json')
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        self.assertEqual(created.data['review']['sentiment'], 'positive')
        # persisted and visible via GET
        resp = self.client.get(f'/api/reviews/dealer/{self.dealer.id}/')
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]['customer_name'], 'rev')
        # review count on dealer reflects the new review
        dealer_resp = self.client.get(f'/api/dealers/{self.dealer.id}/')
        self.assertEqual(dealer_resp.data['review_count'], 1)

    def test_post_review_with_empty_optional_fields(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.post('/api/reviews/', {
            'dealer': self.dealer.id,
            'purchase': False,
            'purchase_date': '',
            'car_make': '',
            'car_model': '',
            'car_year': '',
            'review_text': 'Good experience overall.',
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_post_review_requires_text(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.post('/api/reviews/', {
            'dealer': self.dealer.id, 'purchase': False}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_reviews_unknown_dealer_404(self):
        resp = self.client.get('/api/reviews/dealer/9999/')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


class CarAndSentimentAPITestCase(APITestCase):
    def setUp(self):
        make = CarMake.objects.create(name="Toyota", description="JP")
        CarModel.objects.create(make=make, name="Camry",
                               car_type="Sedan", year=2023)

    def test_get_car_makes(self):
        resp = self.client.get('/api/cars/makes/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(any(m['name'] == 'Toyota' for m in resp.data))

    def test_get_car_models(self):
        resp = self.client.get('/api/cars/models/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(any(m['name'] == 'Camry' for m in resp.data))

    def test_sentiment_positive_negative_neutral(self):
        for text, expected in [
            ("Fantastic services, excellent and amazing!", "positive"),
            ("Terrible horrible awful waste of time", "negative"),
            ("I visited the dealership on Tuesday.", "neutral"),
        ]:
            resp = self.client.post('/api/analyze/', {'text': text},
                                    format='json')
            self.assertEqual(resp.status_code, status.HTTP_200_OK)
            self.assertEqual(resp.data['sentiment'], expected)

    def test_sentiment_requires_text(self):
        resp = self.client.post('/api/analyze/', {}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

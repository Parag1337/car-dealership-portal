from django.shortcuts import render
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, generics, viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import CarMake, CarModel, Dealer, Review
from .serializers import (
    UserSerializer, RegisterSerializer, CarMakeSerializer,
    CarModelSerializer, DealerSerializer, ReviewSerializer
)
import requests
import json


# Sentiment Analysis Helper
class CsrfExemptSessionAuthentication(SessionAuthentication):
    """Session auth without CSRF enforcement, for API/curl clients."""
    def enforce_csrf(self, request):
        return


def analyze_sentiment(text):
    """
    Analyze sentiment of review text.
    Returns: 'positive', 'negative', or 'neutral'
    """
    # Simple keyword-based sentiment analysis
    positive_words = ['excellent', 'great', 'fantastic', 'amazing', 'wonderful', 
                     'good', 'best', 'love', 'perfect', 'awesome', 'outstanding']
    negative_words = ['bad', 'terrible', 'horrible', 'worst', 'awful', 'poor', 
                     'disappointing', 'hate', 'waste', 'never']
    
    text_lower = text.lower()
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    if positive_count > negative_count:
        return 'positive'
    elif negative_count > positive_count:
        return 'negative'
    else:
        return 'neutral'


# Authentication Views
@csrf_exempt
@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([AllowAny])
def login_user(request):
    """
    Authenticate user and create session
    Expected data: {'username': str, 'password': str}
    """
    data = request.data
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Username and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        login(request, user)
        return Response({
            'message': 'Login successful',
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)
    else:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@csrf_exempt
@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """Logout user and clear session"""
    logout(request)
    return Response({
        'message': 'Logout successful'
    }, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([AllowAny])
def register_user(request):
    """
    Register a new user
    Expected data: {'username': str, 'first_name': str, 'last_name': str, 
                   'email': str, 'password': str}
    """
    serializer = RegisterSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        login(request, user)
        return Response({
            'message': 'Registration successful',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_current_user(request):
    """Get current authenticated user info"""
    if request.user.is_authenticated:
        return Response({
            'authenticated': True,
            'user': UserSerializer(request.user).data
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'authenticated': False
        }, status=status.HTTP_200_OK)


# Dealer Views
@api_view(['GET'])
@permission_classes([AllowAny])
def get_dealers(request):
    """Get all dealers"""
    dealers = Dealer.objects.all()
    serializer = DealerSerializer(dealers, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_dealer_by_id(request, dealer_id):
    """Get dealer by ID"""
    try:
        dealer = Dealer.objects.get(id=dealer_id)
        serializer = DealerSerializer(dealer)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Dealer.DoesNotExist:
        return Response(
            {'error': 'Dealer not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_dealers_by_state(request, state):
    """Get dealers filtered by state"""
    dealers = Dealer.objects.filter(state__iexact=state)
    serializer = DealerSerializer(dealers, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Review Views
@api_view(['GET'])
@permission_classes([AllowAny])
def get_dealer_reviews(request, dealer_id):
    """Get all reviews for a specific dealer"""
    try:
        dealer = Dealer.objects.get(id=dealer_id)
        reviews = Review.objects.filter(dealer=dealer)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Dealer.DoesNotExist:
        return Response(
            {'error': 'Dealer not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@csrf_exempt
@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated])
def post_review(request):
    """
    Post a new review
    Expected data: {'dealer': int, 'purchase': bool, 'purchase_date': date (optional),
                   'car_make': str (optional), 'car_model': str (optional), 
                   'car_year': int (optional), 'review_text': str}
    """
    data = request.data.copy()
    
    # Normalize empty strings to None for optional fields so
    # DateField/IntegerField validation doesn't fail on ''.
    for field in ('purchase_date', 'car_year'):
        if data.get(field) in ('',):
            data[field] = None
    # Normalize optional char fields: '' -> '' is fine, but keep as-is
    for field in ('car_make', 'car_model'):
        if data.get(field) is None:
            data[field] = ''
    
    # Analyze sentiment
    review_text = data.get('review_text', '')
    sentiment = analyze_sentiment(review_text)
    
    serializer = ReviewSerializer(data=data)
    
    if serializer.is_valid():
        serializer.save(customer=request.user, sentiment=sentiment)
        return Response({
            'message': 'Review posted successfully',
            'review': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Car Make and Model Views
@api_view(['GET'])
@permission_classes([AllowAny])
def get_car_makes(request):
    """Get all car makes"""
    makes = CarMake.objects.all()
    serializer = CarMakeSerializer(makes, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_car_models(request):
    """Get all car models, optionally filtered by make"""
    make_id = request.GET.get('make')
    
    if make_id:
        models = CarModel.objects.filter(make_id=make_id)
    else:
        models = CarModel.objects.all()
    
    serializer = CarModelSerializer(models, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Sentiment Analysis View
@csrf_exempt
@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([AllowAny])
def analyze_review_sentiment(request):
    """
    Analyze sentiment of review text
    Expected data: {'text': str}
    Returns: {'sentiment': 'positive'|'negative'|'neutral'}
    """
    text = request.data.get('text', '')
    
    if not text:
        return Response(
            {'error': 'Text is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    sentiment = analyze_sentiment(text)
    
    return Response({
        'text': text,
        'sentiment': sentiment
    }, status=status.HTTP_200_OK)

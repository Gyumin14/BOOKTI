from django.urls import path
from django.contrib import admin
from . import views
from .views import SignupView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('main/', views.main_page, name="main_page"),
    path('books/<int:book_id>', views.book_detail, name="book_detail"),
    path("signup/", SignupView.as_view()),  # ✅ 여기로 변경
    path("bookti/submit/", views.bookti_submit),
    path("bookti/recommendations/", views.bookti_recommendations),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", views.me),
]
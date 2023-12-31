from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('create', views.create_listing, name='create' ),
    path('listing/<int:listing_id>', views.listing, name='listing'),
    path("watchlist/<int:user_id>", views.watchlist, name='watchlist'),
    path('categories', views.categories, name='categories'),
    path('category/<str:category>', views.category, name='category')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
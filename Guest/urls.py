"""Rental URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import include, re_path, path
from django.contrib import admin
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from django.views.generic.base import RedirectView
from rest_framework.routers import DefaultRouter
from Guest.token import GenerateTokenAPIView
admin.site.site_header = "Rental Admin"
admin.site.site_title = "Rental Admin Portal"
admin.site.index_title = "Welcome to Rental Admin Portal"


router = DefaultRouter()
router.register(r'clothviewset', views.ClothViewSet, basename='cloth')

admin.autodiscover()
urlpatterns = [
    re_path(r'api/', include(router.urls)),
    re_path(r'api-auth/', include('rest_framework.urls')),
    re_path(r'^$', RedirectView.as_view(url='/index2/')),
    re_path(r'^index2/',views.index2),
    re_path(r'^home/',views.home),
	re_path(r'^contact/', views.contact),
    re_path(r'^about/',views.about),
	re_path(r'^admin/',admin.site.urls),
    re_path(r'^user/',include('user.urls')),
    re_path(r'^register', views.register),
    re_path(r'^login', views.login_view),
    re_path(r'^profile/',views.profile),
    re_path(r'cloth/', views.post_cloth),
    re_path(r'cloths/', views.get_cloth_list),
    re_path(r'^logout', LogoutView.as_view()),
    re_path(r'^cloth_descr/',views.cloth_descr),
    re_path(r'^deleter', views.deleter),
    re_path(r'^deleteh', views.deleteh),
    re_path(r'^search/', views.search),
    re_path(r'token/', views.generate_token),
    #bulk create
    re_path(r'random/', views.generate_random_cloths),
    #chatbot
    re_path(r'allclothes/', views.all_clothes_view),
    re_path(r"chatbot/chat/", views.chatbot_response),
    re_path(r"chatbotpage/", views.chatbot_page),
]

urlpatterns+= staticfiles_urlpatterns()
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
# urlpatterns+= mediafiles_urlpatterns()
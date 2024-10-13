from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name="index"),
    path('login.html', views.Login.as_view(), name='login'),
    path('painel.html', views.Painel.as_view(), name='painel'),
    path('adc_item/', views.AdicionarItem.as_view(), name='adicionar_item'),
    path('logout.html', views.Logout.as_view(), name='logout'),
]

"""
URL configuration for ze_menu_web project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.contrib import admin 
from django.urls import path, include 
from . import views

app_name = 'pedido'

urlpatterns = [
    path('admin/', admin.site.urls),
	path('', views.index, name="index"),
	path('login/', views.Login.as_view(), name='login'),
	path('painel/', views.Painel.as_view(), name='painel'),
	path('logout/', views.Logout.as_view(), name='logout'),
    path('pedidos/', views.PedidoListView.as_view(), name='pedido'),
    path('pedidos/aumentar/<int:mesa_id>/<int:pedido_id>/', views.AumentarQuantidadePedido.as_view(), name='aumentar_pedido'),
    path('pedidos/diminuir/<int:mesa_id>/<int:pedido_id>/', views.DiminuirQuantidadePedido.as_view(), name='diminuir_pedido'),
    path('pedidos/deletar/<int:mesa_id>/<int:pedido_id>/', views.DeletarPedido.as_view(), name='deletar_pedido'),
    path('fecharconta/<int:pk>/', views.FecharConta.as_view(), name='fechar_conta'),
    path('cardapio/',views.GerenciarCardapio.as_view(), name='gerenciar_cardapio'),
]

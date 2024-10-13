
from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'pedido'

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.index, name="index"),
    path('login.html', views.Login.as_view(), name='login'),
    path('painel.html', views.Painel.as_view(), name='painel'),
    path('adc_item/', views.AdicionarItem.as_view(), name='adicionar_item'),
    path('logout.html', views.Logout.as_view(), name='logout'),
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

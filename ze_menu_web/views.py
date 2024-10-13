from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, login, logout
from contas.forms import ItemForm
from django.db import connection

def index(_request):
    return redirect("login.html")

class Login(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("painel.html")
        return render(request, "login.html")
    
    def post(self, request):
        usuario = authenticate(request, username=request.POST["email"], password=request.POST["senha"])
        if usuario is not None:
            login(request, usuario)
            return redirect("painel.html")
        return render(request, "login.html")

class Painel(View):
    def get(self, request):
        return render(request, "painel.html")

class Logout(View):
    def get(self, request):
        logout(request)
        return redirect("login.html")

class AdicionarItem(View):
    def get(self, request):
        form = ItemForm()
        return render(request, 'adicionar_item.html', {'form': form})

    def post(self, request):
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            # Pegando os dados do formulário
            nome_item = form.cleaned_data['nome_item']
            descricao = form.cleaned_data['descricao']
            precos = form.cleaned_data['precos']
            imagem_item = form.cleaned_data.get('imagem_item')

            # Verificando se um arquivo de imagem foi enviado
            if imagem_item:
                imagem_item_name = imagem_item.name
            else:
                imagem_item_name = None  # Ou coloque um valor padrão aqui, se necessário

            # Inserindo no banco de dados
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO emp1.cardapio (nome_item, descricao, precos, imagem_item)
                    VALUES (%s, %s, %s, %s)
                    """, [nome_item, descricao, precos, imagem_item_name]
                )
            
            # Salvando usando o ORM
            form.save(commit=True)

            return redirect('painel.html')
        
        return render(request, 'adicionar_item.html', {'form': form})

from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.views.generic import ListView
from django.db import connection, transaction
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from contas.forms import ItemForm
from contas.models import Usuario

def index(_request):
	return redirect("login")

class Login(View):

	def get(self, request):
		if request.user.is_authenticated:
			return redirect("painel")
		return render(request, "login.html")
	
	def post(self, request):
		usuario = authenticate(request, username=request.POST["email"], password=request.POST["senha"])
		if usuario is not None:
			login(request, usuario)
			return redirect("painel")
		return render(request, "login.html")

class Painel(LoginRequiredMixin, View):
	def get(self, request):
		return render(request, "painel.html")

class Logout(LoginRequiredMixin, View):
	def get(self, request):
		logout(request)
		return redirect("login")

class Cadastrar(View):
	def get(self, request):
		return render(request, 'cadastrar.html')
	
	def post(self, request):
		if request.POST['senha'] == request.POST['confirmarsenha']:
			Usuario.objects.create_user(request.POST['nome_empresa'], request.POST['email'], request.POST['senha'], request.POST['telefone'])
			usuario = authenticate(request, username=request.POST["email"], password=request.POST["senha"])
			if usuario is not None:
				login(request, usuario)
				return redirect("painel")
		else:
			return render(request, 'cadastrar.html', context={ 'erro': 'Senhas diferentes entre si'})

class PedidoListView(ListView):
    template_name = 'pedido.html'
    context_object_name = 'object_list'  

    def get_queryset(self):
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT 
                    m.numero_mesa, 
                    m.status_mesa, 
                    p.numero_pedido, 
                    p.nome_item, 
                    p.status_pedido,
                    p.qtd,
                    p.preco
                FROM emp1.mesas AS m
                LEFT JOIN emp1.pedidos AS p ON m.numero_mesa = p.mesa
                ORDER BY m.numero_mesa, p.numero_pedido
            ''')
            rows = cursor.fetchall()

            mesas = {}
            for row in rows:
                numero_mesa = row[0]
                status_mesa = row[1]
                pedido = {
                    'numeroPedido': row[2],
                    'nomeItem': row[3],
                    'statusPedido': row[4],
                    'quantidade': row[5],
                    'preco': float(row[6]) if row[6] else 0.0
                }

                if numero_mesa not in mesas:
                    mesas[numero_mesa] = {
                        'status_mesa': status_mesa,
                        'pedidos': [],
                        'total': 0.0
                    }

                if pedido['numeroPedido']:
                    mesas[numero_mesa]['pedidos'].append(pedido)
                    mesas[numero_mesa]['total'] += pedido['quantidade'] * pedido['preco']

        return mesas
    

class AumentarQuantidadePedido(View):
    def post(self, request, mesa_id, pedido_id):
        try:
            nova_quantidade = int(request.POST.get('quantidade', 1))
            if nova_quantidade < 1:
                raise ValueError
        except (ValueError, TypeError):
            messages.error(request, 'Quantidade inválida.')
            return redirect('pedido')

        with connection.cursor() as cursor:
            cursor.execute('''
                UPDATE emp1.pedidos
                SET qtd = qtd + %s
                WHERE numero_pedido = %s AND mesa = %s
            ''', [nova_quantidade, pedido_id, mesa_id])

        messages.success(request, 'Quantidade do pedido atualizada com sucesso.')
        return HttpResponseRedirect(reverse('pedido'))
    

class DiminuirQuantidadePedido(View):
    def post(self, request, mesa_id, pedido_id):
        try:
            diminuicao = int(request.POST.get('quantidade', 1))
            if diminuicao < 1:
                raise ValueError
        except (ValueError, TypeError):
            messages.error(request, 'Quantidade inválida.')
            return redirect('pedido')

        with transaction.atomic():
            with connection.cursor() as cursor:    
                cursor.execute('SELECT qtd FROM emp1.pedidos WHERE numero_pedido = %s AND mesa = %s', [pedido_id, mesa_id])
                row = cursor.fetchone()
                
                if row:
                    quantidade_atual = row[0]
                    nova_quantidade = quantidade_atual - diminuicao

                    if nova_quantidade < 1:
                        messages.error(request, 'A quantidade não pode ser menor que 1.')
                        return redirect('pedido')

                    # Atualizar a quantidade
                    cursor.execute('''
                        UPDATE emp1.pedidos
                        SET qtd = %s
                        WHERE numero_pedido = %s AND mesa = %s
                    ''', [nova_quantidade, pedido_id, mesa_id])

                    messages.success(request, 'Quantidade do pedido atualizada com sucesso.')
                else:
                    messages.error(request, 'Pedido não encontrado.')

        return redirect(reverse('pedido'))


class DeletarPedido(View):
    def post(self, request, mesa_id, pedido_id):
        with connection.cursor() as cursor:
            cursor.execute('''
                DELETE FROM emp1.pedidos
                WHERE numero_pedido = %s AND mesa = %s
            ''', [pedido_id, mesa_id])

        messages.success(request, 'Pedido deletado com sucesso.')
        return HttpResponseRedirect(reverse('pedido'))


class FecharConta(View):
    def post(self, request, pk):
        with connection.cursor() as cursor:
            # Deleta todos os pedidos associados à mesa
            cursor.execute('DELETE FROM emp1.pedidos WHERE mesa = %s', [pk])
            cursor.execute('UPDATE emp1.mesas SET status_mesa = %s WHERE numero_mesa = %s', ['vazia', pk])
            transaction.commit()
        messages.success(request, f'Conta da Mesa {pk} fechada com sucesso.')
        return redirect(reverse_lazy('pedido'))
    
class GerenciarCardapio(View):
    def get(self, request):
        categorias = self.getCategorias()
        cardapio = {categoria: self.getItens(categoria) for categoria in categorias}
        return render(request, "gerenciar_cardapio.html", {'cardapio': cardapio, 'categorias': categorias})

    def getCategorias(self):
        with connection.cursor() as cursor:
            cursor.execute("select unnest(enum_range(NULL::emp1.categoria))")
            rows = cursor.fetchall()
        return [row[0] for row in rows]

    def getItens(self, categoria):
        with connection.cursor() as cursor:
            cursor.execute("select nome_item, imagem_item from emp1.cardapio where categoria=%s", [categoria])
            result = cursor.fetchall()
        return result
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

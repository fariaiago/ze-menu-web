from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.views.generic import ListView
from django.db import connection, transaction
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from contas.forms import ItemForm, AdicionarCategoriaForm, EditarCategoriaForm
from contas.models import Usuario
from datetime import timedelta
from django.utils import timezone
from contas.models import ItemCardapio
import os
import qrcode
from django.conf import settings
from pathlib import Path

def index(request):
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
		messages.error(request, 'E-mail ou senha inválidos.')
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
			messages.error(request, 'Senhas diferentes entre si.')
			return render(request, 'cadastrar.html')

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
    def getLastID(self):
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM emp1.cardapio ORDER BY id DESC LIMIT 1")
            result = cursor.fetchone()
        return result[0] if result else 0 

    def get(self, request):
        print(self.getLastID())
        form = ItemForm()
        return render(request, 'adicionar_item.html', {'form': form})

    def post(self, request):
        lastId = self.getLastID() + 1
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            new_item = ItemCardapio(
                id = lastId,
                nome_item=form.cleaned_data['nome_item'],
                descricao=form.cleaned_data['descricao'],
                precos=form.cleaned_data['precos'],
                imagem_item = form.cleaned_data.get('imagem_item'),
                categoria=form.cleaned_data['categoria'],
            )
            imagem_item= form.cleaned_data.get('imagem_item')
            imagem_item_name = f"assets/images/{imagem_item.name}" if imagem_item else None
            
            new_item.save()

            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO emp1.cardapio (nome_item, descricao, precos, imagem_item, categoria)
                    VALUES (%s, %s, %s, %s, %s)
                    """, [form.cleaned_data['nome_item'], form.cleaned_data['descricao'], form.cleaned_data['precos'], imagem_item_name, form.cleaned_data['categoria']]
                )

            messages.success(request, 'Item adicionado ao cardapio com sucesso.')
            return redirect('/cardapio/')
        
        messages.error(request, 'Adicionar item ao cardapio falhou.')
        return render(request, 'adicionar_item.html', {'form': form})
    

class EditarItem(View):
    def get(self, request, item_nome):
        item = get_object_or_404(ItemCardapio, nome_item=item_nome)
        form = ItemForm(instance=item)
        return render(request, 'editar_item.html', {'form': form, 'item': item})

    def post(self, request, item_nome):
        item = get_object_or_404(ItemCardapio, nome_item=item_nome)
        form = ItemForm(request.POST, request.FILES, instance=item)
        
        if form.is_valid():
            nome_item = form.cleaned_data['nome_item']
            descricao = form.cleaned_data['descricao']
            precos = form.cleaned_data['precos']
            imagem_item = form.cleaned_data.get('imagem_item')
            categoria = form.cleaned_data['categoria']
            imagem_item_name = imagem_item.name[7:] if imagem_item else f'assets/images/{imagem_item.name}'

            form.save()

            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE emp1.cardapio
                    SET nome_item = %s, descricao = %s, precos = %s, imagem_item = %s, categoria = %s
                    WHERE nome_item = %s
                    """, [nome_item, descricao, precos, imagem_item_name, categoria, item_nome]
                )
            messages.success(request, 'Item editado com sucesso.')
            return redirect('/cardapio/')
        messages.error(request, 'Editar item do cardapio falhou.')
        return render(request, 'editar_item.html', {'form': form, 'item': item})

class DeletarItem(View):
	def post(self, request, nome_item):
		with transaction.atomic(): 
			with connection.cursor() as cursor:
				try:
					cursor.execute("""
						DELETE FROM emp1.cardapio
						WHERE nome_item = %s;
					""", [nome_item])
					messages.success(request, 'Item removido do cardapio com sucesso.')
					return redirect('/cardapio/')
				except Exception as e:
					messages.error(request, 'Remover item do cardapio falhou.')
					return redirect('/cardapio/')
		messages.error(request, 'Remover item do cardapio falhou.')
		return redirect('/cardapio/')

class AdicionarCategoria(View):
     def get(self, request):
        form = AdicionarCategoriaForm()
        return render(request, 'adicionar_categoria.html', {'form' : form})
     
     def post(self, request):
        form = AdicionarCategoriaForm(request.POST)
        if form.is_valid():
            categoria = form.cleaned_data['categoria']
            
            with connection.cursor() as cursor:
                 cursor.execute(
                    f"""
                    alter type emp1.categoria add value '{categoria}'
                    """
                )
            messages.success(request, 'Categoria adicionada ao cardapio com sucesso.')
            return redirect('/cardapio/')


class DeletarCategoria(View):
    def post(self, request, categoria):
        print("Categoria recebida para exclusão:", categoria)  # Confirmação do valor recebido

        default_categoria = 'porcoes' 

        with transaction.atomic(): 
            with connection.cursor() as cursor:
                try:
                    # Verificar se a categoria a ser removida existe no ENUM
                    cursor.execute("""
                        SELECT 1
                        FROM pg_enum
                        WHERE enumtypid = 'emp1.categoria'::regtype
                          AND enumlabel = %s;
                    """, [categoria])
                    if not cursor.fetchone():
                        messages.error(request, f"Categoria '{categoria}' não existe.")
                        print(f"Categoria '{categoria}' não existe no ENUM 'emp1.categoria'.")
                        return redirect('/cardapio/')  # Redireciona para a página do cardápio

                    # Verificar se a categoria padrão existe no ENUM
                    cursor.execute("""
                        SELECT 1
                        FROM pg_enum
                        WHERE enumtypid = 'emp1.categoria'::regtype
                          AND enumlabel = %s;
                    """, [default_categoria])
                    if not cursor.fetchone():
                        messages.error(request, f"Categoria padrão '{default_categoria}' não existe no ENUM 'emp1.categoria'.")
                        print(f"Categoria padrão '{default_categoria}' não existe no ENUM 'emp1.categoria'.")
                        return redirect('/cardapio/')  # Redireciona para a página do cardápio

                    # Excluir os itens associados à categoria
                    cursor.execute("""
                        DELETE FROM emp1.cardapio
                        WHERE categoria = %s;
                    """, [categoria])
                    deletados = cursor.rowcount
                    print(f"{deletados} itens excluídos da categoria: {categoria}")
                    messages.success(request, f"{deletados} itens da categoria '{categoria}' foram excluídos.")

                    # Renomear o tipo ENUM existente para um temporário
                    cursor.execute('ALTER TYPE emp1.categoria RENAME TO categoria_old;')
                    print("Tipo ENUM renomeado para 'categoria_old'.")
                    messages.info(request, "Tipo ENUM renomeado para 'categoria_old'.")

                    # Obter todos os valores do ENUM 'categoria_old', exceto o valor a ser excluído
                    cursor.execute("""
                        SELECT enumlabel
                        FROM pg_enum
                        WHERE enumtypid = 'emp1.categoria_old'::regtype
                          AND enumlabel != %s
                        ORDER BY enumsortorder;
                    """, [categoria])
                    remaining_values = [row[0] for row in cursor.fetchall()]
                    print(f"Valores restantes no ENUM (sem a categoria a ser removida): {remaining_values}")
                    messages.info(request, f"Valores restantes no ENUM após remoção: {remaining_values}")

                    if not remaining_values:
                        raise ValueError("Não é possível remover a única categoria existente.")

                    # Criar o novo tipo ENUM 'categoria' com os valores restantes
                    enums = ', '.join(f"'{value}'" for value in remaining_values)
                    cursor.execute(f"""
                        CREATE TYPE emp1.categoria AS ENUM ({enums});
                    """)
                    print('Novo tipo ENUM "categoria" criado com os valores atualizados.')
                    messages.info(request, "Novo tipo ENUM 'categoria' criado com os valores atualizados.")

                    # Alterar a coluna 'categoria' para usar o novo tipo ENUM
                    cursor.execute("""
                        ALTER TABLE emp1.cardapio
                        ALTER COLUMN categoria TYPE emp1.categoria
                        USING categoria::text::emp1.categoria;
                    """)
                    print('Coluna "categoria" atualizada para o novo tipo ENUM "categoria".')
                    messages.info(request, 'Coluna "categoria" atualizada para o novo tipo ENUM "categoria".')

                    # Excluir o tipo ENUM antigo 'categoria_old'
                    cursor.execute("DROP TYPE emp1.categoria_old;")
                    print("Tipo ENUM antigo 'categoria_old' removido.")
                    messages.success(request, f"Categoria '{categoria}' deletada com sucesso.")

                except Exception as e:
                    print(f"Erro ao deletar a categoria: {e}")
                    messages.error(request, f"Erro ao deletar a categoria: {e}")
                    return redirect('/cardapio/')

        return redirect('/cardapio/')

      
class EditarCategoria(View):
    def get(self, request, categoria_atual):
        form = EditarCategoriaForm(initial={'categoria_nova': categoria_atual})
        return render(request, 'edit_categoria.html', {'form': form, 'categoria_atual': categoria_atual})

    def post(self, request, categoria_atual):
        form = EditarCategoriaForm(request.POST)
        if form.is_valid():
            nova_categoria = form.cleaned_data['categoria_nova']
            with connection.cursor() as cursor:
                # Verifica as categorias existentes no ENUM
                cursor.execute("SELECT unnest(enum_range(NULL::emp1.categoria)) AS category;")
                existing_categories = [row[0] for row in cursor.fetchall()]

                # Adiciona o novo valor ao ENUM se ele ainda não existir
                if nova_categoria not in existing_categories:
                    cursor.execute(f"ALTER TYPE emp1.categoria ADD VALUE '{nova_categoria}';")

                # Atualiza os registros da tabela com a nova categoria
                cursor.execute(f"UPDATE emp1.cardapio SET categoria = '{nova_categoria}' WHERE categoria = '{categoria_atual}';")

                # Renomeia o tipo ENUM antigo
                cursor.execute("ALTER TYPE emp1.categoria RENAME TO categoria_old;")

                # Cria um novo tipo ENUM sem a categoria antiga
                new_categories = [cat for cat in existing_categories if cat != categoria_atual]
                new_categories.append(nova_categoria)  # Garante que a nova categoria está incluída
                enum_values = ', '.join(f"'{cat}'" for cat in new_categories)
                cursor.execute(f"CREATE TYPE emp1.categoria AS ENUM ({enum_values});")

                # Atualiza a coluna para usar o novo tipo ENUM
                cursor.execute("""
                    ALTER TABLE emp1.cardapio
                    ALTER COLUMN categoria TYPE emp1.categoria
                    USING categoria::text::emp1.categoria;
                """)

                # Exclui o tipo ENUM antigo
                cursor.execute("DROP TYPE emp1.categoria_old;")
            messages.success(request, 'Categoria editada com sucesso.')
            return redirect('/cardapio/')
        
class RelatorioVenda(View):
    template_name = 'relatorios.html'

    def get(self, request):
        # Produto mais vendido
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT nome_item, SUM(qtd) AS total_vendido
                FROM emp1.pedidos
                GROUP BY nome_item
                ORDER BY total_vendido DESC
                LIMIT 1;
            """)
            produto_mais_vendido = cursor.fetchone()
        
        # Produto menos vendido
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT nome_item, SUM(qtd) AS total_vendido
                FROM emp1.pedidos
                GROUP BY nome_item
                ORDER BY total_vendido ASC
                LIMIT 1;
            """)
            produto_menos_vendido = cursor.fetchone()
        
        # Quantidade de vendas mensais
        inicio_mes = timezone.now().replace(day=1)
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT SUM(qtd) AS total_vendas
                FROM emp1.pedidos
                WHERE created_at >= %s;
            """, [inicio_mes])
            vendas_mensais = cursor.fetchone()[0] or 0
        
        # Faturamento semanal
        inicio_semana = timezone.now() - timedelta(days=timezone.now().weekday())
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT SUM(qtd * preco) AS faturamento
                FROM emp1.pedidos
                WHERE created_at >= %s;
            """, [inicio_semana])
            faturamento_semanal = cursor.fetchone()[0] or 0
        
        # Faturamento mensal
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT SUM(qtd * preco) AS faturamento
                FROM emp1.pedidos
                WHERE created_at >= %s;
            """, [inicio_mes])
            faturamento_mensal = cursor.fetchone()[0] or 0
        
        context = {
            'produto_mais_vendido': {
                'nome_item': produto_mais_vendido[0] if produto_mais_vendido else None,
                'total_vendido': produto_mais_vendido[1] if produto_mais_vendido else 0
            },
            'produto_menos_vendido': {
                'nome_item': produto_menos_vendido[0] if produto_menos_vendido else None,
                'total_vendido': produto_menos_vendido[1] if produto_menos_vendido else 0
            },
            'vendas_mensais': vendas_mensais,
            'faturamento_semanal': faturamento_semanal,
            'faturamento_mensal': faturamento_mensal,
        }

        return render(request, self.template_name, context)


def CriarMesas(request):
    if request.method == "POST":
        num = request.POST.get('id')

        qr_content = f"{num} emp1"
        # Define o caminho para salvar os QR Codes dentro de static/qrcodes
        path_img = os.path.join(settings.BASE_DIR, "static", "qrcodes")

        # Cria a pasta caso não exista
        os.makedirs(path_img, exist_ok=True)

        # Gera o QR Code
        img = qrcode.make(qr_content)

        # Salva o QR Code na pasta especificada
        img.save(f"{path_img}/Mesa {num}.png")

        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO emp1.mesas (status_mesa)
                VALUES (%s)
                """,
                ['vazia']
            )

    return listar_qrcodes(request)

def DeletarMesa(request):
    if request.method == "POST":
        # Obtém o número da mesa enviado pelo formulário
        num = request.POST.get('mesa_id')
        
        # Remove a entrada correspondente no banco de dados
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM emp1.mesas
                WHERE numero_mesa = %s
                """,
                [num]
            )
        
        # Caminho para o arquivo do QR Code
        path_img = os.path.join(settings.BASE_DIR, "static", "qrcodes", f"Mesa {num}.png")

        # Remove o QR Code da pasta
        if os.path.exists(path_img):
            os.remove(path_img)

    return listar_qrcodes(request)

def listar_qrcodes(request):
    # Caminho para qrcodes
    qrcode_path = os.path.join(settings.BASE_DIR, 'static', 'qrcodes')
    
    # Lista todos os arquivos da pasta
    qrcodes = [
        f'qrcodes/{file}' for file in os.listdir(qrcode_path)
    ]

    return render(request, 'mesas.html', {'qrcodes': qrcodes})

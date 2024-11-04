from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Usuario, ItemCardapio, Categoria
from django.db import models, connection
from django import forms


class UsuarioCreationForm(UserCreationForm):

    class Meta:
        model = Usuario
        fields = ("nome_empresa", "email", "telefone",)


class UsuarioChangeForm(UserChangeForm):

    class Meta:
        model = Usuario
        fields = ("nome_empresa", "email", "telefone",)

def get_categoria_choices():
    with connection.cursor() as cursor:
        cursor.execute("SELECT unnest(enum_range(NULL::emp1.categoria))")
        rows = cursor.fetchall()
    return [(row[0], row[0]) for row in rows]  # Retorna uma lista de tuplas (valor, label)

class ItemForm(forms.ModelForm):
    categoria = forms.ChoiceField(
        choices=get_categoria_choices(),
        label="Categoria",
        required=True
    )

    class Meta:
        model = ItemCardapio
        fields = ['nome_item', 'descricao', 'precos', 'imagem_item', 'categoria']

class AdicionarCategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['categoria']
        from django import forms
        
class EditarCategoriaForm(forms.Form):
    categoria_nova = forms.CharField(max_length=30, label='Novo nome da categoria')
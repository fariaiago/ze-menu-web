from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Usuario, ItemCardapio, Categoria
from django.db import models
from django import forms


class UsuarioCreationForm(UserCreationForm):

    class Meta:
        model = Usuario
        fields = ("nome_empresa", "email", "telefone",)


class UsuarioChangeForm(UserChangeForm):

    class Meta:
        model = Usuario
        fields = ("nome_empresa", "email", "telefone",)

class ItemForm(forms.ModelForm):
    class Meta:
        model = ItemCardapio 
        fields = ['nome_item', 'descricao', 'precos', 'imagem_item']
        widgets = {
            'imagem_item': forms.ClearableFileInput(attrs={'required': False}),
        }

class AdicionarCategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['categoria']
        from django import forms
        
class EditarCategoriaForm(forms.Form):
    categoria_nova = forms.CharField(max_length=30, label='Novo nome da categoria')
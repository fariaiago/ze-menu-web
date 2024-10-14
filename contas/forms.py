from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Usuario, ItemCardapio
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

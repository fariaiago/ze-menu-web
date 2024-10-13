from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import UsuarioCreationForm, UsuarioChangeForm, ItemForm
from .models import Usuario

class UsuarioAdmin(UserAdmin):
	add_form = UsuarioCreationForm
	form = UsuarioChangeForm
	model = Usuario
	list_display = ("nome_empresa", "email", "telefone",)
	list_filter = ("nome_empresa", "email", "telefone",)
	fieldsets = (
		(None, {"fields": ("email", "senha")}),
		("Permissions", {"fields": ()}),
	)
	add_fieldsets = (
		(None, {
			"classes": ("wide",),
			"fields": (
				"nome_empresa", "email", "senha", "telefone",
				"created_at", "updated_at"
			)}
		),
	)
	search_fields = ("nome_empresa", "email", "telefone")
	ordering = ("nome_empresa", "email", "telefone")
	filter_horizontal = ()

admin.site.register(Usuario, UsuarioAdmin)

class ItemAdmin(admin.ModelAdmin):
	form = ItemForm
	list_display = ("nome_item", "descricao", "precos", "imagem_item",)
	list_filter = ("nome_item", "descricao", "precos", "imagem_item",)
	fieldsets = (
		(None, {"fields": ("nome", "descricao", "precos", "imagem_item")}),
		("Permissions", {"fields": ()}),
	)
	add_fieldsets = (
		(None, {
			"classes": ("wide",),
			"fields": (
				"nome", "descricao", "precos", "imagem_item",
			)}
		),
	)
	search_fields = ("nome", "descricao", "precos", "imagem_item")
	ordering = ("nome", "descricao", "precos", "imagem_item")
	filter_horizontal = ()
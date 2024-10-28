from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.contrib.auth.hashers import (
	acheck_password,
	check_password,
	is_password_usable,
	make_password,
)
from django.utils.crypto import salted_hmac
from .managers import UsuarioManager

class Usuario(AbstractBaseUser):
	comp_id = models.AutoField(primary_key=True)
	nome_empresa = models.CharField(max_length=255)
	email = models.EmailField(max_length=255, unique=True)
	senha = models.CharField(max_length=128)
	telefone = models.CharField(max_length=20, unique=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	USERNAME_FIELD = "email"
	EMAIL_FIELD = "email"
	REQUIRED_FIELDS = ["nome_empresa", "senha", "telefone"]
	
	objects = UsuarioManager()

	last_login = None
	password = None

	class Meta:
		db_table = "usuarios"
	
	def set_password(self, raw_password):
		self.senha = make_password(raw_password)
		self._senha = raw_password

	def check_password(self, raw_password):
		def setter(raw_password):
			self.set_password(raw_password)
			self._senha = None
			self.save(update_fields=["senha"])
		return check_password(raw_password, self.senha, setter)

	async def acheck_password(self, raw_password):
		async def setter(raw_password):
			self.set_password(raw_password)
			self._senha = None
			await self.asave(update_fields=["senha"])
		return await acheck_password(raw_password, self.senha, setter)

	def set_unusable_password(self):
		self.senha = make_password(None)

	def has_usable_password(self):
		return is_password_usable(self.senha)

	def _get_session_auth_hash(self, secret=None):
		key_salt = "django.contrib.auth.models.AbstractBaseUser.get_session_auth_hash"
		return salted_hmac(
			key_salt,
			self.senha,
			secret=secret,
			algorithm="sha256",
		).hexdigest()

class ItemCardapio(models.Model):
    nome_item = models.CharField(max_length=200)
    descricao = models.TextField()
    precos = models.DecimalField(max_digits=10, decimal_places=2)
    imagem_item = models.ImageField(upload_to='imagens_cardapio/', blank=True, null=True)
    def __str__(self):
        return self.nome_item
	
class Categoria(models.Model):
	categoria = models.CharField(max_length=30)
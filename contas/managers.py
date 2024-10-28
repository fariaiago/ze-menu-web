from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.hashers import make_password

class UsuarioManager(BaseUserManager):

	def create_user(self, nome_empresa, email, senha, telefone, **extra_fields):
		if not nome_empresa or not email or not telefone:
			raise ValueError(_("O nome da empresa, e-mail ou telefone estão vazios"))
		email = self.normalize_email(email)
		usuario = self.model(nome_empresa=nome_empresa, email=email, telefone=telefone, **extra_fields)
		usuario.set_password(senha)
		usuario.save(using=self._db)
		return usuario
	
	def create_superuser(self, nome_empresa, email, senha, telefone, **extra_fields):
		if not nome_empresa or not email or not telefone:
			raise ValueError(_("O nome da empresa, e-mail ou telefone estão vazios"))
		email = self.normalize_email(email)
		usuario = self.model(nome_empresa=nome_empresa, email=email, telefone=telefone, **extra_fields)
		usuario.set_password(senha)
		usuario.save(using=self._db)
		return usuario
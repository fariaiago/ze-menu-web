from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, login, logout

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
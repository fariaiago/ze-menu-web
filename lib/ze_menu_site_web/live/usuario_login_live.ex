defmodule ZeMenuSiteWeb.UsuarioLoginLive do
  use ZeMenuSiteWeb, :live_view

  def render(assigns) do
    ~H"""
    <.flash_group flash={@flash} />
    <div class="flex items-center min-h-screen justify-center">
      <div class="flex-row bg-white rounded-lg">
        <img src={"/images/logo.png"} alt="a" class="h-18 w-56 mt-8 mx-48 justify-center">
        <div class="flex justify-center text-xl">
          <b class="pt-8 pb-2">Acesso ao gerenciador</b><br>
        </div>
        <.simple_form for={@form} id="login_form" action={~p"/usuarios/log_in"} phx-update="ignore" class="px-20 py-8">
          <.input field={@form[:email]} name="email" type="email" label="E-mail" placeholder="Digite seu e-mail" class="py-3" required/>
          <.input field={@form[:password]} name="password" type="password" label="Senha" placeholder="Digite sua senha" class="py-3" required/>
          <div class="flex justify-end">
            <a class="pt-2 pb-4 text-xs underline decoration-gray-200" href="/usuarios/log_in">Esqueci a senha</a><br>
          </div>
          <:actions>
          <div class="flex-1 justify-center">
            <.button class="ml-20 px-32 py-4">Acessar</.button>
          </div>
          </:actions>
        </.simple_form>
      </div>
    </div>
    """
  end

  def mount(_params, _session, socket) do
    email = Phoenix.Flash.get(socket.assigns.flash, :email)
    form = to_form(%{"email" => email}, as: "usuario")
    {:ok, assign(socket, form: form), temporary_assigns: [form: form], layout: false}
  end
end

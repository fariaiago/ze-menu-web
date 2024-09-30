defmodule ZeMenuSiteWeb.UsuarioForgotPasswordLive do
  use ZeMenuSiteWeb, :live_view

  alias ZeMenuSite.Conta

  def render(assigns) do
    ~H"""
    <div class="mx-auto max-w-sm">
      <.header class="text-center">
        Forgot your password?
        <:subtitle>We'll send a password reset link to your inbox</:subtitle>
      </.header>

      <.simple_form for={@form} id="reset_password_form" phx-submit="send_email">
        <.input field={@form[:email]} type="email" placeholder="Email" required />
        <:actions>
          <.button phx-disable-with="Sending..." class="w-full">
            Send password reset instructions
          </.button>
        </:actions>
      </.simple_form>
      <p class="text-center text-sm mt-4">
        <.link href={~p"/usuarios/register"}>Register</.link>
        | <.link href={~p"/usuarios/log_in"}>Log in</.link>
      </p>
    </div>
    """
  end

  def mount(_params, _session, socket) do
    {:ok, assign(socket, form: to_form(%{}, as: "usuario"))}
  end

  def handle_event("send_email", %{"usuario" => %{"email" => email}}, socket) do
    if usuario = Conta.get_usuario_by_email(email) do
      Conta.deliver_usuario_reset_password_instructions(
        usuario,
        &url(~p"/usuarios/reset_password/#{&1}")
      )
    end

    info =
      "If your email is in our system, you will receive instructions to reset your password shortly."

    {:noreply,
     socket
     |> put_flash(:info, info)
     |> redirect(to: ~p"/")}
  end
end

defmodule ZeMenuSiteWeb.UsuarioSessionController do
  use ZeMenuSiteWeb, :controller

  alias ZeMenuSite.Conta
  alias ZeMenuSiteWeb.UsuarioAuth

  def create(conn, %{"_action" => "registered"} = params) do
    create(conn, params, "Conta criada com sucesso!")
  end

  def create(conn, %{"_action" => "password_updated"} = params) do
    conn
    |> put_session(:usuario_return_to, ~p"/usuarios/settings")
    |> create(params, "Senha atualizada com sucesso!")
  end

  def create(conn, params) do
    create(conn, params, "Bem vindo!")
  end
#%{"usuario" => usuario_params}
  defp create(conn, usuario_params, info) do
    %{"email" => email, "password" => password} = usuario_params

    if usuario = Conta.get_usuario_by_email_and_password(email, password) do
      conn
      |> put_flash(:info, info)
      |> UsuarioAuth.log_in_usuario(usuario, usuario_params)
    else
      # In order to prevent user enumeration attacks, don't disclose whether the email is registered.
      conn
      |> put_flash(:error, "E-mail ou senha invalidos")
      |> put_flash(:email, String.slice(email, 0, 160))
      |> redirect(to: ~p"/usuarios/log_in")
    end
  end

  def delete(conn, _params) do
    conn
    |> put_flash(:info, "Sessão finalizada com sucesso.")
    |> UsuarioAuth.log_out_usuario()
  end
end

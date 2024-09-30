defmodule ZeMenuSiteWeb.UsuarioAuth do
  use ZeMenuSiteWeb, :verified_routes

  import Plug.Conn
  import Phoenix.Controller

  alias ZeMenuSite.Conta

  # Make the remember me cookie valid for 60 days.
  # If you want bump or reduce this value, also change
  # the token expiry itself in UsuarioToken.
  @max_age 60 * 60 * 24 * 60
  @remember_me_cookie "_ze_menu_site_web_usuario_remember_me"
  @remember_me_options [sign: true, max_age: @max_age, same_site: "Lax"]

  @doc """
  Logs the usuario in.

  It renews the session ID and clears the whole session
  to avoid fixation attacks. See the renew_session
  function to customize this behaviour.

  It also sets a `:live_socket_id` key in the session,
  so LiveView sessions are identified and automatically
  disconnected on log out. The line can be safely removed
  if you are not using LiveView.
  """
  def log_in_usuario(conn, usuario, params \\ %{}) do
    token = Conta.generate_usuario_session_token(usuario)
    usuario_return_to = get_session(conn, :usuario_return_to)

    conn
    |> renew_session()
    |> put_token_in_session(token)
    |> maybe_write_remember_me_cookie(token, params)
    |> redirect(to: usuario_return_to || signed_in_path(conn))
  end

  defp maybe_write_remember_me_cookie(conn, token, %{"remember_me" => "true"}) do
    put_resp_cookie(conn, @remember_me_cookie, token, @remember_me_options)
  end

  defp maybe_write_remember_me_cookie(conn, _token, _params) do
    conn
  end

  # This function renews the session ID and erases the whole
  # session to avoid fixation attacks. If there is any data
  # in the session you may want to preserve after log in/log out,
  # you must explicitly fetch the session data before clearing
  # and then immediately set it after clearing, for example:
  #
  #     defp renew_session(conn) do
  #       preferred_locale = get_session(conn, :preferred_locale)
  #
  #       conn
  #       |> configure_session(renew: true)
  #       |> clear_session()
  #       |> put_session(:preferred_locale, preferred_locale)
  #     end
  #
  defp renew_session(conn) do
    delete_csrf_token()

    conn
    |> configure_session(renew: true)
    |> clear_session()
  end

  @doc """
  Logs the usuario out.

  It clears all session data for safety. See renew_session.
  """
  def log_out_usuario(conn) do
    usuario_token = get_session(conn, :usuario_token)
    usuario_token && Conta.delete_usuario_session_token(usuario_token)

    if live_socket_id = get_session(conn, :live_socket_id) do
      ZeMenuSiteWeb.Endpoint.broadcast(live_socket_id, "disconnect", %{})
    end

    conn
    |> renew_session()
    |> delete_resp_cookie(@remember_me_cookie)
    |> redirect(to: ~p"/")
  end

  @doc """
  Authenticates the usuario by looking into the session
  and remember me token.
  """
  def fetch_current_usuario(conn, _opts) do
    {usuario_token, conn} = ensure_usuario_token(conn)
    usuario = usuario_token && Conta.get_usuario_by_session_token(usuario_token)
    assign(conn, :current_usuario, usuario)
  end

  defp ensure_usuario_token(conn) do
    if token = get_session(conn, :usuario_token) do
      {token, conn}
    else
      conn = fetch_cookies(conn, signed: [@remember_me_cookie])

      if token = conn.cookies[@remember_me_cookie] do
        {token, put_token_in_session(conn, token)}
      else
        {nil, conn}
      end
    end
  end

  @doc """
  Handles mounting and authenticating the current_usuario in LiveViews.

  ## `on_mount` arguments

    * `:mount_current_usuario` - Assigns current_usuario
      to socket assigns based on usuario_token, or nil if
      there's no usuario_token or no matching usuario.

    * `:ensure_authenticated` - Authenticates the usuario from the session,
      and assigns the current_usuario to socket assigns based
      on usuario_token.
      Redirects to login page if there's no logged usuario.

    * `:redirect_if_usuario_is_authenticated` - Authenticates the usuario from the session.
      Redirects to signed_in_path if there's a logged usuario.

  ## Examples

  Use the `on_mount` lifecycle macro in LiveViews to mount or authenticate
  the current_usuario:

      defmodule ZeMenuSiteWeb.PageLive do
        use ZeMenuSiteWeb, :live_view

        on_mount {ZeMenuSiteWeb.UsuarioAuth, :mount_current_usuario}
        ...
      end

  Or use the `live_session` of your router to invoke the on_mount callback:

      live_session :authenticated, on_mount: [{ZeMenuSiteWeb.UsuarioAuth, :ensure_authenticated}] do
        live "/profile", ProfileLive, :index
      end
  """
  def on_mount(:mount_current_usuario, _params, session, socket) do
    {:cont, mount_current_usuario(socket, session)}
  end

  def on_mount(:ensure_authenticated, _params, session, socket) do
    socket = mount_current_usuario(socket, session)

    if socket.assigns.current_usuario do
      {:cont, socket}
    else
      socket =
        socket
        |> Phoenix.LiveView.put_flash(:error, "You must log in to access this page.")
        |> Phoenix.LiveView.redirect(to: ~p"/usuarios/log_in")

      {:halt, socket}
    end
  end

  def on_mount(:redirect_if_usuario_is_authenticated, _params, session, socket) do
    socket = mount_current_usuario(socket, session)

    if socket.assigns.current_usuario do
      {:halt, Phoenix.LiveView.redirect(socket, to: signed_in_path(socket))}
    else
      {:cont, socket}
    end
  end

  defp mount_current_usuario(socket, session) do
    Phoenix.Component.assign_new(socket, :current_usuario, fn ->
      if usuario_token = session["usuario_token"] do
        Conta.get_usuario_by_session_token(usuario_token)
      end
    end)
  end

  @doc """
  Used for routes that require the usuario to not be authenticated.
  """
  def redirect_if_usuario_is_authenticated(conn, _opts) do
    if conn.assigns[:current_usuario] do
      conn
      |> redirect(to: signed_in_path(conn))
      |> halt()
    else
      conn
    end
  end

  @doc """
  Used for routes that require the usuario to be authenticated.

  If you want to enforce the usuario email is confirmed before
  they use the application at all, here would be a good place.
  """
  def require_authenticated_usuario(conn, _opts) do
    if conn.assigns[:current_usuario] do
      conn
    else
      conn
      |> put_flash(:error, "You must log in to access this page.")
      |> maybe_store_return_to()
      |> redirect(to: ~p"/usuarios/log_in")
      |> halt()
    end
  end

  defp put_token_in_session(conn, token) do
    conn
    |> put_session(:usuario_token, token)
    |> put_session(:live_socket_id, "usuarios_sessions:#{Base.url_encode64(token)}")
  end

  defp maybe_store_return_to(%{method: "GET"} = conn) do
    put_session(conn, :usuario_return_to, current_path(conn))
  end

  defp maybe_store_return_to(conn), do: conn

  defp signed_in_path(_conn), do: ~p"/"
end

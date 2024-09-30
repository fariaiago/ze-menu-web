defmodule ZeMenuSiteWeb.Router do
  use ZeMenuSiteWeb, :router

  import ZeMenuSiteWeb.UsuarioAuth

  pipeline :browser do
    plug :accepts, ["html"]
    plug :fetch_session
    plug :fetch_live_flash
    plug :put_root_layout, html: {ZeMenuSiteWeb.Layouts, :root}
    plug :protect_from_forgery
    plug :put_secure_browser_headers
    plug :fetch_current_usuario
  end

  pipeline :api do
    plug :accepts, ["json"]
  end

  scope "/", ZeMenuSiteWeb do
    pipe_through :browser

    get "/", PageController, :home
  end

  # Other scopes may use custom stacks.
  # scope "/api", ZeMenuSiteWeb do
  #   pipe_through :api
  # end

  # Enable LiveDashboard and Swoosh mailbox preview in development
  if Application.compile_env(:ze_menu_site, :dev_routes) do
    # If you want to use the LiveDashboard in production, you should put
    # it behind authentication and allow only admins to access it.
    # If your application does not have an admins-only section yet,
    # you can use Plug.BasicAuth to set up some basic authentication
    # as long as you are also using SSL (which you should anyway).
    import Phoenix.LiveDashboard.Router

    scope "/dev" do
      pipe_through :browser

      live_dashboard "/dashboard", metrics: ZeMenuSiteWeb.Telemetry
      forward "/mailbox", Plug.Swoosh.MailboxPreview
    end
  end

  ## Authentication routes

  scope "/", ZeMenuSiteWeb do
    pipe_through [:browser, :redirect_if_usuario_is_authenticated]

    live_session :redirect_if_usuario_is_authenticated,
      on_mount: [{ZeMenuSiteWeb.UsuarioAuth, :redirect_if_usuario_is_authenticated}] do
      live "/usuarios/register", UsuarioRegistrationLive, :new
      live "/usuarios/log_in", UsuarioLoginLive, :new
      live "/usuarios/reset_password", UsuarioForgotPasswordLive, :new
      live "/usuarios/reset_password/:token", UsuarioResetPasswordLive, :edit
    end

    post "/usuarios/log_in", UsuarioSessionController, :create
  end

  scope "/", ZeMenuSiteWeb do
    pipe_through [:browser, :require_authenticated_usuario]

    live_session :require_authenticated_usuario,
      on_mount: [{ZeMenuSiteWeb.UsuarioAuth, :ensure_authenticated}] do
      live "/usuarios/settings", UsuarioSettingsLive, :edit
      live "/usuarios/settings/confirm_email/:token", UsuarioSettingsLive, :confirm_email
    end
  end

  scope "/", ZeMenuSiteWeb do
    pipe_through [:browser]

    delete "/usuarios/log_out", UsuarioSessionController, :delete

    live_session :current_usuario,
      on_mount: [{ZeMenuSiteWeb.UsuarioAuth, :mount_current_usuario}] do
      live "/usuarios/confirm/:token", UsuarioConfirmationLive, :edit
      live "/usuarios/confirm", UsuarioConfirmationInstructionsLive, :new
    end
  end
end

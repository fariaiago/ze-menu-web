defmodule ZeMenuSiteWeb.PageController do
  use ZeMenuSiteWeb, :controller

  def home(conn, _params) do
    # The home page is often custom made,
    # so skip the default app layout.
    #render(conn, :home, layout: false)
    redirect(conn, to: "/usuarios/log_in")
  end
end

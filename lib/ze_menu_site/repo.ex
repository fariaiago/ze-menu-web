defmodule ZeMenuSite.Repo do
  use Ecto.Repo,
    otp_app: :ze_menu_site,
    adapter: Ecto.Adapters.Postgres
end

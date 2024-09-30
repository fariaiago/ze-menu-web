defmodule ZeMenuSiteWeb.UsuarioConfirmationInstructionsLiveTest do
  use ZeMenuSiteWeb.ConnCase, async: true

  import Phoenix.LiveViewTest
  import ZeMenuSite.ContaFixtures

  alias ZeMenuSite.Conta
  alias ZeMenuSite.Repo

  setup do
    %{usuario: usuario_fixture()}
  end

  describe "Resend confirmation" do
    test "renders the resend confirmation page", %{conn: conn} do
      {:ok, _lv, html} = live(conn, ~p"/usuarios/confirm")
      assert html =~ "Resend confirmation instructions"
    end

    test "sends a new confirmation token", %{conn: conn, usuario: usuario} do
      {:ok, lv, _html} = live(conn, ~p"/usuarios/confirm")

      {:ok, conn} =
        lv
        |> form("#resend_confirmation_form", usuario: %{email: usuario.email})
        |> render_submit()
        |> follow_redirect(conn, ~p"/")

      assert Phoenix.Flash.get(conn.assigns.flash, :info) =~
               "If your email is in our system"

      assert Repo.get_by!(Conta.UsuarioToken, usuario_id: usuario.id).context == "confirm"
    end

    test "does not send confirmation token if usuario is confirmed", %{conn: conn, usuario: usuario} do
      Repo.update!(Conta.Usuario.confirm_changeset(usuario))

      {:ok, lv, _html} = live(conn, ~p"/usuarios/confirm")

      {:ok, conn} =
        lv
        |> form("#resend_confirmation_form", usuario: %{email: usuario.email})
        |> render_submit()
        |> follow_redirect(conn, ~p"/")

      assert Phoenix.Flash.get(conn.assigns.flash, :info) =~
               "If your email is in our system"

      refute Repo.get_by(Conta.UsuarioToken, usuario_id: usuario.id)
    end

    test "does not send confirmation token if email is invalid", %{conn: conn} do
      {:ok, lv, _html} = live(conn, ~p"/usuarios/confirm")

      {:ok, conn} =
        lv
        |> form("#resend_confirmation_form", usuario: %{email: "unknown@example.com"})
        |> render_submit()
        |> follow_redirect(conn, ~p"/")

      assert Phoenix.Flash.get(conn.assigns.flash, :info) =~
               "If your email is in our system"

      assert Repo.all(Conta.UsuarioToken) == []
    end
  end
end

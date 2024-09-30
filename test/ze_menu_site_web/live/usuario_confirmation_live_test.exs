defmodule ZeMenuSiteWeb.UsuarioConfirmationLiveTest do
  use ZeMenuSiteWeb.ConnCase, async: true

  import Phoenix.LiveViewTest
  import ZeMenuSite.ContaFixtures

  alias ZeMenuSite.Conta
  alias ZeMenuSite.Repo

  setup do
    %{usuario: usuario_fixture()}
  end

  describe "Confirm usuario" do
    test "renders confirmation page", %{conn: conn} do
      {:ok, _lv, html} = live(conn, ~p"/usuarios/confirm/some-token")
      assert html =~ "Confirm Account"
    end

    test "confirms the given token once", %{conn: conn, usuario: usuario} do
      token =
        extract_usuario_token(fn url ->
          Conta.deliver_usuario_confirmation_instructions(usuario, url)
        end)

      {:ok, lv, _html} = live(conn, ~p"/usuarios/confirm/#{token}")

      result =
        lv
        |> form("#confirmation_form")
        |> render_submit()
        |> follow_redirect(conn, "/")

      assert {:ok, conn} = result

      assert Phoenix.Flash.get(conn.assigns.flash, :info) =~
               "Usuario confirmed successfully"

      assert Conta.get_usuario!(usuario.id).confirmed_at
      refute get_session(conn, :usuario_token)
      assert Repo.all(Conta.UsuarioToken) == []

      # when not logged in
      {:ok, lv, _html} = live(conn, ~p"/usuarios/confirm/#{token}")

      result =
        lv
        |> form("#confirmation_form")
        |> render_submit()
        |> follow_redirect(conn, "/")

      assert {:ok, conn} = result

      assert Phoenix.Flash.get(conn.assigns.flash, :error) =~
               "Usuario confirmation link is invalid or it has expired"

      # when logged in
      conn =
        build_conn()
        |> log_in_usuario(usuario)

      {:ok, lv, _html} = live(conn, ~p"/usuarios/confirm/#{token}")

      result =
        lv
        |> form("#confirmation_form")
        |> render_submit()
        |> follow_redirect(conn, "/")

      assert {:ok, conn} = result
      refute Phoenix.Flash.get(conn.assigns.flash, :error)
    end

    test "does not confirm email with invalid token", %{conn: conn, usuario: usuario} do
      {:ok, lv, _html} = live(conn, ~p"/usuarios/confirm/invalid-token")

      {:ok, conn} =
        lv
        |> form("#confirmation_form")
        |> render_submit()
        |> follow_redirect(conn, ~p"/")

      assert Phoenix.Flash.get(conn.assigns.flash, :error) =~
               "Usuario confirmation link is invalid or it has expired"

      refute Conta.get_usuario!(usuario.id).confirmed_at
    end
  end
end

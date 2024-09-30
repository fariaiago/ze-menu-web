defmodule ZeMenuSiteWeb.UsuarioSettingsLiveTest do
  use ZeMenuSiteWeb.ConnCase, async: true

  alias ZeMenuSite.Conta
  import Phoenix.LiveViewTest
  import ZeMenuSite.ContaFixtures

  describe "Settings page" do
    test "renders settings page", %{conn: conn} do
      {:ok, _lv, html} =
        conn
        |> log_in_usuario(usuario_fixture())
        |> live(~p"/usuarios/settings")

      assert html =~ "Change Email"
      assert html =~ "Change Password"
    end

    test "redirects if usuario is not logged in", %{conn: conn} do
      assert {:error, redirect} = live(conn, ~p"/usuarios/settings")

      assert {:redirect, %{to: path, flash: flash}} = redirect
      assert path == ~p"/usuarios/log_in"
      assert %{"error" => "You must log in to access this page."} = flash
    end
  end

  describe "update email form" do
    setup %{conn: conn} do
      password = valid_usuario_password()
      usuario = usuario_fixture(%{password: password})
      %{conn: log_in_usuario(conn, usuario), usuario: usuario, password: password}
    end

    test "updates the usuario email", %{conn: conn, password: password, usuario: usuario} do
      new_email = unique_usuario_email()

      {:ok, lv, _html} = live(conn, ~p"/usuarios/settings")

      result =
        lv
        |> form("#email_form", %{
          "current_password" => password,
          "usuario" => %{"email" => new_email}
        })
        |> render_submit()

      assert result =~ "A link to confirm your email"
      assert Conta.get_usuario_by_email(usuario.email)
    end

    test "renders errors with invalid data (phx-change)", %{conn: conn} do
      {:ok, lv, _html} = live(conn, ~p"/usuarios/settings")

      result =
        lv
        |> element("#email_form")
        |> render_change(%{
          "action" => "update_email",
          "current_password" => "invalid",
          "usuario" => %{"email" => "with spaces"}
        })

      assert result =~ "Change Email"
      assert result =~ "must have the @ sign and no spaces"
    end

    test "renders errors with invalid data (phx-submit)", %{conn: conn, usuario: usuario} do
      {:ok, lv, _html} = live(conn, ~p"/usuarios/settings")

      result =
        lv
        |> form("#email_form", %{
          "current_password" => "invalid",
          "usuario" => %{"email" => usuario.email}
        })
        |> render_submit()

      assert result =~ "Change Email"
      assert result =~ "did not change"
      assert result =~ "is not valid"
    end
  end

  describe "update password form" do
    setup %{conn: conn} do
      password = valid_usuario_password()
      usuario = usuario_fixture(%{password: password})
      %{conn: log_in_usuario(conn, usuario), usuario: usuario, password: password}
    end

    test "updates the usuario password", %{conn: conn, usuario: usuario, password: password} do
      new_password = valid_usuario_password()

      {:ok, lv, _html} = live(conn, ~p"/usuarios/settings")

      form =
        form(lv, "#password_form", %{
          "current_password" => password,
          "usuario" => %{
            "email" => usuario.email,
            "password" => new_password,
            "password_confirmation" => new_password
          }
        })

      render_submit(form)

      new_password_conn = follow_trigger_action(form, conn)

      assert redirected_to(new_password_conn) == ~p"/usuarios/settings"

      assert get_session(new_password_conn, :usuario_token) != get_session(conn, :usuario_token)

      assert Phoenix.Flash.get(new_password_conn.assigns.flash, :info) =~
               "Password updated successfully"

      assert Conta.get_usuario_by_email_and_password(usuario.email, new_password)
    end

    test "renders errors with invalid data (phx-change)", %{conn: conn} do
      {:ok, lv, _html} = live(conn, ~p"/usuarios/settings")

      result =
        lv
        |> element("#password_form")
        |> render_change(%{
          "current_password" => "invalid",
          "usuario" => %{
            "password" => "too short",
            "password_confirmation" => "does not match"
          }
        })

      assert result =~ "Change Password"
      assert result =~ "should be at least 12 character(s)"
      assert result =~ "does not match password"
    end

    test "renders errors with invalid data (phx-submit)", %{conn: conn} do
      {:ok, lv, _html} = live(conn, ~p"/usuarios/settings")

      result =
        lv
        |> form("#password_form", %{
          "current_password" => "invalid",
          "usuario" => %{
            "password" => "too short",
            "password_confirmation" => "does not match"
          }
        })
        |> render_submit()

      assert result =~ "Change Password"
      assert result =~ "should be at least 12 character(s)"
      assert result =~ "does not match password"
      assert result =~ "is not valid"
    end
  end

  describe "confirm email" do
    setup %{conn: conn} do
      usuario = usuario_fixture()
      email = unique_usuario_email()

      token =
        extract_usuario_token(fn url ->
          Conta.deliver_usuario_update_email_instructions(%{usuario | email: email}, usuario.email, url)
        end)

      %{conn: log_in_usuario(conn, usuario), token: token, email: email, usuario: usuario}
    end

    test "updates the usuario email once", %{conn: conn, usuario: usuario, token: token, email: email} do
      {:error, redirect} = live(conn, ~p"/usuarios/settings/confirm_email/#{token}")

      assert {:live_redirect, %{to: path, flash: flash}} = redirect
      assert path == ~p"/usuarios/settings"
      assert %{"info" => message} = flash
      assert message == "Email changed successfully."
      refute Conta.get_usuario_by_email(usuario.email)
      assert Conta.get_usuario_by_email(email)

      # use confirm token again
      {:error, redirect} = live(conn, ~p"/usuarios/settings/confirm_email/#{token}")
      assert {:live_redirect, %{to: path, flash: flash}} = redirect
      assert path == ~p"/usuarios/settings"
      assert %{"error" => message} = flash
      assert message == "Email change link is invalid or it has expired."
    end

    test "does not update email with invalid token", %{conn: conn, usuario: usuario} do
      {:error, redirect} = live(conn, ~p"/usuarios/settings/confirm_email/oops")
      assert {:live_redirect, %{to: path, flash: flash}} = redirect
      assert path == ~p"/usuarios/settings"
      assert %{"error" => message} = flash
      assert message == "Email change link is invalid or it has expired."
      assert Conta.get_usuario_by_email(usuario.email)
    end

    test "redirects if usuario is not logged in", %{token: token} do
      conn = build_conn()
      {:error, redirect} = live(conn, ~p"/usuarios/settings/confirm_email/#{token}")
      assert {:redirect, %{to: path, flash: flash}} = redirect
      assert path == ~p"/usuarios/log_in"
      assert %{"error" => message} = flash
      assert message == "You must log in to access this page."
    end
  end
end

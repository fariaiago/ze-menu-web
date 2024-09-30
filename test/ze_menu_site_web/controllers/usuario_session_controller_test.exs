defmodule ZeMenuSiteWeb.UsuarioSessionControllerTest do
  use ZeMenuSiteWeb.ConnCase, async: true

  import ZeMenuSite.ContaFixtures

  setup do
    %{usuario: usuario_fixture()}
  end

  describe "POST /usuarios/log_in" do
    test "logs the usuario in", %{conn: conn, usuario: usuario} do
      conn =
        post(conn, ~p"/usuarios/log_in", %{
          "usuario" => %{"email" => usuario.email, "password" => valid_usuario_password()}
        })

      assert get_session(conn, :usuario_token)
      assert redirected_to(conn) == ~p"/"

      # Now do a logged in request and assert on the menu
      conn = get(conn, ~p"/")
      response = html_response(conn, 200)
      assert response =~ usuario.email
      assert response =~ ~p"/usuarios/settings"
      assert response =~ ~p"/usuarios/log_out"
    end

    test "logs the usuario in with remember me", %{conn: conn, usuario: usuario} do
      conn =
        post(conn, ~p"/usuarios/log_in", %{
          "usuario" => %{
            "email" => usuario.email,
            "password" => valid_usuario_password(),
            "remember_me" => "true"
          }
        })

      assert conn.resp_cookies["_ze_menu_site_web_usuario_remember_me"]
      assert redirected_to(conn) == ~p"/"
    end

    test "logs the usuario in with return to", %{conn: conn, usuario: usuario} do
      conn =
        conn
        |> init_test_session(usuario_return_to: "/foo/bar")
        |> post(~p"/usuarios/log_in", %{
          "usuario" => %{
            "email" => usuario.email,
            "password" => valid_usuario_password()
          }
        })

      assert redirected_to(conn) == "/foo/bar"
      assert Phoenix.Flash.get(conn.assigns.flash, :info) =~ "Welcome back!"
    end

    test "login following registration", %{conn: conn, usuario: usuario} do
      conn =
        conn
        |> post(~p"/usuarios/log_in", %{
          "_action" => "registered",
          "usuario" => %{
            "email" => usuario.email,
            "password" => valid_usuario_password()
          }
        })

      assert redirected_to(conn) == ~p"/"
      assert Phoenix.Flash.get(conn.assigns.flash, :info) =~ "Account created successfully"
    end

    test "login following password update", %{conn: conn, usuario: usuario} do
      conn =
        conn
        |> post(~p"/usuarios/log_in", %{
          "_action" => "password_updated",
          "usuario" => %{
            "email" => usuario.email,
            "password" => valid_usuario_password()
          }
        })

      assert redirected_to(conn) == ~p"/usuarios/settings"
      assert Phoenix.Flash.get(conn.assigns.flash, :info) =~ "Password updated successfully"
    end

    test "redirects to login page with invalid credentials", %{conn: conn} do
      conn =
        post(conn, ~p"/usuarios/log_in", %{
          "usuario" => %{"email" => "invalid@email.com", "password" => "invalid_password"}
        })

      assert Phoenix.Flash.get(conn.assigns.flash, :error) == "Invalid email or password"
      assert redirected_to(conn) == ~p"/usuarios/log_in"
    end
  end

  describe "DELETE /usuarios/log_out" do
    test "logs the usuario out", %{conn: conn, usuario: usuario} do
      conn = conn |> log_in_usuario(usuario) |> delete(~p"/usuarios/log_out")
      assert redirected_to(conn) == ~p"/"
      refute get_session(conn, :usuario_token)
      assert Phoenix.Flash.get(conn.assigns.flash, :info) =~ "Logged out successfully"
    end

    test "succeeds even if the usuario is not logged in", %{conn: conn} do
      conn = delete(conn, ~p"/usuarios/log_out")
      assert redirected_to(conn) == ~p"/"
      refute get_session(conn, :usuario_token)
      assert Phoenix.Flash.get(conn.assigns.flash, :info) =~ "Logged out successfully"
    end
  end
end

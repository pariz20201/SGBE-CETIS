import flet as ft
import os
import sys
from sgbe_admin import (
    vista_dashboard_admin, vista_gestion_usuarios,
    vista_gestion_Libros, vista_gestion_Prestamos,
    popup_libroP, boton
)
from config import get_db, actualizar_penalizaciones_automaticas
from services.usuarios import login
from services.libros import obtener_libros, obtener_libro_por_id
from services.prestamos import obtener_prestamos_usuario
from sgbe_bibliotecario import vista_dashboard_bibliotecario


def text_input(password=False, hint=""):
    return ft.TextField(
        cursor_color="#000000",
        hint_text=hint,
        color="#000000",
        bgcolor="#D9D9D9",
        border_radius=17,
        border_color="transparent",
        password=password,
        can_reveal_password=password,
        expand=True
    )

def boton_login(text, on_click):
    return ft.Container(
        content=ft.ElevatedButton(
            text,
            on_click=on_click,
            style=ft.ButtonStyle(
                bgcolor="#D9D9D9",
                color="#000000",
                overlay_color="#888888"
            )
        )
    )

PORTADA_FALLBACK = "https://cdn-icons-png.flaticon.com/512/2232/2232688.png"

def portada_url(titulo: str) -> str:
    import urllib.parse
    return f"https://covers.openlibrary.org/b/title/{urllib.parse.quote(titulo)}-L.jpg"

def imagen_portada(titulo: str, height: int = 200) -> ft.Image:
    return ft.Image(
        src=portada_url(titulo),
        height=height,
        fit="cover",
        border_radius=8,
        error_content=ft.Image(src=PORTADA_FALLBACK, height=height, fit="contain"),
    )

def crear_grid_libros(page, libros):
    if not isinstance(libros, list):
        libros = []
    if not libros:
        return ft.Container(
            expand=True,
            width=float("inf"),
            alignment=ft.Alignment(0, 0), 
            content=ft.Text("No hay libros disponibles", size=20, color=ft.Colors.BLACK54)
        )
    return ft.Container(
        padding=ft.padding.all(20),
        width=float("inf"), 
        content=ft.GridView(
            expand=True,
            runs_count=4,
            spacing=30,
            run_spacing=30,
            controls=[
                ft.Container(
                    height=320,
                    bgcolor="#F5F5F5" if libro[4] <= 0 else ft.Colors.WHITE,
                    border_radius=15,
                    shadow=ft.BoxShadow(blur_radius=10, color="black12"),
                    padding=10,
                    ink=True,
                    on_click=lambda _, l=libro: page.go(f"/detalle/{l[0]}") if l[4] > 0 else None,
                    content=ft.Column(
                        spacing=8,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            imagen_portada(libro[2], height=200),
                            ft.Text(libro[2], size=14, weight=ft.FontWeight.BOLD, max_lines=2,
                                    text_align=ft.TextAlign.CENTER, overflow=ft.TextOverflow.ELLIPSIS, color="black"),
                            ft.Text(f"Autor: {libro[3]}", size=11, color=ft.Colors.BLACK54),
                            ft.Text(f"Género: {libro[5]}", size=11, color="#712B33"),
                            ft.Text(
                                f"Disponibles: {libro[4]}",
                                size=11, weight=ft.FontWeight.BOLD,
                                color="green" if libro[4] > 0 else "red"
                            ),
                        ],
                    )
                )
                for libro in libros
            ]
        )
    )

def crear_grid_prestamos(page, prestamos):
    if not prestamos:
        return ft.Container(
            padding=ft.padding.only(top=20),
            content=ft.Text("No tienes préstamos activos.", size=16, color=ft.Colors.BLACK54)
        )
    return ft.Container(
        padding=ft.padding.symmetric(vertical=10),
        content=ft.GridView(
            expand=False,
            runs_count=4,
            spacing=20,
            run_spacing=20,
            controls=[
                ft.Container(
                    height=320,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=15,
                    shadow=ft.BoxShadow(blur_radius=10, color="black12"),
                    padding=10,
                    content=ft.Column(
                        spacing=8,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            imagen_portada(p[3], height=180),
                            ft.Text(p[3], size=13, weight=ft.FontWeight.BOLD, max_lines=2,
                                    text_align=ft.TextAlign.CENTER, overflow=ft.TextOverflow.ELLIPSIS, color="black"),
                            ft.Text(f"Autor: {p[4]}", size=11, color=ft.Colors.BLACK54),
                            ft.Text(f"Género: {p[6]}", size=11, color="#712B33"),
                            ft.Text(f"Salida: {p[7]}", size=10, color=ft.Colors.BLACK38),
                            ft.Text(
                                f"Devolver antes de: {p[8]}" if p[8] else "Sin fecha límite",
                                size=10,
                                color="red" if p[8] else ft.Colors.BLACK38
                            ),
                        ],
                    )
                )
                for p in prestamos
            ]
        )
    )


def main(page: ft.Page):

    resultado_sync = actualizar_penalizaciones_automaticas()
    if resultado_sync.get("ok"):
        print(resultado_sync.get("msg"))

    page.title = "Librería Digital"
    page.bgcolor = "#ffffff"
    page.window_maximized = True

    correo_input = text_input(hint="")
    pass_input   = text_input(password=True, hint="")

    def limpiar_campos_login():
        correo_input.value     = ""
        pass_input.value       = ""
        correo_input.error_text = None
        pass_input.error_text  = None

    def mostrar_dialogo(titulo, mensaje, on_cerrar=None):
        def _cerrar(e):
            dlg.open = False
            page.update() 
            if on_cerrar:
                on_cerrar()
        
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(titulo, weight=ft.FontWeight.BOLD, color="#000000"),
            content=ft.Text(mensaje),
            shape=ft.RoundedRectangleBorder(radius=10),
            actions=[ft.ElevatedButton("Aceptar", on_click=_cerrar,
                                       bgcolor="#712B33", color="white")],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    def route_change(e):
        page.views.clear()


        if page.route in ("/login", "/", ""):
            limpiar_campos_login()

            def validar_login(e):
                correo_input.error_text = None
                pass_input.error_text   = None
                if not correo_input.value:
                    correo_input.error_text = "Campo obligatorio"
                if not pass_input.value:
                    pass_input.error_text = "Campo obligatorio"
                if not correo_input.value or not pass_input.value:
                    page.update()
                    return

                respuesta = login(correo_input.value, pass_input.value)
                if respuesta["ok"]:
                    page.usuario_actual = respuesta["data"]
                    ruta = respuesta["data"]["redirect"]
                    if ruta == "admin-inicio":
                        page.go("/admin-inicio")
                    elif ruta == "biblio-inicio":
                        page.go("/biblio-inicio")
                    else:
                        page.go("/home")
                else:
                    mostrar_dialogo("Error al iniciar sesión", respuesta["msg"])

            page.views.append(ft.View(
                route="/login",
                padding=0,
                bgcolor="#ffffff",
                controls=[
                    ft.Stack(
                        expand=True,
                        controls=[
                            ft.Container(
                                alignment=ft.Alignment(-1, -1),
                                padding=10,
                                content=ft.Image(src="logo-color-clean-vino.svg", width=300)
                            ),
                            ft.Container(
                                alignment=ft.Alignment(0, 0),
                                content=ft.Container(
                                    width=400, height=350,
                                    padding=20,
                                    bgcolor="#712B33",
                                    border_radius=10,
                                    content=ft.Column(
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        controls=[
                                            ft.Text("Usuario", color="white"),
                                            correo_input,
                                            ft.Text("Contraseña", color="white"),
                                            pass_input,
                                            boton_login("Iniciar Sesión", on_click=validar_login)
                                        ]
                                    )
                                )
                            )
                        ]
                    )
                ]
            ))


        elif page.route == "/home":
            resultado = obtener_libros()
            todos_los_libros = list(resultado["data"]) if resultado["ok"] else []

            texto_busqueda = {"valor": ""}
            genero_activo  = {"valor": None}
            grid_container = ft.Container(expand=True)
            expansion_ref  = ft.Ref[ft.ExpansionTile]()

            def aplicar_filtros():
                txt    = texto_busqueda["valor"].lower().strip()
                genero = genero_activo["valor"]
                filtrados = [
                    l for l in todos_los_libros
                    if (not txt or txt in l[2].lower() or txt in l[3].lower())
                    and (not genero or (l[5] or "").lower() == genero.lower())
                ]
                grid_container.content = crear_grid_libros(page, filtrados)
                page.update()

            def on_buscar(e):
                texto_busqueda["valor"] = e.control.value
                aplicar_filtros()

            generos_unicos = sorted({
                l[5] for l in todos_los_libros
                if l[5] and l[5].strip() and l[5].strip().lower() != "sin género"
            })

            def cerrar_expansion():
                t = expansion_ref.current
                if t:
                    t.controls = construir_tiles()
                    try:
                        t.expanded = False
                    except Exception:
                        pass
                    try:
                        t.update()
                    except Exception:
                        pass

            def construir_tiles():
                tiles = []
                sin_filtro = genero_activo["valor"] is None
                
                def click_todos(_):
                    genero_activo["valor"] = None
                    cerrar_expansion()
                    aplicar_filtros()

                tiles.append(ft.ListTile(
                    title=ft.Text("Todos",
                                  color="#712B33" if sin_filtro else "black",
                                  weight=ft.FontWeight.BOLD if sin_filtro else ft.FontWeight.NORMAL),
                    on_click=click_todos,
                ))

                for g in generos_unicos:
                    es_activo = genero_activo["valor"] == g
                    def hacer_click(genero=g):
                        def _click(_):
                            genero_activo["valor"] = None if genero_activo["valor"] == genero else genero
                            cerrar_expansion()
                            aplicar_filtros()
                        return _click
                    tiles.append(ft.ListTile(
                        title=ft.Text(g,
                                      color="#712B33" if es_activo else "black",
                                      weight=ft.FontWeight.BOLD if es_activo else ft.FontWeight.NORMAL),
                        on_click=hacer_click(g),
                    ))
                return tiles

            grid_container.content = crear_grid_libros(page, todos_los_libros)

            navbar = ft.Container(
                bgcolor="#F0F0F0",
                padding=ft.padding.only(left=20, right=20, top=10, bottom=10),
                width=float("inf"),
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Container(
                            content=ft.Image(src="logo-color-clean-vino.svg", width=150),
                            margin=ft.margin.only(left=10, right=30)
                        ),
                        ft.Container(
                            expand=True,
                            content=ft.TextField(
                                prefix_icon=ft.Icons.SEARCH,
                                expand=True,
                                bgcolor="#712B33",
                                color="white",
                                border_radius=17,
                                hint_text="Buscar libros",
                                hint_style=ft.TextStyle(color=ft.Colors.WHITE54),
                                text_size=12,
                                height=40,
                                content_padding=10,
                                on_change=on_buscar,
                                cursor_color="white",
                            )
                        )
                    ]
                ),
            )

            page.views.append(ft.View(
                route="/home",
                bgcolor="#ffffff",
                padding=0,
                controls=[
                    navbar,
                    ft.Stack(
                        expand=True,
                        controls=[
                            ft.Column(
                                expand=True,
                                scroll=ft.ScrollMode.ALWAYS,
                                controls=[
                                    ft.Container(
                                        padding=ft.padding.only(left=20, right=20, top=10, bottom=10),
                                        content=ft.Text("Libros", size=34, weight=ft.FontWeight.BOLD, color="#000000")
                                    ),
                                    grid_container
                                ]
                            ),
                            ft.Container(
                                width=250, top=10, right=20,
                                bgcolor="#ffffff",
                                border_radius=8,
                                shadow=ft.BoxShadow(blur_radius=8, color="black26"),
                                content=ft.ExpansionTile(
                                    ref=expansion_ref,
                                    title=ft.Text("Filtrar por género", size=16),
                                    maintain_state=True,
                                    collapsed_text_color="#712B33",
                                    text_color="#712B33",
                                    controls=construir_tiles(),
                                )
                            ),
                            ft.Container(
                                content=ft.IconButton(
                                    icon=ft.Icons.PERSON_2_ROUNDED,
                                    icon_color="white",
                                    icon_size=30,
                                    on_click=lambda _: page.go("/perfil"),
                                ),
                                bgcolor="#712B33",
                                shape=ft.BoxShape.CIRCLE,
                                width=60, height=60,
                                shadow=ft.BoxShadow(blur_radius=10, color="black26"),
                                bottom=20, right=20,
                            )
                        ]
                    )
                ]
            ))


        elif "/detalle/" in page.route:
            id_libro = int(page.route.split("/")[-1])
            resultado = obtener_libro_por_id(id_libro)
            if not resultado["ok"]:
                page.go("/home")
                return
            libro = resultado["data"]

            page.views.append(ft.View(
                route=page.route,
                bgcolor="#ffffff",
                appbar=ft.AppBar(
                    title=ft.Text("Detalle del Libro", color="white"),
                    bgcolor="#712B33",
                    leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color="white",
                                          on_click=lambda _: page.go("/home"))
                ),
                controls=[
                    ft.Container(
                        expand=True,
                        padding=ft.padding.all(20),
                        content=ft.Row(
                            spacing=30,
                            vertical_alignment=ft.CrossAxisAlignment.START,
                            controls=[
                                ft.Column(
                                    alignment=ft.MainAxisAlignment.START,
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=10,
                                    controls=[
                                        imagen_portada(libro[2], height=500),
                                        ft.Text(
                                            f"{libro[5]} | Código: {libro[1]}",
                                            size=14, weight=ft.FontWeight.BOLD, color="#000000",
                                            bgcolor="#D9D9D9", text_align=ft.TextAlign.CENTER
                                        ),
                                    ]
                                ),
                                ft.Container(
                                    expand=True,
                                    content=ft.Column(
                                        spacing=20,
                                        horizontal_alignment=ft.CrossAxisAlignment.START,
                                        controls=[
                                            ft.Text(libro[2], size=65, weight=ft.FontWeight.BOLD, color="black"),
                                            ft.Text(f"Autor: {libro[3]}", size=16, color=ft.Colors.BLACK54),
                                            ft.Text(
                                                f"Disponibles: {libro[4]} copia(s)",
                                                size=16, weight=ft.FontWeight.BOLD,
                                                color="green" if libro[4] > 0 else "red"
                                            ),
                                            ft.Divider(),
                                        ]
                                    )
                                )
                            ]
                        )
                    )
                ]
            ))


        elif page.route == "/perfil":
            usuario = getattr(page, "usuario_actual", None)
            if not usuario:
                page.go("/login")
                return

            es_alumno = usuario.get("rol") == "Alumno"
            prestamos_activos = []
            if es_alumno:
                r = obtener_prestamos_usuario(usuario["id"])
                prestamos_activos = list(r["data"]) if r["ok"] else []

            contenedor_grid = ft.Container(expand=False)
            if es_alumno:
                contenedor_grid.content = crear_grid_prestamos(page, prestamos_activos)

            def confirmar_logout(e):
                dlg_logout.open = False 
                page.update()
                page.usuario_actual = None
                limpiar_campos_login()
                page.go("/login")

            def cancelar_logout(e):
                dlg_logout.open = False 
                page.update()

            dlg_logout = ft.AlertDialog(
                modal=True,
                shape=ft.RoundedRectangleBorder(radius=10),
                bgcolor="#ffffff",
                content_padding=30,
                content=ft.Container(
                    width=250, height=90,
                    content=ft.Column(
                        expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15,
                        controls=[ft.Text("¿Cerrar Sesión?", size=22, weight=ft.FontWeight.BOLD, color="black")]
                    )
                ),
                actions=[
                    ft.ElevatedButton("Cancelar", on_click=cancelar_logout,
                                      bgcolor="grey", color="white", width=120, height=45),
                    ft.ElevatedButton("Sí, salir", on_click=confirmar_logout,
                                      bgcolor="#B53548", color="white", width=120, height=45)
                ],
                actions_alignment=ft.MainAxisAlignment.CENTER,
            )

            def abrir_logout(e):
                page.overlay.append(dlg_logout) 
                dlg_logout.open = True
                page.update()

            campo_nueva = ft.TextField(label="Nueva Contraseña", password=True,
                                       can_reveal_password=True, border_color="#712B33",
                                       cursor_color="#712B33")
            campo_conf  = ft.TextField(label="Confirmar Contraseña", password=True,
                                       can_reveal_password=True, border_color="#712B33",
                                       cursor_color="#712B33")

            def cerrar_dlg_pass(e):
                dlg_pass.open = False
                page.update()

            def guardar_pass(e):
                if not campo_nueva.value or not campo_conf.value:
                    mostrar_dialogo("Aviso", "Ambos campos son obligatorios.")
                    return
                if campo_nueva.value != campo_conf.value:
                    mostrar_dialogo("Aviso", "Las contraseñas no coinciden.")
                    return
                if campo_nueva.value.strip() == "":
                    mostrar_dialogo("Aviso", "La contraseña no puede tener solo espacios.")
                    return
                import bcrypt
                try:
                    db  = get_db()
                    cur = db.cursor()
                    h   = bcrypt.hashpw(campo_nueva.value.encode(), bcrypt.gensalt()).decode()
                    cur.execute("UPDATE Usuarios SET Contrasena=%s WHERE Id_Usuario=%s",
                                (h, usuario["id"]))
                    db.commit()
                    cur.close(); db.close()
                    dlg_pass.open = False 
                    page.update()
                    mostrar_dialogo("Éxito", "Contraseña actualizada correctamente.")
                except Exception as ex:
                    dlg_pass.open = False 
                    page.update()
                    mostrar_dialogo("Error", f"No se pudo actualizar: {ex}")

            dlg_pass = ft.AlertDialog(
                modal=True,
                shape=ft.RoundedRectangleBorder(radius=10),
                bgcolor="#ffffff",
                title=ft.Text("Cambiar Contraseña", weight=ft.FontWeight.BOLD, color="black"),
                content=ft.Column([campo_nueva, campo_conf], tight=True, spacing=15),
                actions=[
                    ft.TextButton("Cancelar", on_click=cerrar_dlg_pass,
                                  style=ft.ButtonStyle(color="grey")),
                    ft.ElevatedButton("Guardar", on_click=guardar_pass,
                                      bgcolor="#712B33", color="white")
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )

            def abrir_dlg_pass(e):
                campo_nueva.value = ""
                campo_conf.value  = ""
                page.overlay.append(dlg_pass) 
                dlg_pass.open = True
                page.update()

            controles_perfil = [
                ft.Text("Información de Perfil", size=24, weight=ft.FontWeight.BOLD, color="black"),
                ft.Container(
                    padding=ft.padding.symmetric(vertical=15, horizontal=5),
                    content=ft.Column(spacing=15, controls=[
                        ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                            ft.Text(usuario.get("nombre", "N/A"), size=26,
                                    weight=ft.FontWeight.BOLD, color="#712B33"),
                            ft.Text(usuario.get("rol", "N/A"), size=22,
                                    weight=ft.FontWeight.BOLD, color="#712B33"),
                        ]),
                        ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                            ft.Text(f"ID Usuario: {usuario.get('id', 'N/A')}",
                                    size=14, color=ft.Colors.BLACK54),
                            ft.TextButton(
                                "Cambiar Contraseña",
                                icon=ft.Icons.LOCK_RESET,
                                icon_color="#712B33",
                                style=ft.ButtonStyle(color="#712B33"),
                                on_click=abrir_dlg_pass
                            )
                        ])
                    ])
                )
            ]
            if es_alumno:
                controles_perfil.append(ft.Divider())
                controles_perfil.append(
                    ft.Text(f"Mis Préstamos Activos ({len(prestamos_activos)})",
                            size=20, weight=ft.FontWeight.BOLD, color="black")
                )
                controles_perfil.append(contenedor_grid)

            def ruta_retorno():
                r = usuario.get("rol")
                if r == "Administrador": return "/admin-inicio"
                if r == "Bibliotecario": return "/biblio-inicio"
                return "/home"

            page.views.append(ft.View(
                route="/perfil",
                bgcolor="#ffffff",
                padding=0,
                appbar=ft.AppBar(
                    title=ft.Text("Mi Perfil", color="white"),
                    bgcolor="#712B33",
                    leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color="white",
                                          on_click=lambda _: page.go(ruta_retorno()))
                ),
                controls=[
                    ft.Stack(
                        expand=True,
                        controls=[
                            ft.Container(
                                expand=True, padding=40,
                                content=ft.Column(scroll=ft.ScrollMode.ALWAYS, controls=controles_perfil)
                            ),
                            ft.Container(
                                content=ft.IconButton(
                                    icon=ft.Icons.LOGOUT,
                                    icon_color="white", icon_size=30,
                                    on_click=abrir_logout, tooltip="Cerrar Sesión"
                                ),
                                bgcolor="#B53548",
                                shape=ft.BoxShape.CIRCLE,
                                width=60, height=60,
                                shadow=ft.BoxShadow(blur_radius=10, color="black26"),
                                bottom=20, right=20,
                            )
                        ]
                    )
                ]
            ))

        # Rutas admin
        elif page.route == "/admin-inicio":
            page.views.append(vista_dashboard_admin(page))
        elif page.route == "/admin-usuarios":
            page.views.append(vista_gestion_usuarios(page))
        elif page.route == "/admin-libros":
            page.views.append(vista_gestion_Libros(page, modo="admin"))
        elif page.route == "/admin-prestamos":
            page.views.append(vista_gestion_Prestamos(page))

        # Rutas bibliotecario
        elif page.route == "/biblio-inicio":
            page.views.append(vista_dashboard_bibliotecario(page))
        elif page.route == "/biblio-libros":
            page.views.append(vista_gestion_Libros(page, modo="biblio"))
        elif page.route == "/biblio-prestamos":
            page.views.append(vista_gestion_Prestamos(page))

        page.update()

    def view_pop(view):
         if len(page.views) > 1:
            page.views.pop()
            page.go(page.views[-1].route)
         else:
             page.go("/")

    page.on_route_change = route_change
    page.on_view_pop     = view_pop
    page.go("/login")


def obtener_ruta_assets():
    try:
        base = sys._MEIPASS
    except AttributeError:
        base = os.path.dirname(os.path.abspath(__file__))
    
    ruta_final = os.path.join(base, "assets")
    print(f"Buscando assets en: {ruta_final}")
    return ruta_final

ft.app(target=main, assets_dir=obtener_ruta_assets())

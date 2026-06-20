import flet as ft
from services.usuarios import crear_usuario
from services.alumnos import obtener_prestamos_con_penalizacion
from services.prestamos import contar_prestamos_activos, obtener_prestamos_activos
from sgbe_admin import (
    vista_gestion_Libros, vista_gestion_Prestamos,
    popup_libroP, boton, vista_gestion_usuarios
)


def abrir_popup_nuevo_alumno(page: ft.Page):
    f_nombre = ft.TextField(label="Nombre Completo")
    f_login  = ft.TextField(label="Usuario / Email (Login)")
    f_pass   = ft.TextField(label="Contraseña", password=True)

    def cerrar(e):
        dlg.open = False
        page.update()

    def _alerta(titulo, mensaje):
        def _ok(e):
            a.open = False
            page.update()
        a = ft.AlertDialog(
            modal=True,
            title=ft.Text(titulo, weight="bold", color="black"),
            content=ft.Text(mensaje),
            actions=[ft.ElevatedButton("OK", on_click=_ok, bgcolor="#712B33", color="white")],
            actions_alignment="center",
        )
        page.overlay.append(a)
        a.open = True
        page.update()

    def guardar(e):
        nombre = (f_nombre.value or "").strip()
        login_ = (f_login.value  or "").strip()
        pwd    = f_pass.value or ""

        if not nombre:
            _alerta("Error", "El nombre es obligatorio.")
            return
        if not login_:
            _alerta("Error", "El usuario/email es obligatorio.")
            return
        if " " in login_:
            _alerta("Error", "El usuario/email no puede tener espacios.")
            return
        if not pwd.strip():
            _alerta("Error", "La contraseña es obligatoria.")
            return
        if len(pwd) < 6:
            _alerta("Error", "Mínimo 6 caracteres.")
            return

        res = crear_usuario(nombre=nombre, rol="Alumno", login=login_, password=pwd)
        if res.get("ok"):
            dlg.open = False
            page.update()
            _alerta("Éxito", "Alumno registrado correctamente.")
        else:
            _alerta("Error", res.get("msg", "Error al registrar."))

    dlg = ft.AlertDialog(
        modal=True,
        shape=ft.RoundedRectangleBorder(radius=10),
        bgcolor="#ffffff",
        content_padding=30,
        content=ft.Container(
            width=500,
            height=300,
            content=ft.Column(
                expand=True,
                horizontal_alignment="center",
                spacing=15,
                controls=[
                    ft.Text("Registrar Nuevo Alumno", size=22, weight="bold",
                            text_align="center", color="black"),
                    f_nombre,
                    f_login,
                    f_pass,
                ]
            )
        ),
        actions=[
            ft.ElevatedButton("Cancelar", on_click=cerrar, bgcolor="grey", color="white", width=120, height=45),
            ft.ElevatedButton("Registrar", on_click=guardar, bgcolor="#712B33", color="white", width=120, height=45),
        ],
        actions_alignment="center",
    )
    page.overlay.append(dlg)
    dlg.open = True
    page.update()


def vista_dashboard_bibliotecario(page: ft.Page):
    # Datos reales desde BD
    total_prestados = contar_prestamos_activos()
    res = obtener_prestamos_activos()
    lista_libros = [f"• {fila[2]}" for fila in res.get("data", [])]
    texto_libros = "\n".join(lista_libros) if lista_libros else "No hay libros prestados."

    # CORRECCIÓN: Obtener usuarios atrasados (penalizados) correctamente
    res_pen = obtener_prestamos_con_penalizacion()
    
    # Contar usuarios ÚNICOS con penalizaciones
    usuarios_penalizados = set()
    if res_pen.get("ok"):
        for prestamo in res_pen["data"]:
            # prestamo[2] es el nombre del alumno
            usuarios_penalizados.add(prestamo[2])
    
    total_pen = len(usuarios_penalizados)
    lista_pen = [f"• {nombre}" for nombre in sorted(usuarios_penalizados)]
    texto_pen = "\n".join(lista_pen) if lista_pen else "No hay usuarios con penalizaciones."

    navbar = ft.Container(
        content=ft.Row(
            alignment="spaceBetween",
            controls=[
                ft.Container(content=ft.Image(src="logo-color-clean-vino.svg", width=150),
                             margin=ft.margin.only(left=10, right=30)),
                ft.Text("Panel de Bibliotecario", size=24, weight="bold", color="#712B33")
            ]
        ),
        bgcolor="#F0F0F0",
        padding=ft.padding.only(left=20, right=20, top=10, bottom=10),
        width=float("inf"),
    )

    btn_perfil = ft.Container(
        content=ft.IconButton(icon=ft.Icons.PERSON_2_ROUNDED, icon_color="white",
                              icon_size=30, on_click=lambda _: page.go("/perfil")),
        bgcolor="#712B33", shape=ft.BoxShape.CIRCLE,
        width=60, height=60,
        shadow=ft.BoxShadow(blur_radius=10, color="black26"),
        bottom=20, right=20,
    )

    return ft.View(
        route="/biblio-inicio", bgcolor="#ffffff", padding=0,
        controls=[
            ft.Stack(expand=True, controls=[
                ft.Column(spacing=80, controls=[
                    navbar,
                    ft.Container(
                        margin=ft.margin.only(top=50, bottom=50, right=50, left=50),
                        content=ft.Row(alignment="spaceBetween", controls=[
                            boton(f"Libros prestados\n({total_prestados})",
                                  lambda _: popup_libroP(page, "Libros Prestados", texto_libros),
                                  color_fondo="#1AFF00", color_texto="black", ancho=450),
                            boton(f"Usuarios atrasados\n({total_pen})",
                                  lambda _: popup_libroP(page, "Usuarios Atrasados", texto_pen),
                                  color_fondo="#FF0000", color_texto="black", ancho=450),
                        ])
                    ),
                    ft.Container(content=ft.Row(alignment="center", spacing=30, controls=[
                        boton("Registrar Alumno",
                              lambda _: abrir_popup_nuevo_alumno(page),
                              color_fondo="#712B33", color_texto="white", ancho=280),
                        boton("Gestionar Libros",
                              lambda _: page.go("/biblio-libros"),
                              color_fondo="#712B33", color_texto="white", ancho=280),
                        boton("Préstamos",
                              lambda _: page.go("/biblio-prestamos"),
                              color_fondo="#712B33", color_texto="white", ancho=280),
                    ])),
                ]),
                btn_perfil,
            ])
        ]
    )
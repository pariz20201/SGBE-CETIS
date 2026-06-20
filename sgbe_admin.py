import flet as ft
from datetime import datetime, date
from services.libros import crear_libro, eliminar_libro, buscar_libro, obtener_libro_por_codigo, actualizar_descripcion_libro
from services.usuarios import crear_usuario, obtener_usuarios, actualizar_usuario, eliminar_usuario, buscar_alumno_por_nombre
from services.prestamos import (
    contar_prestamos_activos, obtener_prestamos_activos,
    obtener_prestamos, devolver_libro, crear_prestamo_con_fecha
)
from services.alumnos import quitar_penalizacion_alumno



def crear_navbar(page: ft.Page):
    usuario = getattr(page, "usuario_actual", None)
    titulo  = "Bibliotecario" if (usuario and usuario.get("rol") == "Bibliotecario") else "Administración"
    return ft.Container(
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Container(
                    content=ft.Image(src="logo-color-clean-vino.svg", width=150),
                    margin=ft.margin.only(left=10, right=30)
                ),
                ft.Text(f"Panel de {titulo}", size=24, weight="bold", color="#712B33")
            ]
        ),
        bgcolor="#F0F0F0",
        padding=ft.padding.only(left=20, right=20, top=10, bottom=10),
        width=float("inf"),
    )


def boton(texto, accion, color_fondo="#712B33", color_texto="white", ancho=0):
    alto = max(int(ancho * 0.3), 40)
    return ft.Container(
        content=ft.ElevatedButton(
            content=ft.Text(texto, size=max(int(ancho * 0.07), 12),
                            weight="bold", text_align="center"),
            on_click=accion,
            style=ft.ButtonStyle(
                bgcolor=color_fondo,
                color=color_texto,
                shape=ft.RoundedRectangleBorder(radius=10),
                overlay_color="#44ffffff",
            ),
        ),
        width=ancho,
        height=alto,
    )


def popup_libroP(page, titulo, mensaje):
    def cerrar(e):
        dlg.open = False
        page.update()
    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text(titulo, weight="bold"),
        content=ft.Text(mensaje),
        actions=[ft.TextButton("Cerrar", on_click=cerrar)],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.overlay.append(dlg)
    dlg.open = True
    page.update()


def _alerta(page, titulo, mensaje):
    def _ok(e):
        dlg.open = False
        page.update()
    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text(titulo, weight="bold", color="black"),
        content=ft.Text(mensaje),
        actions=[ft.ElevatedButton("OK", on_click=_ok, bgcolor="#712B33", color="white")],
        actions_alignment="center",
    )
    page.overlay.append(dlg)
    dlg.open = True
    page.update()


def abrir_popup_usuario(page, funcion_actualizar=None):
    f_nombre = ft.TextField(label="Nombre")
    f_login  = ft.TextField(label="Login")
    f_rol    = ft.Dropdown(label="Rol", options=[
        ft.dropdown.Option("Bibliotecario"),
        ft.dropdown.Option("Alumno"),
        ft.dropdown.Option("Administrador"),
    ])
    f_pass   = ft.TextField(label="Contraseña", password=True)

    def cerrar(e):
        dlg.open = False; page.update()

    def guardar(e):
        nombre = (f_nombre.value or "").strip()
        login_ = (f_login.value  or "").strip()
        rol    = f_rol.value
        pwd    = f_pass.value or ""

        if not nombre: _alerta(page, "Error", "El nombre es obligatorio."); return
        if not login_: _alerta(page, "Error", "El login es obligatorio."); return
        if " " in login_: _alerta(page, "Error", "El login no puede tener espacios."); return
        if not rol: _alerta(page, "Error", "Selecciona un rol."); return
        if not pwd.strip(): _alerta(page, "Error", "La contraseña es obligatoria."); return
        if len(pwd) < 6: _alerta(page, "Error", "Mínimo 6 caracteres."); return

        res = crear_usuario(nombre=nombre, rol=rol, login=login_, password=pwd)
        if res.get("ok"):
            dlg.open = False; page.update()
            if funcion_actualizar: funcion_actualizar()
        else:
            _alerta(page, "Error", res.get("msg", "Error al crear usuario."))

    dlg = ft.AlertDialog(
        modal=True, shape=ft.RoundedRectangleBorder(radius=10),
        bgcolor="#ffffff", content_padding=30,
        content=ft.Container(width=500, height=350,
            content=ft.Column(expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15,
                controls=[
                    ft.Text("Nuevo Usuario", size=22, weight="bold", color="black"),
                    f_nombre, f_login, f_rol, f_pass,
                ])
        ),
        actions=[
            ft.ElevatedButton("Cancelar", on_click=cerrar, bgcolor="grey", color="white", width=120, height=45),
            ft.ElevatedButton("Aceptar",  on_click=guardar, bgcolor="#712B33", color="white", width=120, height=45),
        ],
        actions_alignment=ft.MainAxisAlignment.CENTER,
    )
    page.overlay.append(dlg); dlg.open = True; page.update()


def abrir_popup_editar_usuario(page, usuario, funcion_actualizar=None):
    f_nombre = ft.TextField(label="Nombre", value=str(usuario.get("nombre", "")))
    f_login  = ft.TextField(label="Login",  value=str(usuario.get("login",  "")))
    f_rol    = ft.Dropdown(label="Rol", value=str(usuario.get("rol", "Alumno")),
        options=[
            ft.dropdown.Option("Bibliotecario"),
            ft.dropdown.Option("Alumno"),
            ft.dropdown.Option("Administrador"),
        ])

    def cerrar(e):
        dlg.open = False; page.update()

    def guardar(e):
        nombre = (f_nombre.value or "").strip()
        login_ = (f_login.value  or "").strip()
        rol    = f_rol.value
        if not nombre: _alerta(page, "Error", "El nombre es obligatorio."); return
        if not login_: _alerta(page, "Error", "El login es obligatorio."); return
        if " " in login_: _alerta(page, "Error", "El login no puede tener espacios."); return
        if not rol: _alerta(page, "Error", "Selecciona un rol."); return
        res = actualizar_usuario(id_user=usuario.get("id"),
                                 nombre=nombre, rol=rol, login=login_)
        if res.get("ok"):
            dlg.open = False; page.update()
            if funcion_actualizar: funcion_actualizar()
        else:
            _alerta(page, "Error", res.get("msg", "Error al actualizar."))

    dlg = ft.AlertDialog(
        modal=True, shape=ft.RoundedRectangleBorder(radius=10),
        bgcolor="#ffffff", content_padding=30,
        content=ft.Container(width=500, height=300,
            content=ft.Column(expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15,
                controls=[
                    ft.Text("Editar Usuario", size=22, weight="bold", color="black"),
                    f_nombre, f_login, f_rol,
                ])
        ),
        actions=[
            ft.ElevatedButton("Cancelar", on_click=cerrar, bgcolor="grey", color="white", width=120, height=45),
            ft.ElevatedButton("Aceptar",  on_click=guardar, bgcolor="#712B33", color="white", width=120, height=45),
        ],
        actions_alignment=ft.MainAxisAlignment.CENTER,
    )
    page.overlay.append(dlg); dlg.open = True; page.update()



def abrir_popup_eliminar(page, datos_combinados, id_usuario, funcion_actualizar):
    def cerrar(e):
        dlg.open = False; page.update()
    def confirmar(e):
        resultado = eliminar_usuario(id_usuario)
        if resultado["ok"] and funcion_actualizar:
            funcion_actualizar()
        dlg.open = False; page.update()

    dlg = ft.AlertDialog(
        modal=True, shape=ft.RoundedRectangleBorder(radius=10),
        bgcolor="#ffffff", content_padding=30,
        content=ft.Container(width=500, height=180,
            content=ft.Column(expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15,
                controls=[
                    ft.Text("¿Eliminar a este usuario?", size=18, color="black"),
                    ft.Text(datos_combinados, size=22, weight="bold",
                            text_align="center", color="#712B33"),
                ])
        ),
        actions=[
            ft.ElevatedButton("Cancelar",     on_click=cerrar,    bgcolor="grey",    color="white", width=120, height=45),
            ft.ElevatedButton("Sí, eliminar", on_click=confirmar, bgcolor="#712B33", color="white", width=120, height=45),
        ],
        actions_alignment=ft.MainAxisAlignment.CENTER,
    )
    page.overlay.append(dlg); dlg.open = True; page.update()



def abrir_popup_libro(page, funcion_actualizar=None):
    f_codigo   = ft.TextField(label="Código (ISBN)", dense=True)
    f_titulo   = ft.TextField(label="Título",        dense=True)
    f_autor    = ft.TextField(label="Autor",         dense=True)
    f_genero   = ft.TextField(label="Género",        dense=True)
    f_cantidad = ft.TextField(label="Cantidad",      dense=True, value="1")
    f_desc     = ft.TextField(label="Descripción / Estado del libro",
                              dense=True, multiline=True, min_lines=2)

    def cerrar(e):
        dlg.open = False; page.update()

    def guardar(e):
        codigo = (f_codigo.value   or "").strip()
        titulo = (f_titulo.value   or "").strip()
        autor  = (f_autor.value    or "").strip()
        genero = (f_genero.value   or "").strip()
        cant_s = (f_cantidad.value or "").strip()
        desc   = (f_desc.value     or "").strip()

        if not codigo: _alerta(page, "Error", "El código es obligatorio."); return
        if not titulo: _alerta(page, "Error", "El título es obligatorio."); return
        if not autor:  _alerta(page, "Error", "El autor es obligatorio.");  return
        if not genero: _alerta(page, "Error", "El género es obligatorio."); return
        if not cant_s.isdigit() or int(cant_s) <= 0:
            _alerta(page, "Error", "La cantidad debe ser un número mayor a 0."); return

        res = crear_libro(codigo=codigo, titulo=titulo, autor=autor,
                          cantidad=int(cant_s), genero=genero, descripcion=desc)
        if res.get("ok"):
            dlg.open = False; page.update()
            if funcion_actualizar: funcion_actualizar()
        else:
            _alerta(page, "Error", res.get("msg", "Error al crear libro."))

    dlg = ft.AlertDialog(
        modal=True, shape=ft.RoundedRectangleBorder(radius=10),
        bgcolor="#ffffff", content_padding=20,
        content=ft.Container(width=420, height=420,
            content=ft.Column(expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10,
                controls=[
                    ft.Text("Detalles del libro", size=20, weight="bold", color="black"),
                    f_codigo, f_titulo, f_autor, f_genero, f_cantidad, f_desc,
                ])
        ),
        actions=[
            ft.ElevatedButton("Cancelar", on_click=cerrar,  bgcolor="grey",    color="white", width=120, height=40),
            ft.ElevatedButton("Guardar",  on_click=guardar, bgcolor="#712B33", color="white", width=120, height=40),
        ],
        actions_alignment=ft.MainAxisAlignment.CENTER,
    )
    page.overlay.append(dlg); dlg.open = True; page.update()



def abrir_popup_eliminar_libro(page, datos_combinados, id_libro, funcion_actualizar):
    def cerrar(e):
        dlg.open = False
        page.update()
    
    def confirmar(e):
        res = eliminar_libro(id_libro)
        dlg.open = False
        page.update()
        if res.get("ok"):
            _alerta(page, "Éxito", "Libro eliminado correctamente.")
            if funcion_actualizar:
                funcion_actualizar()
        else:
            _alerta(page, "Error", res.get("msg", "No se pudo eliminar el libro."))

    dlg = ft.AlertDialog(
        modal=True,
        shape=ft.RoundedRectangleBorder(radius=10),
        bgcolor="#ffffff",
        content_padding=30,
        content=ft.Container(
            width=500,
            height=180,
            content=ft.Column(
                expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15,
                controls=[
                    ft.Text("¿Eliminar este libro?", size=18, color="black"),
                    ft.Text(datos_combinados, size=22, weight="bold",
                            text_align="center", color="#712B33"),
                ]
            )
        ),
        actions=[
            ft.ElevatedButton("Cancelar", on_click=cerrar, bgcolor="grey", color="white", width=120, height=45),
            ft.ElevatedButton("Sí, eliminar", on_click=confirmar, bgcolor="#B53548", color="white", width=120, height=45),
        ],
        actions_alignment=ft.MainAxisAlignment.CENTER,
    )
    page.overlay.append(dlg)
    dlg.open = True
    page.update()


def abrir_popup_editar_descripcion(page, libro_data, funcion_actualizar=None):
    id_libro = libro_data[0]
    titulo   = libro_data[2]
    desc_actual = libro_data[6] if len(libro_data) > 6 else ""

    f_desc = ft.TextField(
        label="Descripción / Estado del libro",
        value=str(desc_actual) if desc_actual else "",
        multiline=True,
        min_lines=3,
        max_lines=6,
    )

    def cerrar(e):
        dlg.open = False; page.update()

    def guardar(e):
        res = actualizar_descripcion_libro(id_libro, (f_desc.value or "").strip())
        dlg.open = False; page.update()
        if res.get("ok"):
            _alerta(page, "Éxito", "Descripción actualizada.")
            if funcion_actualizar: funcion_actualizar()
        else:
            _alerta(page, "Error", res.get("msg", "No se pudo actualizar."))

    dlg = ft.AlertDialog(
        modal=True, shape=ft.RoundedRectangleBorder(radius=10),
        bgcolor="#ffffff", content_padding=30,
        content=ft.Container(width=460, height=240,
            content=ft.Column(expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12,
                controls=[
                    ft.Text("Editar estado del libro", size=20, weight="bold", color="black"),
                    ft.Text(titulo, size=14, color="black54"),
                    f_desc,
                ])
        ),
        actions=[
            ft.ElevatedButton("Cancelar", on_click=cerrar,  bgcolor="grey",    color="white", width=120, height=45),
            ft.ElevatedButton("Guardar",  on_click=guardar, bgcolor="#712B33", color="white", width=120, height=45),
        ],
        actions_alignment=ft.MainAxisAlignment.CENTER,
    )
    page.overlay.append(dlg); dlg.open = True; page.update()



def abrir_popup_agregar_prestamo(page, funcion_actualizar=None):
    f_alumno = ft.TextField(label="Nombre del alumno", dense=True)
    f_codigo = ft.TextField(label="Código del libro (ISBN)", dense=True)

    hoy = date.today()
    fecha_sel = {"valor": None}
    txt_fecha = ft.Text("Fecha límite: no seleccionada", size=13, color="black54")

    def on_fecha(e):
        if e.control.value:
            fecha_sel["valor"] = e.control.value
            txt_fecha.value = f"Fecha límite: {e.control.value.strftime('%d/%m/%Y')}"
            txt_fecha.color = "#712B33"
        page.update()

    dp = ft.DatePicker(
        first_date=datetime(hoy.year, hoy.month, hoy.day),
        last_date=datetime(hoy.year + 2, 12, 31),
        on_change=on_fecha,
    )
    page.overlay.append(dp)

    def abrir_cal(e):
        dp.open = True
        page.update()

    def cerrar(e):
        dlg.open = False
        page.update()

    def registrar(e):
        nombre = (f_alumno.value or "").strip()
        codigo = (f_codigo.value or "").strip()

        if not nombre:
            _alerta(page, "Error", "Escribe el nombre del alumno.")
            return
        if not codigo:
            _alerta(page, "Error", "Escribe el código del libro.")
            return
        if not fecha_sel["valor"]:
            _alerta(page, "Error", "Selecciona una fecha límite.")
            return

        r_alum = buscar_alumno_por_nombre(nombre)
        if not r_alum.get("ok"):
            _alerta(page, "Error", r_alum.get("msg", f"Alumno '{nombre}' no encontrado."))
            return
        alumno = r_alum["data"]

        if alumno.get("rol") != "Alumno":
            _alerta(page, "Error", f"'{nombre}' no es un alumno.")
            return

        if alumno.get("penalizaciones_activas") or alumno.get("pen_act"):
            _alerta(page, "Error", f"El alumno '{nombre}' tiene penalizaciones activas. No se puede prestarle libros.")
            return

        r_libro = obtener_libro_por_codigo(codigo)
        if not r_libro.get("ok"):
            _alerta(page, "Error", r_libro.get("msg", f"Libro '{codigo}' no encontrado."))
            return
        libro = r_libro["data"]

        disponibles = libro[7] if len(libro) > 7 else libro[4]
        if disponibles <= 0:
            _alerta(page, "Error", f"No hay copias disponibles de '{libro[2]}'.")
            return

        r_p = crear_prestamo_con_fecha(
            id_alumno=alumno["id"],
            id_libro=libro[0],
            fecha_devolucion=fecha_sel["valor"]
        )
        if r_p.get("ok"):
            dlg.open = False
            page.update()
            _alerta(page, "Éxito", f"Préstamo creado para {nombre}.")
            if funcion_actualizar:
                funcion_actualizar()
        else:
            _alerta(page, "Error", r_p.get("msg", "No se pudo crear el préstamo."))

    dlg = ft.AlertDialog(
        modal=True,
        shape=ft.RoundedRectangleBorder(radius=10),
        bgcolor="#ffffff",
        content_padding=30,
        content=ft.Container(
            width=460,
            height=250,
            content=ft.Column(
                expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15,
                controls=[
                    ft.Text("Agregar Préstamo", size=22, weight="bold", color="black"),
                    f_alumno,
                    f_codigo,
                    ft.Row(alignment="center", controls=[
                        txt_fecha,
                        ft.IconButton(
                            icon=ft.Icons.CALENDAR_MONTH,
                            icon_color="#712B33",
                            tooltip="Seleccionar fecha límite",
                            on_click=abrir_cal
                        )
                    ]),
                ]
            )
        ),
        actions=[
            ft.ElevatedButton("Cancelar", on_click=cerrar, bgcolor="grey", color="white", width=120, height=45),
            ft.ElevatedButton("Registrar", on_click=registrar, bgcolor="#712B33", color="white", width=120, height=45),
        ],
        actions_alignment=ft.MainAxisAlignment.CENTER,
    )
    page.overlay.append(dlg)
    dlg.open = True
    page.update()



def abrir_popup_quitar_penalizacion(page, id_alumno, nombre_alumno, funcion_actualizar=None):
    def cerrar(e):
        dlg.open = False
        page.update()

    def confirmar(e):
        res = quitar_penalizacion_alumno(id_alumno)
        dlg.open = False
        page.update()
        if res.get("ok"):
            _alerta(page, "Éxito", f"Penalización de {nombre_alumno} eliminada correctamente.")
            if funcion_actualizar:
                funcion_actualizar()
        else:
            _alerta(page, "Error", res.get("msg", "No se pudo quitar la penalización."))

    dlg = ft.AlertDialog(
        modal=True,
        shape=ft.RoundedRectangleBorder(radius=10),
        bgcolor="#ffffff",
        content_padding=30,
        content=ft.Container(
            width=440,
            height=150,
            content=ft.Column(
                expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
                controls=[
                    ft.Text("¿Quitar penalización?", size=20, weight="bold", color="black"),
                    ft.Text(f"Alumno: {nombre_alumno}", size=14, color="black54"),
                ]
            )
        ),
        actions=[
            ft.ElevatedButton("Cancelar", on_click=cerrar, bgcolor="grey", color="white", width=120, height=45),
            ft.ElevatedButton("Confirmar", on_click=confirmar, bgcolor="#712B33", color="white", width=120, height=45),
        ],
        actions_alignment=ft.MainAxisAlignment.CENTER,
    )
    page.overlay.append(dlg)
    dlg.open = True
    page.update()



def vista_dashboard_admin(page: ft.Page):
    total_prestados = contar_prestamos_activos()
    res = obtener_prestamos_activos()
    lista = [f"• {fila[2]}" for fila in res.get("data", [])]
    texto_libros = "\n".join(lista) if lista else "No hay libros prestados en este momento."

    from services.alumnos import obtener_prestamos_con_penalizacion
    res_pen = obtener_prestamos_con_penalizacion()
    
    usuarios_penalizados = set()
    if res_pen.get("ok"):
        for prestamo in res_pen["data"]:
            usuarios_penalizados.add(prestamo[2])
    
    total_pen = len(usuarios_penalizados)
    lista_pen = [f"• {nombre}" for nombre in sorted(usuarios_penalizados)]
    texto_pen = "\n".join(lista_pen) if lista_pen else "No hay usuarios con penalizaciones."

    boton_flotante = ft.Container(
        content=ft.IconButton(icon=ft.Icons.PERSON_2_ROUNDED, icon_color="white",
                              icon_size=30, on_click=lambda _: page.go("/perfil")),
        bgcolor="#712B33", shape=ft.BoxShape.CIRCLE,
        width=60, height=60,
        shadow=ft.BoxShadow(blur_radius=10, color="black26"),
        bottom=20, right=20,
    )

    return ft.View(
        route="/admin-inicio", bgcolor="#ffffff", padding=0,
        controls=[
            ft.Stack(expand=True, controls=[
                ft.Column(spacing=80, controls=[
                    crear_navbar(page),
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
                        boton("Usuarios",        lambda _: page.go("/admin-usuarios"),  ancho=280),
                        boton("Gestionar Libros",lambda _: page.go("/admin-libros"),    ancho=280),
                        boton("Préstamos",       lambda _: page.go("/admin-prestamos"), ancho=280),
                    ])),
                ]),
                boton_flotante,
            ])
        ]
    )



def vista_gestion_usuarios(page: ft.Page):
    tabla = ft.DataTable(
        width=float("inf"),
        show_checkbox_column=False,
        border=ft.border.all(1, "#712B33"),
        border_radius=10,
        heading_row_color="#F5F5F5",
        columns=[
            ft.DataColumn(ft.Text("Nombre",     weight="bold", color="#712B33")),
            ft.DataColumn(ft.Text("Login",      weight="bold", color="#712B33")),
            ft.DataColumn(ft.Text("Rol",        weight="bold", color="#712B33")),
        ],
        rows=[]
    )

    def filtrar(e):
        txt = e.control.value.lower()
        for fila in tabla.rows:
            fila.visible = txt in " ".join(
                str(c.content.value).lower() for c in fila.cells)
        tabla.update()

    campo_busqueda = ft.TextField(label="Buscar usuario...",
                                  prefix_icon=ft.Icons.SEARCH, width=400, on_change=filtrar)

    def seleccionar_fila(e):
        sel = e.control.selected
        for f in tabla.rows:
            f.selected = False; f.color = None
            for c in f.cells:
                if isinstance(c.content, ft.Text): c.content.color = None
        if not sel:
            e.control.selected = True; e.control.color = "#2D2D2D"
            for c in e.control.cells:
                if isinstance(c.content, ft.Text): c.content.color = "white"
        try: tabla.update()
        except Exception: pass

    def cargar(inicial=False):
        tabla.rows.clear()
        res = obtener_usuarios()
        if res["ok"]:
            for u in res["data"]:
                tabla.rows.append(ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(u[1]))),
                        ft.DataCell(ft.Text(str(u[3]))),
                        ft.DataCell(ft.Text(str(u[2]))),
                    ],
                    selected=False, on_select_change=seleccionar_fila, data=u
                ))
        if not inicial: tabla.update()

    cargar(inicial=True)

    def click_eliminar(e):
        sel = next((r.data for r in tabla.rows if r.selected), None)
        if sel:
            abrir_popup_eliminar(page, f"{sel[1]} - {sel[2]}", sel[0], cargar)
        else:
            popup_libroP(page, "Aviso", "Selecciona un usuario primero.")

    def click_editar(e):
        sel = next((r.data for r in tabla.rows if r.selected), None)
        if sel:
            abrir_popup_editar_usuario(page,
                {"id": sel[0], "nombre": sel[1], "rol": sel[2],
                 "login": sel[3] if len(sel) > 3 else ""},
                funcion_actualizar=cargar)
        else:
            popup_libroP(page, "Aviso", "Selecciona un usuario primero.")

    back_route = "/biblio-inicio" if getattr(page, "route", "").startswith("/biblio") else "/admin-inicio"

    return ft.View(
        route="/admin-usuarios", bgcolor="#ffffff", padding=0,
        controls=[
            ft.Column(expand=True, controls=[
                crear_navbar(page),
                ft.Container(padding=ft.padding.only(left=50),
                    content=ft.Row([
                        ft.IconButton(icon=ft.Icons.ARROW_BACK,
                                      on_click=lambda _: page.go(back_route)),
                        ft.Text("Gestión de Usuarios", size=30, weight="bold", color="#712B33"),
                    ])),
                ft.Container(alignment=ft.Alignment(0, 0),
                    content=ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[
                        boton("Agregar usuario",  lambda _: abrir_popup_usuario(page, cargar), ancho=250),
                        boton("Editar usuario",   click_editar,  ancho=250),
                        boton("Eliminar usuario", click_eliminar, ancho=250),
                    ])),
                ft.Container(padding=ft.padding.only(left=50, right=50, bottom=20), expand=True,
                    content=ft.Column([
                        campo_busqueda,
                        ft.Column(expand=True, scroll="always", controls=[tabla])
                    ])),
            ]),
        ]
    )



def vista_gestion_Libros(page: ft.Page, modo: str = "admin"):
    tabla = ft.DataTable(
        width=float("inf"),
        show_checkbox_column=False,
        border=ft.border.all(1, "#712B33"),
        border_radius=10,
        heading_row_color="#F5F5F5",
        columns=[
            ft.DataColumn(ft.Text("Código",      weight="bold", color="#712B33")),
            ft.DataColumn(ft.Text("Título",      weight="bold", color="#712B33")),
            ft.DataColumn(ft.Text("Autor",       weight="bold", color="#712B33")),
            ft.DataColumn(ft.Text("Disponibles", weight="bold", color="#712B33")),
            ft.DataColumn(ft.Text("Estado/Desc", weight="bold", color="#712B33")),
        ],
        rows=[]
    )

    def filtrar(e):
        txt = e.control.value.lower()
        for fila in tabla.rows:
            fila.visible = txt in " ".join(
                str(c.content.value).lower() for c in fila.cells)
        tabla.update()

    campo_busqueda = ft.TextField(label="Buscar libro...",
                                  prefix_icon=ft.Icons.SEARCH, width=400, on_change=filtrar)

    def seleccionar_fila(e):
        sel = e.control.selected
        for f in tabla.rows:
            f.selected = False; f.color = None
            for c in f.cells:
                if isinstance(c.content, ft.Text): c.content.color = None
        if not sel:
            e.control.selected = True; e.control.color = "#2D2D2D"
            for c in e.control.cells:
                if isinstance(c.content, ft.Text): c.content.color = "white"
        try: tabla.update()
        except Exception: pass

    def cargar(inicial=False):
        tabla.rows.clear()
        res = buscar_libro("")
        if res["ok"]:
            for libro in res["data"]:
                disponibles = libro[7] if len(libro) > 7 else libro[4]
                disponibles = max(0, disponibles)
                
                descripcion = libro[8] if len(libro) > 8 else (libro[6] if len(libro) > 6 else "")
                tabla.rows.append(ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(libro[1]))),
                        ft.DataCell(ft.Text(str(libro[2]))),
                        ft.DataCell(ft.Text(str(libro[3]))),
                        ft.DataCell(ft.Text(str(disponibles))),
                        ft.DataCell(ft.Text(str(descripcion) if descripcion else "—",
                                            max_lines=1, overflow="ellipsis")),
                    ],
                    selected=False, on_select_change=seleccionar_fila, data=libro
                ))
        if not inicial:
            tabla.update()

    cargar(inicial=True)

    def click_eliminar(e):
        sel = next((r.data for r in tabla.rows if r.selected), None)
        if sel:
            abrir_popup_eliminar_libro(page, f"{sel[2]} - {sel[3]}", sel[0], cargar)
        else:
            popup_libroP(page, "Aviso", "Selecciona un libro primero.")

    def click_editar_desc(e):
        sel = next((r.data for r in tabla.rows if r.selected), None)
        if sel:
            abrir_popup_editar_descripcion(page, sel, funcion_actualizar=cargar)
        else:
            popup_libroP(page, "Aviso", "Selecciona un libro primero.")

    if modo == "admin":
        botones = [
            boton("Agregar libro",  lambda _: abrir_popup_libro(page, cargar), ancho=240),
            boton("Editar estado",  click_editar_desc, ancho=240),
            boton("Eliminar libro", click_eliminar, ancho=240),
        ]
        back_route = "/admin-inicio"
    else:
        botones = [
            boton("Editar estado del libro", click_editar_desc, ancho=300),
        ]
        back_route = "/biblio-inicio"

    return ft.View(
        route="/admin-libros", bgcolor="#ffffff", padding=0,
        controls=[
            ft.Column(expand=True, controls=[
                crear_navbar(page),
                ft.Container(padding=ft.padding.only(left=50),
                    content=ft.Row([
                        ft.IconButton(icon=ft.Icons.ARROW_BACK,
                                      on_click=lambda _: page.go(back_route)),
                        ft.Text("Gestión de Libros", size=30, weight="bold", color="#712B33"),
                    ])),
                ft.Container(alignment=ft.Alignment(0, 0),
                    content=ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=botones)),
                ft.Container(padding=ft.padding.only(left=50, right=50, bottom=20), expand=True,
                    content=ft.Column([
                        campo_busqueda,
                        ft.Column(expand=True, scroll="always", controls=[tabla])
                    ])),
            ]),
        ]
    )


def vista_gestion_Prestamos(page: ft.Page):
    tabla = ft.DataTable(
        width=float("inf"),
        show_checkbox_column=False,
        border=ft.border.all(1, "#712B33"),
        border_radius=10,
        heading_row_color="#F5F5F5",
        columns=[], rows=[]
    )

    def seleccionar_fila(e):
        sel = e.control.selected
        for f in tabla.rows:
            f.selected = False
            f.color = f.data.get("color_original")
            for c in f.cells:
                if isinstance(c.content, ft.Text): c.content.color = None
        if not sel:
            e.control.selected = True; e.control.color = "#2D2D2D"
            for c in e.control.cells:
                if isinstance(c.content, ft.Text): c.content.color = "white"
        try: tabla.update()
        except Exception: pass

    def filtrar(e):
        txt = e.control.value.lower()
        for fila in tabla.rows:
            fila.visible = txt in " ".join(
                str(c.content.value).lower() for c in fila.cells)
        tabla.update()

    campo_busqueda = ft.TextField(label="Buscar préstamo...",
                                  prefix_icon=ft.Icons.SEARCH, width=400, on_change=filtrar)

    def cargar_prestamos(inicial=False):
        from datetime import datetime, date
        from config import actualizar_penalizaciones_automaticas
        
        campo_busqueda.value = ""
        tabla.columns = [
            ft.DataColumn(ft.Text("Alumno",      weight="bold", color="#712B33")),
            ft.DataColumn(ft.Text("Título",      weight="bold", color="#712B33")),
            ft.DataColumn(ft.Text("Fecha salida",weight="bold", color="#712B33")),
            ft.DataColumn(ft.Text("Fecha límite",weight="bold", color="#712B33")),
            ft.DataColumn(ft.Text("Estado",      weight="bold", color="#712B33")),
        ]
        tabla.rows.clear()
        
        sync_result = actualizar_penalizaciones_automaticas()
        
        res = obtener_prestamos()
        if res["ok"]:
            hoy = date.today()
            for p in res["data"]:
                estado_txt  = "Activo" if p[4] == 1 else "Devuelto"
                fecha_lim   = str(p[6]) if len(p) > 6 and p[6] else "—"

                color = None
                if p[4] == 1:
                    tiene_penalizacion = False
                    
                    if len(p) > 6 and p[6]:
                        try:
                            if isinstance(p[6], str):
                                fecha_dev = datetime.strptime(p[6], "%Y-%m-%d").date()
                            else:
                                fecha_dev = p[6]
                            
                            if fecha_dev < hoy:
                                tiene_penalizacion = True
                        except Exception as ex:
                            pen_act = p[5] if len(p) > 5 else 0
                            tiene_penalizacion = bool(pen_act)
                    else:
                        pen_act = p[5] if len(p) > 5 else 0
                        tiene_penalizacion = bool(pen_act)
                    
                    color = "#B53548" if tiene_penalizacion else "#47C452"

                tabla.rows.append(ft.DataRow(
                    color=color,
                    cells=[
                        ft.DataCell(ft.Text(str(p[1]))),
                        ft.DataCell(ft.Text(str(p[2]))),
                        ft.DataCell(ft.Text(str(p[3]))),
                        ft.DataCell(ft.Text(fecha_lim)),
                        ft.DataCell(ft.Text(estado_txt)),
                    ],
                    selected=False, on_select_change=seleccionar_fila,
                    data={"prestamo": p, "color_original": color}
                ))
        if not inicial:
            campo_busqueda.update(); tabla.update()

    def ver_penalizaciones(e):
        campo_busqueda.value = ""
        tabla.columns = [
            ft.DataColumn(ft.Text("Alumno",       weight="bold", color="#712B33")),
            ft.DataColumn(ft.Text("Título",       weight="bold", color="#712B33")),
            ft.DataColumn(ft.Text("Fecha salida", weight="bold", color="#712B33")),
            ft.DataColumn(ft.Text("Fecha límite", weight="bold", color="#712B33")),
            ft.DataColumn(ft.Text("Motivo",       weight="bold", color="#712B33")),
        ]
        tabla.rows.clear()

        from services.alumnos import obtener_prestamos_con_penalizacion
        res = obtener_prestamos_con_penalizacion()
        if res["ok"]:
            for p in res["data"]:
                color = "#B53548" if p[7] == 1 else None
                tabla.rows.append(ft.DataRow(
                    color=color,
                    cells=[
                        ft.DataCell(ft.Text(str(p[2]))),
                        ft.DataCell(ft.Text(str(p[3]))),
                        ft.DataCell(ft.Text(str(p[4]))),
                        ft.DataCell(ft.Text(str(p[5]) if p[5] else "—")),
                        ft.DataCell(ft.Text(str(p[6]) if p[6] else "Retraso de entrega")),
                    ],
                    selected=False, on_select_change=seleccionar_fila,
                    data={"prestamo": p, "color_original": color,
                          "id_alumno": p[1], "nombre_alumno": p[2], "modo": "pen"}
                ))
        campo_busqueda.update(); tabla.update()

    def click_devolver(e):
        sel = next((r.data for r in tabla.rows if r.selected), None)
        if not sel:
            popup_libroP(page, "Aviso", "Selecciona un préstamo activo."); return
        p = sel["prestamo"]
        id_p = p[0]; alumno = p[1]; titulo = p[2]; estado = p[4]

        if estado == 0:
            popup_libroP(page, "Aviso", "Este préstamo ya fue devuelto."); return

        def confirmar(e):
            res = devolver_libro(id_p)
            dlg.open = False; page.update()
            if res["ok"]:
                cargar_prestamos()
            else:
                popup_libroP(page, "Error", res.get("msg", "No se pudo registrar."))

        dlg = ft.AlertDialog(
            modal=True, shape=ft.RoundedRectangleBorder(radius=10),
            bgcolor="#ffffff",
            content=ft.Text(f"¿Devolver '{titulo}' de {alumno}?", size=16),
            actions=[
                ft.ElevatedButton("Cancelar", bgcolor="grey", color="white",
                                  on_click=lambda _: (setattr(dlg, "open", False), page.update())),
                ft.ElevatedButton("Sí, devolver", bgcolor="#712B33", color="white",
                                  on_click=confirmar),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        page.overlay.append(dlg); dlg.open = True; page.update()

    def click_quitar_penalizacion(e):
        sel = next((r.data for r in tabla.rows if r.selected), None)
        if not sel:
            popup_libroP(page, "Aviso", "Selecciona una fila con penalización."); return

        if sel.get("modo") == "pen":
            id_alumno    = sel["id_alumno"]
            nombre_alumno = sel["nombre_alumno"]
        else:
            p = sel["prestamo"]
            id_alumno     = None
            nombre_alumno = p[1]
            from services.alumnos import obtener_id_alumno_por_nombre
            r = obtener_id_alumno_por_nombre(nombre_alumno)
            if r.get("ok"):
                id_alumno = r["data"]
            else:
                popup_libroP(page, "Error", "No se encontró el alumno."); return

        abrir_popup_quitar_penalizacion(page, id_alumno, nombre_alumno,
                                        funcion_actualizar=lambda: cargar_prestamos())

    cargar_prestamos(inicial=True)

    back_route = "/biblio-inicio" if getattr(page, "route", "").startswith("/biblio") else "/admin-inicio"

    return ft.View(
        route="/admin-prestamos", bgcolor="#ffffff", padding=0,
        controls=[
            crear_navbar(page),
            ft.Container(padding=ft.padding.only(left=50),
                content=ft.Row([
                    ft.IconButton(icon=ft.Icons.ARROW_BACK,
                                  on_click=lambda _: page.go(back_route)),
                    ft.Text("Gestión de Préstamos", size=30, weight="bold", color="#712B33"),
                ])),
            ft.Container(alignment=ft.Alignment(0, 0), padding=20,
                content=ft.Row(alignment="center", spacing=15, controls=[
                    boton("Agregar Préstamo",
                          lambda _: abrir_popup_agregar_prestamo(page, cargar_prestamos),
                          ancho=200),
                    boton("Devolver libro",  click_devolver,  ancho=200),
                    boton("Ver Préstamos",   lambda _: cargar_prestamos(), ancho=200),
                    boton("Penalizaciones",  ver_penalizaciones, ancho=200),
                    boton("Quitar Penalización", click_quitar_penalizacion,
                          color_fondo="#B53548", ancho=200),
                ])),
            ft.Container(padding=ft.padding.only(left=50, right=50, bottom=20), expand=True,
                content=ft.Column([
                    campo_busqueda,
                    ft.Column(expand=True, scroll="always", controls=[tabla])
                ])),
        ]
    )
# services/usuarios.py
import bcrypt
from config import get_db


def login(userlogin, password):
    try:
        db  = get_db()
        cur = db.cursor()
        cur.execute("""
            SELECT u.Id_Usuario, u.Nombre_Us, u.Rol, u.Contrasena
            FROM Usuarios u
            WHERE u.Userlogin = %s
        """, (userlogin,))
        row = cur.fetchone()
        cur.close(); db.close()

        if not row:
            return {"ok": False, "msg": "Usuario no encontrado."}

        id_u, nombre, rol, hash_pass = row

        if not bcrypt.checkpw(password.encode(), hash_pass.encode()):
            return {"ok": False, "msg": "Contraseña incorrecta."}

        redirect_map = {
            "Administrador": "admin-inicio",
            "Bibliotecario": "biblio-inicio",
            "Alumno":        "home",
        }
        return {
            "ok": True,
            "data": {
                "id":       id_u,
                "nombre":   nombre,
                "rol":      rol,
                "redirect": redirect_map.get(rol, "home"),
            }
        }
    except Exception as ex:
        return {"ok": False, "msg": str(ex)}


def obtener_usuarios():
    try:
        db  = get_db()
        cur = db.cursor()
        cur.execute("""
            SELECT Id_Usuario, Nombre_Us, Rol, Userlogin
            FROM Usuarios
            ORDER BY Nombre_Us
        """)
        rows = cur.fetchall()
        cur.close(); db.close()
        return {"ok": True, "data": rows}
    except Exception as ex:
        return {"ok": False, "msg": str(ex), "data": []}


def crear_usuario(nombre, rol, login, password):
    try:
        db  = get_db()
        cur = db.cursor()
        h   = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        cur.execute("""
            INSERT INTO Usuarios (Nombre_Us, Rol, Contrasena, Userlogin)
            VALUES (%s, %s, %s, %s)
        """, (nombre, rol, h, login))
        id_nuevo = cur.lastrowid

        # Si es alumno, crear registro en Alumnos
        # Identificacion se pone como el id por defecto (puede cambiarse)
        if rol == "Alumno":
            cur.execute("""
                INSERT INTO Alumnos (Id_Alumno, Identificacion, Pen_Act)
                VALUES (%s, %s, 0)
            """, (id_nuevo, id_nuevo))

        db.commit()
        cur.close(); db.close()
        return {"ok": True, "msg": "Usuario creado."}
    except Exception as ex:
        return {"ok": False, "msg": str(ex)}


def actualizar_usuario(id_user, nombre, rol, login):
    try:
        db  = get_db()
        cur = db.cursor()
        cur.execute("""
            UPDATE Usuarios
               SET Nombre_Us = %s,
                   Rol       = %s,
                   Userlogin = %s
             WHERE Id_Usuario = %s
        """, (nombre, rol, login, id_user))
        db.commit()
        cur.close(); db.close()
        return {"ok": True, "msg": "Usuario actualizado."}
    except Exception as ex:
        return {"ok": False, "msg": str(ex)}


def eliminar_usuario(id_user):
    try:
        db  = get_db()
        cur = db.cursor()
        # ON DELETE CASCADE borra también el registro en Alumnos y sus préstamos
        cur.execute("DELETE FROM Usuarios WHERE Id_Usuario = %s", (id_user,))
        db.commit()
        cur.close(); db.close()
        return {"ok": True, "msg": "Usuario eliminado."}
    except Exception as ex:
        return {"ok": False, "msg": str(ex)}


def buscar_alumno_por_nombre(nombre):
    """Busca un usuario con rol Alumno por su nombre exacto."""
    try:
        db  = get_db()
        cur = db.cursor()
        cur.execute("""
            SELECT u.Id_Usuario, u.Nombre_Us, u.Rol, u.Userlogin
            FROM Usuarios u
            JOIN Alumnos a ON a.Id_Alumno = u.Id_Usuario
            WHERE u.Nombre_Us = %s AND u.Rol = 'Alumno'
            LIMIT 1
        """, (nombre,))
        row = cur.fetchone()
        cur.close(); db.close()
        if row:
            return {"ok": True, "data": {
                "id":     row[0],
                "nombre": row[1],
                "rol":    row[2],
                "login":  row[3],
            }}
        return {"ok": False, "msg": f"Alumno '{nombre}' no encontrado."}
    except Exception as ex:
        return {"ok": False, "msg": str(ex)}
# services/prestamos.py
from config import get_db


def contar_prestamos_activos():
    """Devuelve el total de préstamos con estado=1 (activos)."""
    try:
        db  = get_db()
        cur = db.cursor()
        cur.execute("SELECT COUNT(*) FROM Prestamos WHERE estado = 1")
        total = cur.fetchone()[0]
        cur.close(); db.close()
        return total
    except Exception:
        return 0


def obtener_prestamos_activos():
    """Lista de préstamos activos con nombre del alumno y título del libro."""
    try:
        db  = get_db()
        cur = db.cursor()
        cur.execute("""
            SELECT p.Id_Prestamo,
                   u.Nombre_Us,
                   l.Titulo,
                   p.fecha_salida
            FROM Prestamos p
            JOIN Alumnos  a ON p.id_alum = a.Id_Alumno
            JOIN Usuarios u ON a.Id_Alumno = u.Id_Usuario
            JOIN Libros   l ON p.id_libro  = l.id_Libro
            WHERE p.estado = 1
            ORDER BY p.fecha_salida DESC
        """)
        rows = cur.fetchall()
        cur.close(); db.close()
        return {"ok": True, "data": rows}
    except Exception as ex:
        return {"ok": False, "msg": str(ex), "data": []}


def obtener_prestamos():
    """
    Todos los préstamos (activos y devueltos).
    Devuelve tuplas:
    (id_prestamo, nombre_alumno, titulo, fecha_salida, estado, pen_act, fecha_devolucion)
    """
    try:
        db  = get_db()
        cur = db.cursor()
        cur.execute("""
            SELECT p.Id_Prestamo,
                   u.Nombre_Us,
                   l.Titulo,
                   p.fecha_salida,
                   p.estado,
                   COALESCE(a.Pen_Act, 0),
                   p.fecha_devolucion
            FROM Prestamos p
            JOIN Alumnos  a ON p.id_alum  = a.Id_Alumno
            JOIN Usuarios u ON a.Id_Alumno = u.Id_Usuario
            JOIN Libros   l ON p.id_libro  = l.id_Libro
            ORDER BY p.fecha_salida DESC
        """)
        rows = cur.fetchall()
        cur.close(); db.close()
        return {"ok": True, "data": rows}
    except Exception as ex:
        return {"ok": False, "msg": str(ex), "data": []}


def obtener_prestamos_usuario(id_usuario):
    """
    Préstamos activos de un alumno específico para mostrar en su perfil.
    Devuelve tuplas:
    (id_prestamo, id_alumno, nombre_alumno, titulo, autor, genero, activo, fecha_salida, fecha_devolucion)
    """
    try:
        db  = get_db()
        cur = db.cursor()
        cur.execute("""
            SELECT p.Id_Prestamo,
                   a.Id_Alumno,
                   u.Nombre_Us,
                   l.Titulo,
                   l.Autor,
                   l.Genero,
                   l.Activo,
                   p.fecha_salida,
                   p.fecha_devolucion
            FROM Prestamos p
            JOIN Alumnos  a ON p.id_alum  = a.Id_Alumno
            JOIN Usuarios u ON a.Id_Alumno = u.Id_Usuario
            JOIN Libros   l ON p.id_libro  = l.id_Libro
            WHERE a.Id_Alumno = %s
              AND p.estado    = 1
            ORDER BY p.fecha_salida DESC
        """, (id_usuario,))
        rows = cur.fetchall()
        cur.close(); db.close()
        return {"ok": True, "data": rows}
    except Exception as ex:
        return {"ok": False, "msg": str(ex), "data": []}


def devolver_libro(id_prestamo):
    """
    Marca el préstamo como devuelto (estado=0) y hace restock del libro
    sumando 1 a Cantidad.
    """
    try:
        db  = get_db()
        cur = db.cursor()

        # Obtener id_libro del préstamo
        cur.execute("SELECT id_libro FROM Prestamos WHERE Id_Prestamo = %s", (id_prestamo,))
        row = cur.fetchone()
        if not row:
            cur.close(); db.close()
            return {"ok": False, "msg": "Préstamo no encontrado."}

        id_libro = row[0]

        # Marcar como devuelto y registrar fecha de entrada
        cur.execute("""
            UPDATE Prestamos
               SET estado       = 0,
                   fecha_entrada = CURDATE()
             WHERE Id_Prestamo = %s
        """, (id_prestamo,))

        # Restock: incrementar Cantidad del libro
        cur.execute("""
            UPDATE Libros
               SET Cantidad = Cantidad + 1
             WHERE id_Libro = %s
        """, (id_libro,))

        db.commit()
        cur.close(); db.close()
        return {"ok": True, "msg": "Libro devuelto y stock actualizado."}
    except Exception as ex:
        return {"ok": False, "msg": str(ex)}


def crear_prestamo_con_fecha(id_alumno, id_libro, fecha_devolucion):
    """
    Crea un préstamo para un alumno, descuenta 1 de Cantidad del libro.
    fecha_devolucion: objeto date de Python.
    """
    try:
        db  = get_db()
        cur = db.cursor()

        # Verificar disponibilidad (Cantidad > 0 y libro Activo)
        cur.execute("""
            SELECT Cantidad FROM Libros
            WHERE id_Libro = %s AND Activo = 1
        """, (id_libro,))
        libro = cur.fetchone()
        if not libro:
            cur.close(); db.close()
            return {"ok": False, "msg": "Libro no encontrado o inactivo."}
        if libro[0] <= 0:
            cur.close(); db.close()
            return {"ok": False, "msg": "No hay copias disponibles."}

        # Verificar que el alumno no tenga ya ese libro prestado
        cur.execute("""
            SELECT COUNT(*) FROM Prestamos
            WHERE id_alum = %s AND id_libro = %s AND estado = 1
        """, (id_alumno, id_libro))
        if cur.fetchone()[0] > 0:
            cur.close(); db.close()
            return {"ok": False, "msg": "El alumno ya tiene este libro prestado."}

        # Insertar préstamo
        cur.execute("""
            INSERT INTO Prestamos
                (id_alum, id_libro, fecha_salida, estado, fecha_devolucion)
            VALUES (%s, %s, CURDATE(), 1, %s)
        """, (id_alumno, id_libro, fecha_devolucion))

        # Descontar disponibilidad
        cur.execute("""
            UPDATE Libros SET Cantidad = Cantidad - 1
            WHERE id_Libro = %s
        """, (id_libro,))

        db.commit()
        cur.close(); db.close()
        return {"ok": True, "msg": "Préstamo registrado correctamente."}
    except Exception as ex:
        return {"ok": False, "msg": str(ex)}
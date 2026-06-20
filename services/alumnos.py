# services/alumnos.py
# Maneja todo lo relacionado con penalizaciones en la tabla Alumnos
from config import get_db


def contar_penalizaciones_activas():
    """Devuelve cuántos alumnos tienen Pen_Act = 1."""
    try:
        db  = get_db()
        cur = db.cursor()
        cur.execute("SELECT COUNT(*) FROM Alumnos WHERE Pen_Act = 1")
        total = cur.fetchone()[0]
        cur.close(); db.close()
        return total
    except Exception:
        return 0


def obtener_nombres_penalizados():
    """Lista de nombres de alumnos con penalización activa."""
    try:
        db  = get_db()
        cur = db.cursor()
        cur.execute("""
            SELECT u.Nombre_Us
            FROM Alumnos a
            JOIN Usuarios u ON a.Id_Alumno = u.Id_Usuario
            WHERE a.Pen_Act = 1
            ORDER BY u.Nombre_Us
        """)
        rows = cur.fetchall()
        cur.close(); db.close()
        return [r[0] for r in rows]
    except Exception:
        return []


def obtener_prestamos_con_penalizacion():
    """
    Devuelve préstamos de alumnos con Pen_Act=1.
    Tupla: (id_prestamo, id_alumno, nombre_alumno, titulo,
            fecha_salida, fecha_devolucion, penalizaciones_texto, estado)
    """
    try:
        db  = get_db()
        cur = db.cursor()
        cur.execute("""
            SELECT p.Id_Prestamo,
                   a.Id_Alumno,
                   u.Nombre_Us,
                   l.Titulo,
                   p.fecha_salida,
                   p.fecha_devolucion,
                   a.Penalizaciones,
                   p.estado
            FROM Prestamos p
            JOIN Alumnos  a ON p.id_alum   = a.Id_Alumno
            JOIN Usuarios u ON a.Id_Alumno = u.Id_Usuario
            JOIN Libros   l ON p.id_libro  = l.id_Libro
            WHERE a.Pen_Act = 1
            ORDER BY p.fecha_salida DESC
        """)
        rows = cur.fetchall()
        cur.close(); db.close()
        return {"ok": True, "data": rows}
    except Exception as ex:
        return {"ok": False, "msg": str(ex), "data": []}


def quitar_penalizacion_alumno(id_alumno):
    """Limpia Pen_Act y Penalizaciones del alumno."""
    try:
        db  = get_db()
        cur = db.cursor()
        cur.execute("""
            UPDATE Alumnos
               SET Pen_Act       = 0,
                   Penalizaciones = NULL
             WHERE Id_Alumno = %s
        """, (id_alumno,))
        db.commit()
        cur.close(); db.close()
        return {"ok": True, "msg": "Penalización eliminada."}
    except Exception as ex:
        return {"ok": False, "msg": str(ex)}


def obtener_id_alumno_por_nombre(nombre):
    """Devuelve el Id_Alumno dado el nombre del usuario."""
    try:
        db  = get_db()
        cur = db.cursor()
        cur.execute("""
            SELECT a.Id_Alumno
            FROM Alumnos  a
            JOIN Usuarios u ON a.Id_Alumno = u.Id_Usuario
            WHERE u.Nombre_Us = %s
            LIMIT 1
        """, (nombre,))
        row = cur.fetchone()
        cur.close(); db.close()
        if row:
            return {"ok": True, "data": row[0]}
        return {"ok": False, "msg": f"Alumno '{nombre}' no encontrado."}
    except Exception as ex:
        return {"ok": False, "msg": str(ex)}
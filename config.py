import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )


def actualizar_penalizaciones_automaticas(dias_limite=14):
    """
    Activa penalizaciones automáticas por DOS criterios:
    1. Préstamos activos que tienen fecha_devolucion definida y ya venció (< hoy).
    2. Préstamos activos sin fecha_devolucion pero que llevan más de `dias_limite` días.
    En ambos casos actualiza Alumnos: Pen_Act=1 y agrega el motivo a Penalizaciones.
    """
    db  = None
    cur = None
    try:
        db  = get_db()
        cur = db.cursor()

        # ── Criterio 1: fecha_devolucion vencida ──────────────────────────────
        cur.execute("""
            SELECT p.Id_Prestamo,
                   p.id_alum,
                   l.Titulo,
                   p.fecha_devolucion,
                   a.Penalizaciones
            FROM Prestamos p
            JOIN Alumnos a ON p.id_alum  = a.Id_Alumno
            JOIN Libros  l ON p.id_libro = l.id_Libro
            WHERE p.estado           = 1
              AND p.fecha_devolucion IS NOT NULL
              AND p.fecha_devolucion  < CURDATE()
        """)
        vencidos_por_fecha = cur.fetchall()

        actualizados = 0

        for (id_prestamo, id_alum, titulo, fecha_dev, historial) in vencidos_por_fecha:
            historial   = historial or ""
            msg_pen     = f"- Retraso: '{titulo}' debía devolverse el {fecha_dev}."
            if msg_pen not in historial:
                nuevo = (historial + "\n" + msg_pen).strip()
                cur.execute("""
                    UPDATE Alumnos
                       SET Pen_Act       = 1,
                           Penalizaciones = %s
                     WHERE Id_Alumno = %s
                """, (nuevo, id_alum))
                actualizados += cur.rowcount

        # ── Criterio 2: sin fecha_devolucion pero más de dias_limite días ─────
        cur.execute("""
            SELECT p.Id_Prestamo,
                   p.id_alum,
                   p.id_libro,
                   p.fecha_salida,
                   a.Penalizaciones
            FROM Prestamos p
            JOIN Alumnos a ON p.id_alum = a.Id_Alumno
            WHERE p.estado            = 1
              AND p.fecha_devolucion  IS NULL
              AND DATEDIFF(CURDATE(), p.fecha_salida) > %s
        """, (dias_limite,))
        vencidos_por_dias = cur.fetchall()

        for (id_prestamo, id_alum, id_libro, fecha_salida, historial) in vencidos_por_dias:
            historial = historial or ""
            msg_pen   = f"- Retraso automático: Libro ID {id_libro} vencido."
            if msg_pen not in historial:
                nuevo = (historial + "\n" + msg_pen).strip()
                cur.execute("""
                    UPDATE Alumnos
                       SET Pen_Act       = 1,
                           Penalizaciones = %s
                     WHERE Id_Alumno = %s
                """, (nuevo, id_alum))
                actualizados += cur.rowcount

        db.commit()
        return {"ok": True, "msg": f"Se activaron {actualizados} nueva(s) penalización(es) automática(s)."}

    except Exception as e:
        if db:
            db.rollback()
        return {"ok": False, "msg": str(e)}

    finally:
        if cur: cur.close()
        if db:  db.close()
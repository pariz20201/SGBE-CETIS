# services/libros.py
from config import get_db


def obtener_libros():
    """
    Lista todos los libros activos con disponibles calculados.
    Devuelve tuplas: (id, codigo, titulo, autor, disponibles, genero, activo, disponibles, descripcion)
    donde disponibles = Cantidad - préstamos activos del libro.
    """
    try:
        db  = get_db()
        cur = db.cursor()
        cur.execute("""
            SELECT l.id_Libro,
                   l.Codigo,
                   l.Titulo,
                   l.Autor,
                   (l.Cantidad - COALESCE(prestados.total, 0)) AS disponibles,
                   l.Genero,
                   l.Activo,
                   (l.Cantidad - COALESCE(prestados.total, 0)) AS disponibles2,
                   l.Descripcion
            FROM Libros l
            LEFT JOIN (
                SELECT id_libro, COUNT(*) AS total
                FROM Prestamos
                WHERE estado = 1
                GROUP BY id_libro
            ) prestados ON l.id_Libro = prestados.id_libro
            WHERE l.Activo = 1
            ORDER BY l.Titulo
        """)
        rows = cur.fetchall()
        cur.close(); db.close()
        return {"ok": True, "data": rows}
    except Exception as ex:
        return {"ok": False, "msg": str(ex), "data": []}


def obtener_libro_por_id(id_libro):
    """Devuelve un libro por su id."""
    try:
        db  = get_db()
        cur = db.cursor()
        cur.execute("""
            SELECT l.id_Libro,
                   l.Codigo,
                   l.Titulo,
                   l.Autor,
                   (l.Cantidad - COALESCE(prestados.total, 0)) AS disponibles,
                   l.Genero,
                   l.Activo,
                   (l.Cantidad - COALESCE(prestados.total, 0)) AS disponibles2,
                   l.Descripcion
            FROM Libros l
            LEFT JOIN (
                SELECT id_libro, COUNT(*) AS total
                FROM Prestamos WHERE estado = 1
                GROUP BY id_libro
            ) prestados ON l.id_Libro = prestados.id_libro
            WHERE l.id_Libro = %s
        """, (id_libro,))
        row = cur.fetchone()
        cur.close(); db.close()
        if row:
            return {"ok": True, "data": row}
        return {"ok": False, "msg": "Libro no encontrado."}
    except Exception as ex:
        return {"ok": False, "msg": str(ex)}


def obtener_libro_por_codigo(codigo):
    """Devuelve un libro por su código ISBN."""
    try:
        db  = get_db()
        cur = db.cursor()
        cur.execute("""
            SELECT l.id_Libro,
                   l.Codigo,
                   l.Titulo,
                   l.Autor,
                   (l.Cantidad - COALESCE(prestados.total, 0)) AS disponibles,
                   l.Genero,
                   l.Activo,
                   (l.Cantidad - COALESCE(prestados.total, 0)) AS disponibles2,
                   l.Descripcion
            FROM Libros l
            LEFT JOIN (
                SELECT id_libro, COUNT(*) AS total
                FROM Prestamos WHERE estado = 1
                GROUP BY id_libro
            ) prestados ON l.id_Libro = prestados.id_libro
            WHERE l.Codigo = %s AND l.Activo = 1
        """, (codigo,))
        row = cur.fetchone()
        cur.close(); db.close()
        if row:
            return {"ok": True, "data": row}
        return {"ok": False, "msg": f"No se encontró libro con código '{codigo}'."}
    except Exception as ex:
        return {"ok": False, "msg": str(ex)}


def buscar_libro(texto):
    """Busca libros por título o autor (para la tabla de gestión)."""
    try:
        db  = get_db()
        cur = db.cursor()
        like = f"%{texto}%"

        cur.execute("""
            SELECT l.id_Libro,
                   l.Codigo,
                   l.Titulo,
                   l.Autor,
                   l.Cantidad,
                   l.Genero,
                   l.Activo,

                   GREATEST(
                       l.Cantidad - COALESCE(prestados.total, 0),
                       0
                   ) AS disponibles,

                   l.Descripcion

            FROM Libros l

            LEFT JOIN (
                SELECT id_libro, COUNT(*) AS total
                FROM Prestamos
                WHERE estado = 1
                GROUP BY id_libro
            ) prestados
            ON l.id_Libro = prestados.id_libro

            WHERE (l.Titulo LIKE %s OR l.Autor LIKE %s)
            AND l.Activo = 1

            ORDER BY l.Titulo
        """, (like, like))

        rows = cur.fetchall()

        cur.close()
        db.close()

        return {"ok": True, "data": rows}

    except Exception as ex:
        return {"ok": False, "msg": str(ex), "data": []}


def crear_libro(codigo, titulo, autor, cantidad, genero, descripcion=""):
    try:
        db  = get_db()
        cur = db.cursor()
        cur.execute("""
            INSERT INTO Libros (Codigo, Titulo, Autor, Cantidad, Genero, Descripcion, Activo)
            VALUES (%s, %s, %s, %s, %s, %s, 1)
        """, (codigo, titulo, autor, cantidad, genero, descripcion))
        db.commit()
        cur.close(); db.close()
        return {"ok": True, "msg": "Libro creado."}
    except Exception as ex:
        return {"ok": False, "msg": str(ex)}


def eliminar_libro(id_libro):
    """Desactiva el libro (borrado lógico)."""
    try:
        db  = get_db()
        cur = db.cursor()
        cur.execute("UPDATE Libros SET Activo = 0 WHERE id_Libro = %s", (id_libro,))
        db.commit()
        cur.close(); db.close()
        return {"ok": True, "msg": "Libro eliminado."}
    except Exception as ex:
        return {"ok": False, "msg": str(ex)}


def actualizar_descripcion_libro(id_libro, descripcion):
    """Actualiza solo la descripción/estado físico del libro."""
    try:
        db  = get_db()
        cur = db.cursor()
        cur.execute("UPDATE Libros SET Descripcion = %s WHERE id_Libro = %s",
                    (descripcion, id_libro))
        db.commit()
        cur.close(); db.close()
        return {"ok": True, "msg": "Descripción actualizada."}
    except Exception as ex:
        return {"ok": False, "msg": str(ex)}
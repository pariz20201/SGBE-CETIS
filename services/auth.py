import bcrypt
from config import get_db

def login(userlogin, password):
    db = None
    cur = None
    try:
        db = get_db()
        cur = db.cursor()

        cur.execute(
            "SELECT Id_Usuario, Nombre_Us, Rol, Contrasena FROM Usuarios WHERE Userlogin=%s",
            (userlogin,)
        )
        user = cur.fetchone()

        if not user:
            return {"ok": False, "msg": "Usuario no encontrado"}

        id_user, nombre, rol, hash_db = user

        # valida contraseña
        if bcrypt.checkpw(password.encode('utf-8'), hash_db.encode('utf-8')):
            return {
                "ok": True,
                "msg": "Login correcto",
                "data": {
                    "id": id_user,
                    "nombre": nombre,
                    "rol": rol
                }
            }

        return {"ok": False, "msg": "Contraseña incorrecta"}

    except Exception as e:
        return {"ok": False, "msg": f"Error en login: {str(e)}"}

    finally:
        if cur:
            cur.close()
        if db:
            db.close()

def probar_acceso():
    print("--- Intentando Login ---")
    
    # 1. Prueba con datos correctos
    resultado = login("ana.biblio", "mi_password_seguro")
    print(f"Resultado esperado (Éxito): {resultado}")

    # 2. Prueba con contraseña mal
    resultado_error = login("ana.biblio", "password_equivocado")
    print(f"Resultado esperado (Error clave): {resultado_error}")

    # 3. Prueba con usuario inexistente
    resultado_null = login("usuario_fantasma", "1234")
    print(f"Resultado esperado (No existe): {resultado_null}")

if __name__ == "__main__":
    probar_acceso()
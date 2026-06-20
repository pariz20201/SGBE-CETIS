import os
import sysconfig
import subprocess


rutas_posibles = [
    os.path.join(sysconfig.get_path("scripts"), "flet.exe"),
    os.path.join(sysconfig.get_path("scripts", f"{os.name}_user"), "flet.exe")
]

flet_exe = next((ruta for ruta in rutas_posibles if os.path.exists(ruta)), None)

if flet_exe:
    print(f"✅ Empaquetador encontrado en: {flet_exe}")
    print("🔨 Construyendo ejecutable, por favor espera... (Esto puede tomar unos minutos)")
    
    comando = [flet_exe, "pack", "sgbe.py", "--add-data", "assets;assets"]
    subprocess.run(comando)
    
    print("🎉 ¡Proceso terminado! Revisa tu nueva carpeta 'dist'")
else:
    print("❌ No se encontró el motor de Flet. Intenta correr 'pip install flet' nuevamente.")
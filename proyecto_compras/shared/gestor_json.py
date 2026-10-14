import json
import os

class GestorJSON:
    """Lee y guarda una lista de diccionarios en un archivo JSON."""
    def __init__(self, ruta):
        self.__ruta = ruta
        carpeta = os.path.dirname(ruta)
        if carpeta:
            os.makedirs(carpeta, exist_ok=True)
        if not os.path.exists(self.__ruta):
            self.guardar([])

    def leer(self):
        try:
            with open(self.__ruta, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
            return datos if isinstance(datos, list) else []
        except (json.JSONDecodeError, OSError):
            return []

    def guardar(self, datos):
        temporal = self.__ruta + ".tmp"
        with open(temporal, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, ensure_ascii=False, indent=2)
        os.replace(temporal, self.__ruta)

    def añadir(self, registro):
        datos = self.leer()
        datos.append(registro)
        self.guardar(datos)

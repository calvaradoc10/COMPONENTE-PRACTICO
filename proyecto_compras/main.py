from models import Proveedor, Producto
from views import ClienteController, ProductoController, VentaController, ProveedorController, CompraController
from shared import imprimir_titulo, imprimir_exito, imprimir_error, imprimir_info, confirmar

class Menu:
    def __init__(self):
        self.clientes = ClienteController()
        self.productos = ProductoController()
        self.ventas = VentaController(self.clientes, self.productos)
        self.proveedores = ProveedorController()
        self.compras = CompraController(self.proveedores, self.productos)

    @staticmethod
    def pausa():
        input("\nPresione Enter para continuar...")

    @staticmethod
    def pedir_entero(texto):
        try: return int(input(texto).strip())
        except (ValueError, TypeError): return None

    @staticmethod
    def mostrar_resultado(exito, mensaje):
        (imprimir_exito if exito else imprimir_error)(mensaje)

    def ejecutar(self):
        while True:
            imprimir_titulo("SISTEMA DE VENTAS Y COMPRAS")
            print("  1. Clientes\n  2. Productos\n  3. Ventas\n  4. Proveedores\n  5. Compras\n  0. Salir\n")
            opcion = input("Opción: ").strip()
            if opcion == "1": self.menu_crud(self.clientes)
            elif opcion == "2": self.menu_crud(self.productos)
            elif opcion == "3": self.menu_crud(self.ventas)
            elif opcion == "4": self.menu_crud(self.proveedores)
            elif opcion == "5": self.menu_crud(self.compras)
            elif opcion == "0": imprimir_info("¡Hasta luego!"); break
            else: imprimir_error("Opción no válida"); self.pausa()

    def menu_crud(self, controlador):
        while True:
            imprimir_titulo(controlador.nombre.upper() + "S")
            print(f"  1. Crear {controlador.nombre}\n  2. Ver todos\n  3. Buscar\n  4. Ver por id\n  5. Actualizar\n  6. Eliminar")
            if controlador == self.ventas: print("  7. Ver factura")
            if controlador == self.compras: print("  7. Ver orden de compra")
            print("  0. Volver\n")
            opcion = input("Opción: ").strip()
            if opcion == "1":
                if controlador == self.ventas: self.crear_venta()
                elif controlador == self.compras: self.crear_compra()
                else: self.crear(controlador)
            elif opcion == "2": self.ver_todos(controlador)
            elif opcion == "3": self.buscar(controlador)
            elif opcion == "4": self.ver_por_id(controlador)
            elif opcion == "5": self.actualizar(controlador)
            elif opcion == "6": self.eliminar(controlador)
            elif opcion == "7" and controlador == self.ventas: self.ver_factura()
            elif opcion == "7" and controlador == self.compras: self.ver_orden_compra()
            elif opcion == "0": break
            else: imprimir_error("Opción no válida"); self.pausa()

    def crear(self, controlador):
        imprimir_titulo(f"CREAR {controlador.nombre.upper()}")
        datos = {}
        for campo in controlador.campos:
            valor = input(f"{campo.capitalize()}: ")
            if controlador == self.productos and campo == "stock" and not valor.strip(): valor = "0"
            datos[campo] = valor
        self.mostrar_resultado(*controlador.crear(datos)); self.pausa()

    def ver_todos(self, controlador):
        imprimir_titulo(controlador.nombre.upper() + "S")
        lista = controlador.leer()
        if not lista: imprimir_info("No hay registros todavía.")
        else:
            for objeto in lista: print(" ", objeto)
            imprimir_info(f"Total: {len(lista)}")
        self.pausa()

    def buscar(self, controlador):
        texto = input("Texto para buscar: "); encontrados = controlador.buscar(texto)
        if not encontrados: imprimir_info("Sin coincidencias.")
        else:
            for objeto in encontrados: print(" ", objeto)
        self.pausa()

    def ver_por_id(self, controlador):
        id_registro = self.pedir_entero("Id: "); objeto = controlador.obtener(id_registro) if id_registro else None
        if objeto is None: imprimir_error("Registro no encontrado.")
        else:
            for clave, valor in objeto.a_diccionario().items(): print(f"  {clave.capitalize()}: {valor}")
        self.pausa()

    def actualizar(self, controlador):
        if controlador in (self.ventas, self.compras):
            imprimir_error("Las ventas/compras registradas no se pueden modificar."); self.pausa(); return
        id_registro = self.pedir_entero("Id del registro: "); objeto = controlador.obtener(id_registro) if id_registro else None
        if objeto is None: imprimir_error("Registro no encontrado."); self.pausa(); return
        print(f"Editando: {objeto.etiqueta()} (deje vacío para conservar el valor)")
        cambios = {}
        for campo in controlador.campos:
            actual = getattr(objeto, campo)
            nuevo = input(f"{campo.capitalize()} [{actual}]: ").strip()
            if nuevo: cambios[campo] = nuevo
        self.mostrar_resultado(*controlador.actualizar(id_registro, cambios)); self.pausa()

    def eliminar(self, controlador):
        id_registro = self.pedir_entero("Id del registro: "); objeto = controlador.obtener(id_registro) if id_registro else None
        if objeto is None: imprimir_error("Registro no encontrado.")
        elif confirmar(f"¿Eliminar {objeto.etiqueta()}? (s/n): "):
            self.mostrar_resultado(*controlador.eliminar(id_registro))
        else: imprimir_info("Operación cancelada.")
        self.pausa()

    def crear_venta(self):
        cliente_id = self.pedir_entero("Id del cliente: ")
        if cliente_id is None: imprimir_error("Id inválido."); self.pausa(); return
        print("Productos:")
        for p in self.productos.leer(): print(" ", p)
        items = []
        while True:
            pid = self.pedir_entero("Id del producto (0 para terminar): ")
            if pid in (None, 0): break
            cantidad = self.pedir_entero("Cantidad: ")
            if cantidad is None: imprimir_error("Cantidad inválida."); continue
            items.append({"producto_id": pid, "cantidad": cantidad})
        self.mostrar_resultado(*self.ventas.crear({"cliente_id": cliente_id, "items": items})); self.pausa()

    def ver_factura(self):
        id_venta = self.pedir_entero("Id de la venta: "); texto = self.ventas.factura(id_venta) if id_venta else None
        print(texto if texto else "No existe esa venta."); self.pausa()

    def crear_compra(self):
        imprimir_titulo("REGISTRAR COMPRA")
        proveedor_id = self.pedir_entero("Id del proveedor: ")
        if proveedor_id is None: imprimir_error("El id debe ser un número."); self.pausa(); return
        print("Productos disponibles:")
        for producto in self.productos.leer(): print(" ", producto)
        items = []
        while True:
            producto_id = self.pedir_entero("\nId del producto (0 para terminar): ")
            if producto_id in (None, 0): break
            cantidad = self.pedir_entero("Cantidad: ")
            costo = input("Costo unitario: ").strip()
            items.append({"producto_id": producto_id, "cantidad": cantidad, "costo_unitario": costo})
        self.mostrar_resultado(*self.compras.crear({"proveedor_id": proveedor_id, "items": items})); self.pausa()

    def ver_orden_compra(self):
        id_compra = self.pedir_entero("Id de la compra: "); texto = self.compras.orden_compra(id_compra) if id_compra else None
        print(texto if texto else "No existe esa compra."); self.pausa()

if __name__ == "__main__":
    try: Menu().ejecutar()
    except KeyboardInterrupt: print("\nPrograma interrumpido por el usuario.")

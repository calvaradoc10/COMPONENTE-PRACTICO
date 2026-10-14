from abc import ABC, abstractmethod
from shared import GestorJSON
from models import Cliente, Producto, Venta, Proveedor, Compra

class CrudBase(ABC):
    MODELO = None
    def __init__(self, nombre, archivo):
        self.nombre = nombre
        self.archivo = archivo
        self.gestor = GestorJSON(archivo)
        self.lista = []
        self.leer()
    @property
    def campos(self): return self.MODELO.CAMPOS
    def guardar(self): self.gestor.guardar([obj.a_diccionario() for obj in self.lista])
    def leer(self):
        self.lista = [self.MODELO.desde_diccionario(d) for d in self.gestor.leer()]
        return self.lista
    def obtener(self, id_registro):
        try: id_registro = int(id_registro)
        except (TypeError, ValueError): return None
        return next((o for o in self.lista if o.id == id_registro), None)
    def siguiente(self): return max((o.id for o in self.lista), default=0) + 1
    def listar(self): return self.leer()
    def buscar(self, texto):
        texto = str(texto).strip().lower()
        return [o for o in self.leer() if texto in str(o.a_diccionario()).lower()]
    @abstractmethod
    def validar(self, datos, excluir_id=None): pass
    def crear(self, datos):
        try:
            self.validar(datos)
            objeto = self.MODELO(self.siguiente(), **{c: datos.get(c, "") for c in self.MODELO.CAMPOS})
            self.lista.append(objeto); self.guardar()
            return True, f"{self.nombre.capitalize()} creado correctamente (id {objeto.id})."
        except (ValueError, TypeError, KeyError) as e: return False, str(e)
    def actualizar(self, id_registro, cambios):
        actual = self.obtener(id_registro)
        if actual is None: return False, "Registro no encontrado."
        datos = actual.a_diccionario(); datos.update({k:v for k,v in cambios.items() if k in self.MODELO.CAMPOS})
        try:
            self.validar(datos, excluir_id=actual.id)
            nuevo = self.MODELO(actual.id, **{c: datos.get(c, "") for c in self.MODELO.CAMPOS})
            self.lista[self.lista.index(actual)] = nuevo; self.guardar()
            return True, "Registro actualizado correctamente."
        except (ValueError, TypeError, KeyError) as e: return False, str(e)
    def eliminar(self, id_registro):
        actual = self.obtener(id_registro)
        if actual is None: return False, "Registro no encontrado."
        self.lista.remove(actual); self.guardar(); return True, "Registro eliminado correctamente."

class ClienteController(CrudBase):
    MODELO = Cliente
    def __init__(self, archivo="data/clientes.json"): super().__init__("cliente", archivo)
    def validar(self, datos, excluir_id=None):
        email = str(datos.get("email", "")).strip().lower()
        if any(x.id != excluir_id and x.email == email for x in self.lista): raise ValueError("Ese email ya está registrado.")

class ProductoController(CrudBase):
    MODELO = Producto
    def __init__(self, archivo="data/productos.json"): super().__init__("producto", archivo)
    def validar(self, datos, excluir_id=None):
        nombre = str(datos.get("nombre", "")).strip().lower()
        if any(x.id != excluir_id and x.nombre.lower() == nombre for x in self.lista): raise ValueError("Ese producto ya está registrado.")

class VentaController(CrudBase):
    MODELO = Venta
    def __init__(self, clientes, productos, archivo="data/ventas.json"):
        self.clientes = clientes; self.productos = productos
        super().__init__("venta", archivo)
    def validar(self, datos, excluir_id=None):
        if not self.clientes.obtener(datos.get("cliente_id")): raise ValueError("El cliente no existe.")
    def crear(self, datos):
        try:
            self.validar(datos)
            items = datos.get("items", [])
            if not items: raise ValueError("Agregue al menos un producto a la venta.")
            ids = [int(i["producto_id"]) for i in items]
            if len(ids) != len(set(ids)): raise ValueError("No repita productos en una misma venta.")
            venta = Venta(self.siguiente(), datos["cliente_id"])
            productos = []
            for item in items:
                producto = self.productos.obtener(item["producto_id"])
                if producto is None: raise ValueError(f"No existe el producto {item['producto_id']}.")
                cantidad = int(item["cantidad"])
                if not producto.hay_stock(cantidad): raise ValueError(f"Stock insuficiente de {producto.nombre}: hay {producto.stock}, piden {cantidad}")
                venta.agregar_detalle(producto, cantidad); productos.append((producto, cantidad))
            for producto, cantidad in productos: producto.descontar_stock(cantidad)
            self.lista.append(venta); self.productos.guardar(); self.guardar()
            return True, f"Venta registrada (id {venta.id}) por ${venta.total:.2f}."
        except (ValueError, TypeError, KeyError) as e: return False, str(e)
    def actualizar(self, id_registro, cambios): return False, "Las ventas registradas no se pueden modificar."
    def eliminar(self, id_registro): return False, "Las ventas registradas no se pueden eliminar."
    def factura(self, id_venta):
        venta = self.obtener(id_venta)
        if not venta: return None
        cliente = self.clientes.obtener(venta.cliente_id)
        lineas = [f"FACTURA #{venta.id}   fecha: {venta.fecha}", f"Cliente: {cliente.nombre_completo if cliente else venta.cliente_id}", "-"*46]
        lineas += [f"  {d.cantidad} x {d.descripcion} = ${d.subtotal:.2f}" for d in venta.detalles]
        lineas += ["-"*46, f"  TOTAL: ${venta.total:.2f}  ({venta.cantidad_items} ítems)"]
        return "\n".join(lineas)
    def ventas_de_cliente(self, id_cliente): return [v for v in self.leer() if v.cliente_id == int(id_cliente)]

class ProveedorController(CrudBase):
    MODELO = Proveedor
    def __init__(self, archivo="data/proveedores.json"): super().__init__("proveedor", archivo)
    def buscar(self, texto):
        texto = str(texto).strip().lower()
        return [p for p in self.leer() if texto in f"{p.nombre} {p.apellido} {p.email} {p.ruc} {p.empresa}".lower()]
    def validar(self, datos, excluir_id=None):
        email = str(datos.get("email", "")).strip().lower(); ruc = str(datos.get("ruc", "")).strip()
        if any(x.id != excluir_id and x.email == email for x in self.lista): raise ValueError("Ese email ya está registrado.")
        if any(x.id != excluir_id and x.ruc == ruc for x in self.lista): raise ValueError("Ese RUC ya está registrado.")

class CompraController(CrudBase):
    MODELO = Compra
    def __init__(self, proveedores, productos, archivo="data/compras.json"):
        self.proveedores = proveedores; self.productos = productos
        super().__init__("compra", archivo)
    def validar(self, datos, excluir_id=None):
        if not self.proveedores.obtener(datos.get("proveedor_id")): raise ValueError("El proveedor no existe.")
    def crear(self, datos):
        try:
            self.validar(datos)
            items = datos.get("items", [])
            if not items: raise ValueError("Agregue al menos un producto a la compra.")
            ids = [int(i["producto_id"]) for i in items]
            if len(ids) != len(set(ids)): raise ValueError("No repita productos en una misma compra.")
            compra = Compra(self.siguiente(), datos["proveedor_id"])
            productos = []
            # Primero valida y construye TODOS los detalles. Aún no cambia stock.
            for item in items:
                producto = self.productos.obtener(item["producto_id"])
                if producto is None: raise ValueError(f"No existe el producto {item['producto_id']}.")
                cantidad = int(item["cantidad"])
                compra.agregar_detalle(producto, cantidad, item["costo_unitario"])
                productos.append((producto, cantidad))
            # Solo cuando todo es válido, se suma el stock y se guardan ambos archivos.
            for producto, cantidad in productos: producto.aumentar_stock(cantidad)
            self.lista.append(compra)
            self.productos.guardar(); self.guardar()
            return True, f"Compra registrada (id {compra.id}) por ${compra.total:.2f}."
        except (ValueError, TypeError, KeyError) as e: return False, str(e)
    def actualizar(self, id_registro, cambios): return False, "Las compras registradas no se pueden modificar."
    def eliminar(self, id_registro): return False, "Las compras registradas no se pueden eliminar."
    def orden_compra(self, id_compra):
        compra = self.obtener(id_compra)
        if not compra: return None
        proveedor = self.proveedores.obtener(compra.proveedor_id)
        nombre = f"{proveedor.empresa} · {proveedor.nombre_completo} · RUC {proveedor.ruc}" if proveedor else str(compra.proveedor_id)
        lineas = [f"ORDEN DE COMPRA #{compra.id}   fecha: {compra.fecha}", f"Proveedor: {nombre}", "-"*46]
        lineas += [f"  {d}" for d in compra.detalles]
        lineas += ["-"*46, f"  TOTAL: ${compra.total:.2f}  ({compra.cantidad_items} ítems)"]
        return "\n".join(lineas)
    def compras_de_proveedor(self, id_proveedor): return [c for c in self.leer() if c.proveedor_id == int(id_proveedor)]

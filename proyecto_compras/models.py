from abc import ABC, abstractmethod
from datetime import date

class ModeloBase(ABC):
    CAMPOS = ()
    OBLIGATORIOS = ()
    def __init__(self, id_registro): self.__id = int(id_registro)
    @property
    def id(self): return self.__id
    @staticmethod
    def limpiar(texto): return str(texto).strip()
    @abstractmethod
    def a_diccionario(self): pass
    @abstractmethod
    def etiqueta(self): pass
    @classmethod
    def desde_diccionario(cls, datos):
        valores = {campo: datos.get(campo, "") for campo in cls.CAMPOS}
        return cls(datos["id"], **valores)
    def __str__(self): return f"[{self.id}] {self.etiqueta()}"

class Persona(ModeloBase):
    CAMPOS = ("nombre", "apellido", "email")
    OBLIGATORIOS = CAMPOS
    def __init__(self, id_registro, nombre, apellido, email):
        super().__init__(id_registro); self.nombre = nombre; self.apellido = apellido; self.email = email
    @staticmethod
    def es_email_valido(texto):
        texto = str(texto).strip()
        if texto.count("@") != 1: return False
        usuario, dominio = texto.split("@")
        return bool(usuario) and "." in dominio and not dominio.endswith(".") and " " not in texto
    @property
    def nombre(self): return self.__nombre
    @nombre.setter
    def nombre(self, valor):
        valor = Persona.limpiar(valor)
        if not valor: raise ValueError("El nombre es obligatorio")
        self.__nombre = valor.title()
    @property
    def apellido(self): return self.__apellido
    @apellido.setter
    def apellido(self, valor):
        valor = Persona.limpiar(valor)
        if not valor: raise ValueError("El apellido es obligatorio")
        self.__apellido = valor.title()
    @property
    def email(self): return self.__email
    @email.setter
    def email(self, valor):
        valor = Persona.limpiar(valor)
        if not Persona.es_email_valido(valor): raise ValueError(f"Email inválido: '{valor}'")
        self.__email = valor.lower()
    @property
    def nombre_completo(self): return f"{self.__nombre} {self.__apellido}"
    def a_diccionario(self): return {"id": self.id, "nombre": self.__nombre, "apellido": self.__apellido, "email": self.__email}

class Cliente(Persona):
    CAMPOS = Persona.CAMPOS + ("telefono", "ciudad")
    OBLIGATORIOS = Persona.OBLIGATORIOS
    def __init__(self, id_registro, nombre, apellido, email, telefono="", ciudad=""):
        super().__init__(id_registro, nombre, apellido, email); self.telefono = telefono; self.ciudad = ciudad
    @property
    def telefono(self): return self.__telefono
    @telefono.setter
    def telefono(self, valor):
        valor = self.limpiar(valor)
        if valor and not valor.isdigit(): raise ValueError("El teléfono solo puede tener números")
        self.__telefono = valor
    @property
    def ciudad(self): return self.__ciudad
    @ciudad.setter
    def ciudad(self, valor): self.__ciudad = self.limpiar(valor).title()
    def a_diccionario(self):
        datos = super().a_diccionario(); datos.update(telefono=self.__telefono, ciudad=self.__ciudad); return datos
    def etiqueta(self): return f"{self.nombre_completo} · {self.email}"

class Producto(ModeloBase):
    CAMPOS = ("nombre", "precio", "stock")
    OBLIGATORIOS = ("nombre", "precio")
    def __init__(self, id_registro, nombre, precio, stock=0):
        super().__init__(id_registro); self.nombre = nombre; self.precio = precio; self.stock = stock
    @property
    def nombre(self): return self.__nombre
    @nombre.setter
    def nombre(self, valor):
        valor = self.limpiar(valor)
        if not valor: raise ValueError("El nombre del producto es obligatorio")
        self.__nombre = valor.title()
    @property
    def precio(self): return self.__precio
    @precio.setter
    def precio(self, valor):
        try: valor = float(valor)
        except (TypeError, ValueError): raise ValueError(f"El precio debe ser un número: '{valor}'")
        if valor <= 0: raise ValueError("El precio debe ser mayor a 0")
        self.__precio = round(valor, 2)
    @property
    def stock(self): return self.__stock
    @stock.setter
    def stock(self, valor):
        try: valor = int(valor)
        except (TypeError, ValueError): raise ValueError(f"El stock debe ser un número entero: '{valor}'")
        if valor < 0: raise ValueError("El stock no puede ser negativo")
        self.__stock = valor
    @property
    def disponible(self): return self.__stock > 0
    def hay_stock(self, cantidad): return 0 < cantidad <= self.__stock
    def descontar_stock(self, cantidad):
        if not self.hay_stock(cantidad): raise ValueError(f"Stock insuficiente de {self.__nombre}: hay {self.__stock}, piden {cantidad}")
        self.__stock -= cantidad
    def aumentar_stock(self, cantidad):
        try: cantidad = int(cantidad)
        except (TypeError, ValueError): raise ValueError("La cantidad comprada debe ser un entero")
        if cantidad <= 0: raise ValueError("La cantidad comprada debe ser mayor a 0")
        self.__stock += cantidad
    def a_diccionario(self): return {"id": self.id, "nombre": self.__nombre, "precio": self.__precio, "stock": self.__stock}
    def etiqueta(self): return f"{self.__nombre} · ${self.__precio:.2f} · stock {self.__stock}"

class DetalleVenta:
    def __init__(self, producto_id, descripcion, cantidad, precio_unitario):
        self.__producto_id = int(producto_id); self.__descripcion = str(descripcion); self.cantidad = cantidad; self.precio_unitario = precio_unitario
    @property
    def producto_id(self): return self.__producto_id
    @property
    def descripcion(self): return self.__descripcion
    @property
    def cantidad(self): return self.__cantidad
    @cantidad.setter
    def cantidad(self, valor):
        try: valor = int(valor)
        except (TypeError, ValueError): raise ValueError(f"La cantidad debe ser un número entero: '{valor}'")
        if valor <= 0: raise ValueError("La cantidad debe ser mayor a 0")
        self.__cantidad = valor
    @property
    def precio_unitario(self): return self.__precio_unitario
    @precio_unitario.setter
    def precio_unitario(self, valor):
        try: valor = float(valor)
        except (TypeError, ValueError): raise ValueError(f"El precio debe ser un número: '{valor}'")
        if valor <= 0: raise ValueError("El precio unitario debe ser mayor a 0")
        self.__precio_unitario = round(valor, 2)
    @property
    def subtotal(self): return round(self.__cantidad * self.__precio_unitario, 2)
    def a_diccionario(self): return {"producto_id": self.__producto_id, "descripcion": self.__descripcion, "cantidad": self.__cantidad, "precio_unitario": self.__precio_unitario, "subtotal": self.subtotal}
    @classmethod
    def desde_diccionario(cls, datos): return cls(datos["producto_id"], datos["descripcion"], datos["cantidad"], datos["precio_unitario"])
    def __str__(self): return f"{self.__cantidad} x {self.__descripcion} = ${self.subtotal:.2f}"

class Venta(ModeloBase):
    CAMPOS = ("cliente_id", "fecha"); OBLIGATORIOS = ("cliente_id",)
    def __init__(self, id_registro, cliente_id, fecha="", detalles=None):
        super().__init__(id_registro); self.cliente_id = cliente_id; self.fecha = fecha or date.today().isoformat(); self.__detalles = list(detalles) if detalles else []
    @property
    def cliente_id(self): return self.__cliente_id
    @cliente_id.setter
    def cliente_id(self, valor):
        try: self.__cliente_id = int(valor)
        except (TypeError, ValueError): raise ValueError(f"cliente_id inválido: '{valor}'")
    @property
    def fecha(self): return self.__fecha
    @fecha.setter
    def fecha(self, valor): self.__fecha = self.limpiar(valor)
    @property
    def detalles(self): return tuple(self.__detalles)
    @property
    def total(self): return round(sum(d.subtotal for d in self.__detalles), 2)
    @property
    def cantidad_items(self): return sum(d.cantidad for d in self.__detalles)
    def agregar_detalle(self, producto, cantidad):
        if not producto.hay_stock(int(cantidad)): raise ValueError(f"Stock insuficiente de {producto.nombre}: hay {producto.stock}, piden {cantidad}")
        detalle = DetalleVenta(producto.id, producto.nombre, cantidad, producto.precio); self.__detalles.append(detalle); return detalle
    def a_diccionario(self): return {"id": self.id, "cliente_id": self.__cliente_id, "fecha": self.__fecha, "total": self.total, "detalles": [d.a_diccionario() for d in self.__detalles]}
    @classmethod
    def desde_diccionario(cls, datos): return cls(datos["id"], datos["cliente_id"], datos.get("fecha", ""), [DetalleVenta.desde_diccionario(d) for d in datos.get("detalles", [])])
    def etiqueta(self): return f"Venta del {self.__fecha} · cliente {self.__cliente_id} · {len(self.__detalles)} ítem(s) · ${self.total:.2f}"

class Proveedor(Persona):
    CAMPOS = Persona.CAMPOS + ("ruc", "empresa")
    OBLIGATORIOS = Persona.OBLIGATORIOS + ("ruc",)
    def __init__(self, id_registro, nombre, apellido, email, ruc="", empresa=""):
        super().__init__(id_registro, nombre, apellido, email); self.ruc = ruc; self.empresa = empresa
    @property
    def ruc(self): return self.__ruc
    @ruc.setter
    def ruc(self, valor):
        valor = self.limpiar(valor)
        if len(valor) != 13 or not valor.isdigit(): raise ValueError(f"El RUC debe tener 13 números: '{valor}'")
        self.__ruc = valor
    @property
    def empresa(self): return self.__empresa
    @empresa.setter
    def empresa(self, valor): self.__empresa = self.limpiar(valor).title()
    def a_diccionario(self):
        datos = super().a_diccionario(); datos.update(ruc=self.__ruc, empresa=self.__empresa); return datos
    def etiqueta(self): return f"{self.__empresa or 'Sin empresa'} · {self.nombre_completo} · RUC {self.__ruc}"

class DetalleCompra:
    def __init__(self, producto_id, descripcion, cantidad, costo_unitario):
        self.__producto_id = int(producto_id); self.__descripcion = str(descripcion); self.cantidad = cantidad; self.costo_unitario = costo_unitario
    @property
    def producto_id(self): return self.__producto_id
    @property
    def descripcion(self): return self.__descripcion
    @property
    def cantidad(self): return self.__cantidad
    @cantidad.setter
    def cantidad(self, valor):
        try: valor = int(valor)
        except (TypeError, ValueError): raise ValueError(f"La cantidad debe ser un número entero: '{valor}'")
        if valor <= 0: raise ValueError("La cantidad debe ser mayor a 0")
        self.__cantidad = valor
    @property
    def costo_unitario(self): return self.__costo_unitario
    @costo_unitario.setter
    def costo_unitario(self, valor):
        try: valor = float(valor)
        except (TypeError, ValueError): raise ValueError(f"El costo debe ser un número: '{valor}'")
        if valor <= 0: raise ValueError("El costo unitario debe ser mayor a 0")
        self.__costo_unitario = round(valor, 2)
    @property
    def subtotal(self): return round(self.__cantidad * self.__costo_unitario, 2)
    def a_diccionario(self): return {"producto_id": self.__producto_id, "descripcion": self.__descripcion, "cantidad": self.__cantidad, "costo_unitario": self.__costo_unitario, "subtotal": self.subtotal}
    @classmethod
    def desde_diccionario(cls, datos): return cls(datos["producto_id"], datos["descripcion"], datos["cantidad"], datos["costo_unitario"])
    def __str__(self): return f"{self.__cantidad} x {self.__descripcion} a ${self.__costo_unitario:.2f} = ${self.subtotal:.2f}"

class Compra(ModeloBase):
    CAMPOS = ("proveedor_id", "fecha"); OBLIGATORIOS = ("proveedor_id",)
    def __init__(self, id_registro, proveedor_id, fecha="", detalles=None):
        super().__init__(id_registro); self.proveedor_id = proveedor_id; self.fecha = fecha or date.today().isoformat(); self.__detalles = list(detalles) if detalles else []
    @property
    def proveedor_id(self): return self.__proveedor_id
    @proveedor_id.setter
    def proveedor_id(self, valor):
        try: self.__proveedor_id = int(valor)
        except (TypeError, ValueError): raise ValueError(f"proveedor_id inválido: '{valor}'")
    @property
    def fecha(self): return self.__fecha
    @fecha.setter
    def fecha(self, valor): self.__fecha = self.limpiar(valor)
    @property
    def detalles(self): return tuple(self.__detalles)
    @property
    def total(self): return round(sum(d.subtotal for d in self.__detalles), 2)
    @property
    def cantidad_items(self): return sum(d.cantidad for d in self.__detalles)
    def agregar_detalle(self, producto, cantidad, costo_unitario):
        detalle = DetalleCompra(producto.id, producto.nombre, cantidad, costo_unitario); self.__detalles.append(detalle); return detalle
    def a_diccionario(self): return {"id": self.id, "proveedor_id": self.__proveedor_id, "fecha": self.__fecha, "total": self.total, "detalles": [d.a_diccionario() for d in self.__detalles]}
    @classmethod
    def desde_diccionario(cls, datos): return cls(datos["id"], datos["proveedor_id"], datos.get("fecha", ""), [DetalleCompra.desde_diccionario(d) for d in datos.get("detalles", [])])
    def etiqueta(self): return f"Compra del {self.__fecha} · proveedor {self.__proveedor_id} · {len(self.__detalles)} ítem(s) · ${self.total:.2f}"

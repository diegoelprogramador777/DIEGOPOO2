import mysql.connector
from mysql.connector import Error

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'ecommerce_jerseys'
}

class Producto:
    def __init__(self, id, nombre, precio, stock):
        self.id = id
        self.nombre = nombre
        self.precio = precio
        self.stock = stock

class Carrito:
    def __init__(self):
        self.items = []
    
    def agregar_producto(self, producto, cantidad):
        if producto.stock >= cantidad:
            self.items.append((producto, cantidad))
            producto.stock -= cantidad
            print(f"{cantidad} {producto.nombre}(s) añadido(s) al carrito")
        else:
            print("Stock insuficiente")

class Tienda:
    def __init__(self):
        self.conexion = self.conectar_db()
        self.inicializar_db()
        self.productos = self.cargar_productos()
    
    def conectar_db(self):
        try:
            return mysql.connector.connect(**DB_CONFIG)
        except Error as e:
            print(f"Error de conexión: {e}")
            exit(1)
    
    def inicializar_db(self):
        cursor = self.conexion.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id INT PRIMARY KEY,
                nombre VARCHAR(255) UNIQUE,
                precio DECIMAL(10,2),
                stock INT
            )
        """)
        
        # Insertar productos iniciales
        productos_iniciales = [
            (1, 'Jersey México Local', 899.00, 10),
            (2, 'Jersey México Visitante', 899.00, 10)
        ]
        
        for producto in productos_iniciales:
            try:
                cursor.execute("""
                    INSERT INTO productos (id, nombre, precio, stock)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    nombre=VALUES(nombre), precio=VALUES(precio)
                """, producto)
            except Error as e:
                print(f"Error insertando producto: {e}")
        
        self.conexion.commit()
    
    def cargar_productos(self):
        cursor = self.conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM productos")
        return [Producto(p['id'], p['nombre'], p['precio'], p['stock']) 
                for p in cursor.fetchall()]
    
    def mostrar_productos(self):
        print("\nProductos disponibles:")
        for p in self.productos:
            print(f"{p.id}. {p.nombre} - ${p.precio} (Stock: {p.stock})")
    
    def procesar_compra(self, carrito):
        if not carrito.items:
            print("Carrito vacío")
            return
        
        total = sum(p.precio * cantidad for p, cantidad in carrito.items)
        print(f"\nTotal a pagar: ${total:.2f}")
        
        try:
            cursor = self.conexion.cursor()
            for producto, cantidad in carrito.items:
                cursor.execute("""
                    UPDATE productos 
                    SET stock = stock - %s 
                    WHERE id = %s
                """, (cantidad, producto.id))
            
            self.conexion.commit()
            print("¡Compra exitosa! Gracias por su compra")
        except Error as e:
            print(f"Error procesando compra: {e}")
            self.conexion.rollback()

def main():
    tienda = Tienda()
    carrito = Carrito()
    
    while True:
        print("\n--- Tienda de Jerseys México ---")
        print("1. Ver productos")
        print("2. Agregar al carrito")
        print("3. Ver carrito")
        print("4. Comprar")
        print("5. Salir")
        
        opcion = input("Seleccione una opción: ")
        
        if opcion == '1':
            tienda.mostrar_productos()
        elif opcion == '2':
            tienda.mostrar_productos()
            try:
                id_producto = int(input("ID del producto: "))
                cantidad = int(input("Cantidad: "))
                producto = next(p for p in tienda.productos if p.id == id_producto)
                carrito.agregar_producto(producto, cantidad)
            except:
                print("Selección inválida")
        elif opcion == '3':
            print("\nCarrito:")
            for p, cantidad in carrito.items:
                print(f"{p.nombre} x{cantidad} - ${p.precio * cantidad:.2f}")
        elif opcion == '4':
            tienda.procesar_compra(carrito)
            carrito = Carrito()
        elif opcion == '5':
            print("¡Hasta luego!")
            break
        else:
            print("Opción no válida")

if __name__ == "__main__":
    main()

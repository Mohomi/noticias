from conecta import obtener_conexion
import mysql.connector

def crear_tabla_clima():
    """
    Crea la tabla tbl_clima si no existe.
    """
    try:
        conn = obtener_conexion()
        cur = conn.cursor()
        
        create_table_query = """
        CREATE TABLE IF NOT EXISTS tbl_clima (
            id_clima INT AUTO_INCREMENT PRIMARY KEY,
            id_ubicacion VARCHAR(50) NOT NULL,
            t_actual DECIMAL(5,2),
            t_maxima DECIMAL(5,2),
            t_minima DECIMAL(5,2),
            descripcion VARCHAR(255),
            icono VARCHAR(50),
            fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY unique_ubicacion (id_ubicacion)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        
        cur.execute(create_table_query)
        conn.commit()
        
        print("✅ Tabla tbl_clima creada correctamente")
        
        # Insertar datos de ejemplo
        insert_query = """
        INSERT INTO tbl_clima (id_ubicacion, t_actual, t_maxima, t_minima, descripcion, icono)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            t_actual = VALUES(t_actual),
            t_maxima = VALUES(t_maxima),
            t_minima = VALUES(t_minima),
            descripcion = VALUES(descripcion),
            icono = VALUES(icono)
        """
        
        # Datos de ejemplo para Punitaqui
        datos_ejemplo = [
            ('com-punitaqui', 22.5, 28.0, 15.0, 'Soleado', '☀️'),
            ('reg-coquimbo', 20.0, 25.0, 14.0, 'Parcialmente nublado', '⛅'),
            ('cl', 18.0, 23.0, 12.0, 'Nublado', '☁️')
        ]
        
        cur.executemany(insert_query, datos_ejemplo)
        conn.commit()
        
        print(f"✅ Insertados {len(datos_ejemplo)} registros de ejemplo")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    crear_tabla_clima()

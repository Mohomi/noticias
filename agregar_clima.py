from conecta import obtener_conexion

def agregar_clima_providencia():
    try:
        conn = obtener_conexion()
        cur = conn.cursor()
        
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
        
        datos = ('com-providencia', 24.0, 30.0, 18.0, 'Soleado', '☀️')
        
        cur.execute(insert_query, datos)
        conn.commit()
        
        print("✅ Agregado clima para com-providencia")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    agregar_clima_providencia()

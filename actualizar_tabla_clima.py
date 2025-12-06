from conecta import obtener_conexion
import mysql.connector

def actualizar_tabla_clima():
    """
    Actualiza la tabla tbl_clima agregando columnas para coordenadas geográficas
    y poblando datos de ubicaciones chilenas comunes.
    """
    try:
        conn = obtener_conexion()
        cur = conn.cursor()
        
        print("🔧 Actualizando estructura de tbl_clima...")
        
        # Verificar si las columnas ya existen
        cur.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'tbl_clima' 
            AND COLUMN_NAME IN ('latitud', 'longitud')
        """)
        existing_columns = cur.fetchone()[0]
        
        if existing_columns < 2:
            # Agregar columnas de coordenadas
            alter_query = """
            ALTER TABLE tbl_clima 
            ADD COLUMN latitud DECIMAL(10,8),
            ADD COLUMN longitud DECIMAL(11,8)
            """
            
            try:
                cur.execute(alter_query)
                conn.commit()
                print("✅ Columnas latitud y longitud agregadas correctamente")
            except mysql.connector.Error as e:
                if "Duplicate column name" in str(e):
                    print("ℹ️  Las columnas ya existen, continuando...")
                else:
                    raise e
        else:
            print("ℹ️  Las columnas latitud y longitud ya existen")
        
        # Actualizar coordenadas para ubicaciones existentes
        print("\n📍 Actualizando coordenadas de ubicaciones chilenas...")
        
        # Datos de ubicaciones chilenas comunes (id_ubicacion, latitud, longitud)
        ubicaciones_chile = [
            # País
            ('cl', -33.4489, -70.6693),  # Santiago (capital)
            
            # Regiones principales
            ('reg-coquimbo', -29.9533, -71.3395),  # La Serena
            ('reg-valparaiso', -33.0472, -71.6127),  # Valparaíso
            ('reg-metropolitana', -33.4489, -70.6693),  # Santiago
            ('reg-biobio', -36.8270, -73.0498),  # Concepción
            
            # Comunas específicas que ya existen en la BD
            ('com-punitaqui', -30.9833, -71.2667),  # Punitaqui
            ('com-providencia', -33.4333, -70.6167),  # Providencia
            ('com-santiago', -33.4489, -70.6693),  # Santiago Centro
            ('com-valparaiso', -33.0472, -71.6127),  # Valparaíso
            ('com-concepcion', -36.8270, -73.0498),  # Concepción
            ('com-la-serena', -29.9027, -71.2519),  # La Serena
            ('com-antofagasta', -23.6509, -70.3975),  # Antofagasta
            ('com-temuco', -38.7359, -72.5904),  # Temuco
            ('com-puerto-montt', -41.4693, -72.9424),  # Puerto Montt
            ('com-punta-arenas', -53.1638, -70.9171),  # Punta Arenas
        ]
        
        update_query = """
        UPDATE tbl_clima 
        SET latitud = %s, longitud = %s
        WHERE id_ubicacion = %s
        """
        
        updated_count = 0
        for id_ubicacion, lat, lon in ubicaciones_chile:
            try:
                cur.execute(update_query, (lat, lon, id_ubicacion))
                if cur.rowcount > 0:
                    updated_count += 1
                    print(f"  ✓ {id_ubicacion}: ({lat}, {lon})")
            except Exception as e:
                print(f"  ⚠️  Error actualizando {id_ubicacion}: {e}")
        
        conn.commit()
        print(f"\n✅ Actualizadas {updated_count} ubicaciones con coordenadas")
        
        # Insertar nuevas ubicaciones si no existen
        print("\n📝 Insertando ubicaciones faltantes...")
        
        insert_query = """
        INSERT INTO tbl_clima (id_ubicacion, latitud, longitud, t_actual, t_maxima, t_minima, descripcion, icono)
        VALUES (%s, %s, %s, NULL, NULL, NULL, 'Sin datos', '❓')
        ON DUPLICATE KEY UPDATE
            latitud = VALUES(latitud),
            longitud = VALUES(longitud)
        """
        
        inserted_count = 0
        for id_ubicacion, lat, lon in ubicaciones_chile:
            try:
                cur.execute(insert_query, (id_ubicacion, lat, lon))
                if cur.rowcount > 0:
                    inserted_count += 1
            except Exception as e:
                print(f"  ⚠️  Error insertando {id_ubicacion}: {e}")
        
        conn.commit()
        print(f"✅ Procesadas {inserted_count} ubicaciones")
        
        # Mostrar resumen de la tabla
        print("\n📊 Resumen de tbl_clima:")
        cur.execute("""
            SELECT id_ubicacion, latitud, longitud, t_actual, descripcion 
            FROM tbl_clima 
            ORDER BY id_ubicacion
        """)
        rows = cur.fetchall()
        
        print(f"\nTotal de registros: {len(rows)}")
        print("\nPrimeros 10 registros:")
        for i, row in enumerate(rows[:10], 1):
            id_ub, lat, lon, temp, desc = row
            coord_str = f"({lat}, {lon})" if lat and lon else "Sin coordenadas"
            temp_str = f"{temp}°C" if temp else "N/A"
            print(f"  {i}. {id_ub}: {coord_str} - {temp_str} - {desc}")
        
        cur.close()
        conn.close()
        
        print("\n✅ Actualización completada exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Actualizando tabla tbl_clima")
    print("=" * 60)
    actualizar_tabla_clima()

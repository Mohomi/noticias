from conecta import obtener_conexion

def verificar_tablas_geograficas():
    try:
        conn = obtener_conexion()
        cur = conn.cursor()
        
        tablas = ['tbl_paises', 'tbl_regiones', 'tbl_provincias', 'tbl_comunas']
        
        for tabla in tablas:
            print(f"\n📋 Estructura de {tabla}:")
            try:
                cur.execute(f"DESCRIBE {tabla}")
                columnas = cur.fetchall()
                for col in columnas:
                    print(f"  - {col[0]} ({col[1]})")
                
                # Ver algunos datos de ejemplo
                cur.execute(f"SELECT * FROM {tabla} LIMIT 3")
                datos = cur.fetchall()
                print(f"\n  Datos de ejemplo ({len(datos)} registros):")
                for dato in datos:
                    print(f"    {dato}")
            except Exception as e:
                print(f"  ❌ Error: {e}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verificar_tablas_geograficas()

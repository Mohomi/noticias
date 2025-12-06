from conecta import obtener_conexion

def verificar_estructura_clima():
    try:
        conn = obtener_conexion()
        cur = conn.cursor()
        
        # Ver estructura de la tabla
        cur.execute("DESCRIBE tbl_clima")
        columnas = cur.fetchall()
        
        print("📋 Estructura de tbl_clima:")
        for col in columnas:
            print(f"  - {col}")
        
        # Ver algunos datos de ejemplo
        cur.execute("SELECT * FROM tbl_clima LIMIT 5")
        datos = cur.fetchall()
        
        print(f"\n📊 Datos de ejemplo: {len(datos)} registros")
        for dato in datos:
            print(f"  - {dato}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verificar_estructura_clima()

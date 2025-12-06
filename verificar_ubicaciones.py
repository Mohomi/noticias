from conecta import obtener_conexion

def verificar_estructura():
    try:
        conn = obtener_conexion()
        cur = conn.cursor()
        
        # Ver estructura de la tabla
        cur.execute("DESCRIBE tbl_preferenciaubicacion")
        columnas = cur.fetchall()
        
        print("📋 Estructura de tbl_preferenciaubicacion:")
        for col in columnas:
            print(f"  - {col}")
        
        # Ver datos
        cur.execute("SELECT * FROM tbl_preferenciaubicacion WHERE id_usuario = 1")
        ubicaciones = cur.fetchall()
        
        print(f"\n📊 Datos guardados para usuario 1: {len(ubicaciones)} registros")
        for ub in ubicaciones:
            print(f"  - {ub}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verificar_estructura()

from conecta import obtener_conexion

def verificar_tipos():
    try:
        conn = obtener_conexion()
        cur = conn.cursor()
        
        print("📋 Estructura de tbl_preferenciaubicacion:")
        cur.execute("DESCRIBE tbl_preferenciaubicacion")
        for col in cur.fetchall():
            print(f"  - {col}")
        
        print("\n📋 Estructura de tbl_clima:")
        cur.execute("DESCRIBE tbl_clima")
        for col in cur.fetchall():
            print(f"  - {col}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    verificar_tipos()

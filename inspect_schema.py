from conecta import obtener_conexion

def inspect_schema():
    try:
        conn = obtener_conexion()
        cur = conn.cursor(dictionary=True)
        
        print("🔍 Columnas de tbl_noticia:")
        cur.execute("DESCRIBE tbl_noticia")
        columns = cur.fetchall()
        for col in columns:
            print(f"- {col['Field']} ({col['Type']})")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    inspect_schema()

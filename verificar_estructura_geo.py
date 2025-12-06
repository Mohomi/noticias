from conecta import obtener_conexion

def verificar_estructura_completa():
    try:
        conn = obtener_conexion()
        cur = conn.cursor(dictionary=True)
        
        print("=" * 60)
        print("VERIFICACIÓN DE TABLAS GEOGRÁFICAS")
        print("=" * 60)
        
        # 1. Países
        print("\n📍 TBL_PAISES:")
        cur.execute("DESCRIBE tbl_paises")
        for col in cur.fetchall():
            print(f"  {col['Field']:20} {col['Type']:20} {col['Key']}")
        
        cur.execute("SELECT * FROM tbl_paises LIMIT 3")
        print("\n  Datos:")
        for row in cur.fetchall():
            print(f"    {row}")
        
        # 2. Regiones
        print("\n📍 TBL_REGIONES:")
        cur.execute("DESCRIBE tbl_regiones")
        for col in cur.fetchall():
            print(f"  {col['Field']:20} {col['Type']:20} {col['Key']}")
        
        cur.execute("SELECT * FROM tbl_regiones LIMIT 5")
        print("\n  Datos:")
        for row in cur.fetchall():
            print(f"    {row}")
        
        # 3. Provincias
        print("\n📍 TBL_PROVINCIAS:")
        cur.execute("DESCRIBE tbl_provincias")
        for col in cur.fetchall():
            print(f"  {col['Field']:20} {col['Type']:20} {col['Key']}")
        
        cur.execute("SELECT * FROM tbl_provincias LIMIT 5")
        print("\n  Datos:")
        for row in cur.fetchall():
            print(f"    {row}")
        
        # 4. Comunas
        print("\n📍 TBL_COMUNAS:")
        cur.execute("DESCRIBE tbl_comunas")
        for col in cur.fetchall():
            print(f"  {col['Field']:20} {col['Type']:20} {col['Key']}")
        
        cur.execute("SELECT * FROM tbl_comunas LIMIT 5")
        print("\n  Datos:")
        for row in cur.fetchall():
            print(f"    {row}")
        
        # Verificar relaciones
        print("\n" + "=" * 60)
        print("VERIFICACIÓN DE RELACIONES")
        print("=" * 60)
        
        cur.execute("SELECT COUNT(*) as total FROM tbl_paises")
        print(f"\n📊 Total países: {cur.fetchone()['total']}")
        
        cur.execute("SELECT COUNT(*) as total FROM tbl_regiones")
        print(f"📊 Total regiones: {cur.fetchone()['total']}")
        
        cur.execute("SELECT COUNT(*) as total FROM tbl_provincias")
        print(f"📊 Total provincias: {cur.fetchone()['total']}")
        
        cur.execute("SELECT COUNT(*) as total FROM tbl_comunas")
        print(f"📊 Total comunas: {cur.fetchone()['total']}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verificar_estructura_completa()

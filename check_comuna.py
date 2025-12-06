from conecta import obtener_conexion

def check_comuna_name(nombre):
    print(f"🔍 Checking comuna name like {nombre}")
    conn = obtener_conexion()
    cur = conn.cursor(dictionary=True)
    
    try:
        query = "SELECT * FROM tbl_comunas WHERE nombre LIKE %s"
        cur.execute(query, (f"%{nombre}%",))
        res = cur.fetchall()
        print(f"Results: {len(res)}")
        for r in res:
            print(r)
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    check_comuna_name("Providencia")

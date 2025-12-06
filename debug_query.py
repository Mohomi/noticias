from conecta import obtener_conexion

def debug_query(id_usuario):
    print(f"🔍 Debugging query for user {id_usuario}")
    conn = obtener_conexion()
    cur = conn.cursor(dictionary=True)
    
    query = """
        SELECT DISTINCT p.id_ubicacion, c.latitud, c.longitud
        FROM tbl_preferenciaubicacion p
        LEFT JOIN tbl_clima c ON CAST(p.id_ubicacion AS CHAR) = CAST(c.id_ubicacion AS CHAR)
        WHERE p.id_usuario = %s
        AND c.latitud IS NOT NULL 
        AND c.longitud IS NOT NULL
    """
    print("Executing query:")
    print(query)
    
    cur.execute(query, (id_usuario,))
    results = cur.fetchall()
    print(f"Results: {len(results)}")
    for r in results:
        print(r)
        
    # Try without CAST
    print("\nTrying without CAST:")
    query2 = """
        SELECT DISTINCT p.id_ubicacion, c.latitud, c.longitud
        FROM tbl_preferenciaubicacion p
        LEFT JOIN tbl_clima c ON p.id_ubicacion = c.id_ubicacion
        WHERE p.id_usuario = %s
        AND c.latitud IS NOT NULL 
        AND c.longitud IS NOT NULL
    """
    try:
        cur.execute(query2, (id_usuario,))
        results2 = cur.fetchall()
        print(f"Results without CAST: {len(results2)}")
        for r in results2:
            print(r)
    except Exception as e:
        print(f"Error without CAST: {e}")

    cur.close()
    conn.close()

if __name__ == "__main__":
    debug_query(1)

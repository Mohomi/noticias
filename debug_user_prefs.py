from conecta import obtener_conexion

def debug_user_prefs(id_usuario):
    print(f"🔍 Debugging preferences for user {id_usuario}")
    conn = obtener_conexion()
    cur = conn.cursor(dictionary=True)
    
    # Check preferences
    cur.execute("SELECT * FROM tbl_preferenciaubicacion WHERE id_usuario = %s", (id_usuario,))
    prefs = cur.fetchall()
    print(f"📋 Preferences found: {len(prefs)}")
    for p in prefs:
        print(f"  - {repr(p['id_ubicacion'])} ({p['tipo_ubicacion']})")
        
        # Check coordinates for this location
        cur.execute("SELECT * FROM tbl_clima WHERE id_ubicacion = %s", (p['id_ubicacion'],))
        clima = cur.fetchone()
        if clima:
            print(f"    📍 Coords: {clima['latitud']}, {clima['longitud']}")
        else:
            print(f"    ❌ No entry in tbl_clima")

    cur.close()
    conn.close()

if __name__ == "__main__":
    debug_user_prefs(1)

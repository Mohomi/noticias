from conecta import obtener_conexion

def migrate_clima_ids():
    print("🔄 Migrating tbl_clima IDs to match preferences format (com-{id})...")
    conn = obtener_conexion()
    cur = conn.cursor(dictionary=True)
    
    # Mapping of slug to ID based on tbl_comunas
    # We need to fetch all comunas to build the map
    cur.execute("SELECT id_comuna, nombre FROM tbl_comunas")
    comunas = cur.fetchall()
    
    # Create a map of normalized name -> id
    # e.g. "providencia" -> 316
    name_to_id = {}
    for c in comunas:
        normalized = c['nombre'].lower().replace(' ', '-').replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u').replace('ñ','n')
        name_to_id[normalized] = c['id_comuna']
        
    # Also add specific hardcoded mappings for what we inserted in actualizar_tabla_clima.py
    # ('com-punitaqui', ...), ('com-providencia', ...), etc.
    
    # Let's see what's in tbl_clima
    cur.execute("SELECT id_ubicacion FROM tbl_clima WHERE id_ubicacion LIKE 'com-%'")
    clima_entries = cur.fetchall()
    
    print(f"Found {len(clima_entries)} entries in tbl_clima to potentially update.")
    
    updated_count = 0
    for entry in clima_entries:
        old_id = entry['id_ubicacion']
        # Extract name part: com-providencia -> providencia
        name_part = old_id.replace('com-', '')
        
        # Try to find ID
        new_id_num = name_to_id.get(name_part)
        
        # Special cases if simple normalization fails
        if not new_id_num:
            if name_part == 'santiago': new_id_num = 308 # Santiago
            elif name_part == 'valparaiso': new_id_num = 56 # Valparaiso
            elif name_part == 'concepcion': new_id_num = 162 # Concepcion
            elif name_part == 'la-serena': new_id_num = 31 # La Serena
            elif name_part == 'antofagasta': new_id_num = 9 # Antofagasta
            elif name_part == 'temuco': new_id_num = 237 # Temuco
            elif name_part == 'puerto-montt': new_id_num = 265 # Puerto Montt
            elif name_part == 'punta-arenas': new_id_num = 301 # Punta Arenas
            elif name_part == 'punitaqui': new_id_num = 40 # Punitaqui
            
        if new_id_num:
            new_id = f"com-{new_id_num}"
            print(f"  Mapping {old_id} -> {new_id}")
            
            try:
                # Check if new ID already exists
                cur.execute("SELECT id_ubicacion FROM tbl_clima WHERE id_ubicacion = %s", (new_id,))
                if cur.fetchone():
                    print(f"    ⚠️ {new_id} already exists, deleting old {old_id}")
                    cur.execute("DELETE FROM tbl_clima WHERE id_ubicacion = %s", (old_id,))
                else:
                    # Update ID
                    cur.execute("UPDATE tbl_clima SET id_ubicacion = %s WHERE id_ubicacion = %s", (new_id, old_id))
                    updated_count += 1
            except Exception as e:
                print(f"    ❌ Error updating {old_id}: {e}")
        else:
            print(f"  ⚠️ Could not find ID for {old_id}")

    conn.commit()
    print(f"✅ Updated {updated_count} entries.")
    cur.close()
    conn.close()

if __name__ == "__main__":
    migrate_clima_ids()

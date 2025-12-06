import mysql.connector
from conecta import obtener_conexion

def obtener_estructura_geografica():
    """
    Obtiene la estructura jerárquica completa de países, regiones, provincias y comunas.
    
    Returns:
        dict: Estructura jerárquica en formato compatible con el componente de ubicaciones
    """
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        
        # 1. Obtener todos los países
        cursor.execute("SELECT id, nombre FROM tbl_paises")
        paises = cursor.fetchall()
        
        estructura = []
        
        for pais in paises:
            # Construir ID del país (ej: "cl" para Chile)
            pais_id = f"pais-{pais['id']}"
            
            pais_node = {
                'id': pais_id,
                'label': pais['nombre'],
                'type': 'country',
                'children': []
            }
            
            # 2. Obtener regiones del país
            cursor.execute("""
                SELECT id, nombre, abreviatura 
                FROM tbl_regiones 
                WHERE pais_id = %s
                ORDER BY orden_region
            """, (pais['id'],))
            regiones = cursor.fetchall()
            
            for region in regiones:
                # Construir ID de región (ej: "reg-coquimbo")
                region_id = f"reg-{region['abreviatura'].lower()}" if region['abreviatura'] else f"reg-{region['id']}"
                
                region_node = {
                    'id': region_id,
                    'label': region['nombre'],
                    'type': 'region',
                    'children': []
                }
                
                # 3. Obtener provincias de la región
                cursor.execute("""
                    SELECT id, nombre
                    FROM tbl_provincias
                    WHERE region_id = %s
                    ORDER BY nombre
                """, (region['id'],))
                provincias = cursor.fetchall()
                
                for provincia in provincias:
                    # Construir ID de provincia (ej: "prov-elqui")
                    provincia_id = f"prov-{provincia['id']}"
                    
                    provincia_node = {
                        'id': provincia_id,
                        'label': provincia['nombre'],
                        'type': 'province',
                        'children': []
                    }
                    
                    # 4. Obtener comunas de la provincia
                    cursor.execute("""
                        SELECT id_comuna, nombre
                        FROM tbl_comunas
                        WHERE provincia_id = %s
                        ORDER BY nombre
                    """, (provincia['id'],))
                    comunas = cursor.fetchall()
                    
                    for comuna in comunas:
                        # Construir ID de comuna (ej: "com-punitaqui")
                        comuna_id = f"com-{comuna['id_comuna']}"
                        
                        comuna_node = {
                            'id': comuna_id,
                            'label': comuna['nombre'],
                            'type': 'commune'
                        }
                        
                        provincia_node['children'].append(comuna_node)
                    
                    region_node['children'].append(provincia_node)
                
                pais_node['children'].append(region_node)
            
            estructura.append(pais_node)
        
        # Si solo hay un país, retornar ese país directamente
        if len(estructura) == 1:
            result = estructura[0]
        else:
            result = {'id': 'root', 'label': 'Países', 'type': 'root', 'children': estructura}
        
        print(f"✅ Estructura geográfica generada: {len(paises)} país(es)")
        return result
        
    except mysql.connector.Error as error:
        print(f"❌ Error BD al obtener estructura geográfica: {error}")
        return {'id': 'error', 'label': 'Error cargando datos', 'type': 'error', 'children': []}
    except Exception as e:
        print(f"❌ Error inesperado al obtener estructura geográfica: {e}")
        import traceback
        traceback.print_exc()
        return {'id': 'error', 'label': 'Error cargando datos', 'type': 'error', 'children': []}
    finally:
        if cursor: cursor.close()
        if conexion and conexion.is_connected(): conexion.close()

# Probar la función
if __name__ == "__main__":
    import json
    result = obtener_estructura_geografica()
    print("\n" + "="*60)
    print("ESTRUCTURA GENERADA:")
    print("="*60)
    print(json.dumps(result, indent=2, ensure_ascii=False))

import mysql.connector
from conecta import obtener_conexion

def normalizar_categoria(nombre_categoria_raw):
    """
    Normaliza una categoría usando el mapeo definido en tbl_categoria_mapeo.

    Args:
        nombre_categoria_raw: Nombre de categoría tal como viene del feed RSS

    Returns:
        tuple: (id_categoria_normalizada, nombre_normalizado) o (None, nombre_original) si no hay mapeo
    """
    if not nombre_categoria_raw or not isinstance(nombre_categoria_raw, str):
        return None, nombre_categoria_raw

    nombre_normalizado = nombre_categoria_raw.strip().lower()

    conn = None
    cur = None
    try:
        conn = obtener_conexion()
        cur = conn.cursor(dictionary=True)

        # Buscar si existe un mapeo para este nombre
        query = """
            SELECT cm.id_categoria_real, c.nombre as nombre_real
            FROM tbl_categoria_mapeo cm
            INNER JOIN tbl_categoria c ON cm.id_categoria_real = c.id_categoria
            WHERE LOWER(cm.nombre_alternativo) = %s
        """
        cur.execute(query, (nombre_normalizado,))
        mapeo = cur.fetchone()

        if mapeo:
            # Categoria Normalizada y mapeada
            # print(f"    🔄 Categoría '{nombre_categoria_raw}' mapeada a '{mapeo['nombre_real']}' (ID: {mapeo['id_categoria_real']})")
            return mapeo['id_categoria_real'], mapeo['nombre_real']
        else:
            # No hay mapeo, devolver el nombre original sin normalizar
            return None, nombre_categoria_raw

    except mysql.connector.Error as err:
        print(f"    ❌ Error al normalizar categoría '{nombre_categoria_raw}': {err}")
        return None, nombre_categoria_raw
    finally:
        if cur:
            cur.close()
        if conn and conn.is_connected():
            conn.close()

def obtener_mapeos_categoria():
    """
    Obtiene todos los mapeos de categorías para mostrar en administración.

    Returns:
        list: Lista de diccionarios con los mapeos
    """
    conn = None
    cur = None
    try:
        conn = obtener_conexion()
        cur = conn.cursor(dictionary=True)

        query = """
            SELECT
                cm.id_mapeo,
                cm.nombre_alternativo,
                cm.id_categoria_real,
                c.nombre as nombre_categoria_real,
                cm.fecha_creacion
            FROM tbl_categoria_mapeo cm
            INNER JOIN tbl_categoria c ON cm.id_categoria_real = c.id_categoria
            ORDER BY c.nombre, cm.nombre_alternativo
        """
        cur.execute(query)
        return cur.fetchall()

    except mysql.connector.Error as err:
        print(f"❌ Error al obtener mapeos de categoría: {err}")
        return []
    finally:
        if cur:
            cur.close()
        if conn and conn.is_connected():
            conn.close()

def agregar_mapeo_categoria(nombre_alternativo, id_categoria_real):
    """
    Agrega un nuevo mapeo de categoría.

    Args:
        nombre_alternativo: Nombre alternativo a mapear
        id_categoria_real: ID de la categoría real

    Returns:
        dict: Resultado de la operación
    """
    conn = None
    cur = None
    try:
        conn = obtener_conexion()
        cur = conn.cursor()

        # Verificar que la categoría real existe
        cur.execute("SELECT nombre FROM tbl_categoria WHERE id_categoria = %s", (id_categoria_real,))
        categoria_real = cur.fetchone()

        if not categoria_real:
            return {'success': False, 'message': f'Categoría real con ID {id_categoria_real} no existe'}

        # Insertar el mapeo
        query = """
            INSERT INTO tbl_categoria_mapeo (nombre_alternativo, id_categoria_real)
            VALUES (%s, %s)
        """
        cur.execute(query, (nombre_alternativo.strip().lower(), id_categoria_real))
        conn.commit()

        print(f"✅ Mapeo agregado: '{nombre_alternativo}' -> '{categoria_real[0]}'")
        return {'success': True, 'message': f'Mapeo agregado exitosamente'}

    except mysql.connector.IntegrityError as err:
        if 'duplicate' in str(err).lower():
            return {'success': False, 'message': f'El nombre alternativo "{nombre_alternativo}" ya existe'}
        return {'success': False, 'message': f'Error de integridad: {err}'}
    except mysql.connector.Error as err:
        print(f"❌ Error al agregar mapeo: {err}")
        return {'success': False, 'message': str(err)}
    finally:
        if cur:
            cur.close()
        if conn and conn.is_connected():
            conn.close()

def eliminar_mapeo_categoria(id_mapeo):
    """
    Elimina un mapeo de categoría.

    Args:
        id_mapeo: ID del mapeo a eliminar

    Returns:
        dict: Resultado de la operación
    """
    conn = None
    cur = None
    try:
        conn = obtener_conexion()
        cur = conn.cursor()

        query = "DELETE FROM tbl_categoria_mapeo WHERE id_mapeo = %s"
        cur.execute(query, (id_mapeo,))
        conn.commit()

        if cur.rowcount > 0:
            print(f"✅ Mapeo {id_mapeo} eliminado")
            return {'success': True, 'message': 'Mapeo eliminado exitosamente'}
        else:
            return {'success': False, 'message': 'Mapeo no encontrado'}

    except mysql.connector.Error as err:
        print(f"❌ Error al eliminar mapeo: {err}")
        return {'success': False, 'message': str(err)}
    finally:
        if cur:
            cur.close()
        if conn and conn.is_connected():
            conn.close()

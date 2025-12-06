#!/usr/bin/env python3
"""
Script para configurar la tabla de mapeo de categorías.
Ejecuta el SQL necesario para crear la tabla y poblarla con datos iniciales.
"""

import mysql.connector
from conecta import obtener_conexion

def ejecutar_sql(sql):
    """Ejecuta una consulta SQL."""
    conn = None
    cur = None
    try:
        conn = obtener_conexion()
        cur = conn.cursor()

        # Ejecutar múltiples statements
        statements = [stmt.strip() for stmt in sql.split(';') if stmt.strip()]

        for statement in statements:
            if statement:
                print(f"🔍 Ejecutando: {statement[:50]}...")
                cur.execute(statement)

        conn.commit()
        print("✅ SQL ejecutado exitosamente")

    except mysql.connector.Error as err:
        print(f"❌ Error ejecutando SQL: {err}")
        if conn:
            conn.rollback()
        raise
    finally:
        if cur:
            cur.close()
        if conn and conn.is_connected():
            conn.close()

def main():
    print("🚀 Configurando tabla de mapeo de categorías...")

    # SQL para crear la tabla
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS tbl_categoria_mapeo (
        id_mapeo BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
        nombre_alternativo VARCHAR(100) NOT NULL UNIQUE,
        id_categoria_real BIGINT UNSIGNED NOT NULL,
        fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY (id_categoria_real) REFERENCES tbl_categoria(id_categoria)
            ON DELETE CASCADE ON UPDATE CASCADE,

        INDEX idx_nombre_alternativo (nombre_alternativo),
        INDEX idx_categoria_real (id_categoria_real)
    );
    """

    # Ejecutar creación de tabla
    ejecutar_sql(create_table_sql)

    # Verificar categorías existentes para saber cuáles IDs usar
    try:
        conn = obtener_conexion()
        cur = conn.cursor(dictionary=True)

        cur.execute("SELECT id_categoria, nombre FROM tbl_categoria ORDER BY id_categoria")
        categorias = cur.fetchall()

        print("📋 Categorías existentes:")
        for cat in categorias:
            print(f"  {cat['id_categoria']}: {cat['nombre']}")

        # Crear mapeos basados en categorías existentes
        # Buscar categorías similares por nombre
        mapeos = []

        for cat in categorias:
            cat_id = cat['id_categoria']
            cat_nombre = cat['nombre'].lower()

            # Nacional
            if 'nacional' in cat_nombre or 'país' in cat_nombre or 'local' in cat_nombre:
                mapeos.extend([
                    ('nacional', cat_id),
                    ('país', cat_id),
                    ('pais', cat_id),
                    ('local', cat_id)
                ])

            # Internacional
            if 'internacional' in cat_nombre or 'mundo' in cat_nombre or 'global' in cat_nombre:
                mapeos.extend([
                    ('internacional', cat_id),
                    ('mundo', cat_id),
                    ('global', cat_id),
                    ('world', cat_id)
                ])

            # Política
            if 'política' in cat_nombre or 'politics' in cat_nombre:
                mapeos.extend([
                    ('política', cat_id),
                    ('politica', cat_id),
                    ('politics', cat_id)
                ])

            # Economía
            if 'economía' in cat_nombre or 'economia' in cat_nombre or 'business' in cat_nombre:
                mapeos.extend([
                    ('economía', cat_id),
                    ('economia', cat_id),
                    ('business', cat_id),
                    ('negocios', cat_id)
                ])

            # Deportes
            if 'deportes' in cat_nombre or 'sports' in cat_nombre:
                mapeos.extend([
                    ('deportes', cat_id),
                    ('sports', cat_id),
                    ('deportivo', cat_id)
                ])

            # Tecnología
            if 'tecnología' in cat_nombre or 'tecnologia' in cat_nombre or 'tech' in cat_nombre:
                mapeos.extend([
                    ('tecnología', cat_id),
                    ('tecnologia', cat_id),
                    ('tech', cat_id),
                    ('ciencia', cat_id),
                    ('science', cat_id)
                ])

        # Insertar mapeos
        if mapeos:
            print(f"🔄 Insertando {len(mapeos)} mapeos de categorías...")
            cur.executemany(
                "INSERT IGNORE INTO tbl_categoria_mapeo (nombre_alternativo, id_categoria_real) VALUES (%s, %s)",
                mapeos
            )
            conn.commit()
            print("✅ Mapeos insertados exitosamente")
        else:
            print("⚠️ No se encontraron categorías para mapear automáticamente")

        cur.close()
        conn.close()

    except mysql.connector.Error as err:
        print(f"❌ Error configurando mapeos: {err}")
        return

    print("🎉 Configuración completada exitosamente!")

if __name__ == "__main__":
    main()

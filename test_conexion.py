"""
Script para probar la conexión a la base de datos
Ejecutar: python test_conexion.py
"""
from conecta import conectar_base_datos

if __name__ == "__main__":
    print("=" * 50)
    print("🧪 PRUEBA DE CONEXIÓN A LA BASE DE DATOS")
    print("=" * 50)
    
    resultados = conectar_base_datos()
    
    print("\n" + "=" * 50)
    print(f"📊 Total de registros obtenidos: {len(resultados)}")
    print("=" * 50)
    
    if len(resultados) > 0:
        print("\n✅ Conexión exitosa! Registros encontrados:\n")
        for i, registro in enumerate(resultados, 1):
            print(f"{i}. ID: {registro.get('id_fuente')}, Nombre: {registro.get('nombre')}, Descripción: {registro.get('descripcion')}")
    else:
        print("\n⚠️ No se obtuvieron registros. Verifica:")
        print("  1. Que la tabla tbl_fuente exista en la base de datos")
        print("  2. Que la conexión a la base de datos sea correcta")
        print("  3. Que el archivo connect.env tenga la configuración correcta")


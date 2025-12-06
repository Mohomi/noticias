"""
Script para verificar que todas las dependencias estén instaladas
y que la API Flask pueda iniciar correctamente
"""
import sys

print("=" * 60)
print("🔍 VERIFICACIÓN DE DEPENDENCIAS PARA LA API FLASK")
print("=" * 60)
print()

# Verificar Python
print(f"✅ Python versión: {sys.version}")
print()

# Verificar Flask
try:
    import flask
    print(f"✅ Flask instalado: versión {flask.__version__}")
except ImportError:
    print("❌ Flask NO está instalado")
    print("   Instala con: pip install flask")
    sys.exit(1)

# Verificar flask-cors
try:
    import flask_cors
    print(f"✅ Flask-CORS instalado: versión {flask_cors.__version__}")
except ImportError:
    print("❌ Flask-CORS NO está instalado")
    print("   Instala con: pip install flask-cors")
    sys.exit(1)

# Verificar mysql-connector
try:
    import mysql.connector
    print(f"✅ MySQL Connector instalado")
except ImportError:
    print("❌ MySQL Connector NO está instalado")
    print("   Instala con: pip install mysql-connector-python")
    sys.exit(1)

# Verificar dotenv
try:
    import dotenv
    print(f"✅ Python-dotenv instalado")
except ImportError:
    print("❌ Python-dotenv NO está instalado")
    print("   Instala con: pip install python-dotenv")
    sys.exit(1)

print()
print("=" * 60)
print("🔍 VERIFICANDO IMPORTS DE LA API")
print("=" * 60)
print()

# Intentar importar conecta
try:
    from conecta import conectar_base_datos, registrar_usuario, ingresar_usuario
    print("✅ Módulo conecta.py importado correctamente")
except ImportError as e:
    print(f"❌ Error al importar conecta.py: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error inesperado al importar conecta.py: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Intentar importar api
try:
    print("✅ Intentando importar api.py...")
    import api
    print("✅ api.py importado correctamente")
except ImportError as e:
    print(f"❌ Error al importar api.py: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error inesperado al importar api.py: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("=" * 60)
print("✅ TODAS LAS VERIFICACIONES PASARON")
print("=" * 60)
print()
print("🚀 Ahora puedes ejecutar: python api.py")
print()


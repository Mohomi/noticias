# Instrucciones para ejecutar la API de Python

## Prerrequisitos

1. Python 3.7 o superior instalado
2. Acceso a la base de datos MySQL configurada en `connect.env`

## Instalación de dependencias

Instala las dependencias de Python necesarias:

```bash
pip install -r requirements.txt
```

## Ejecutar la API

Para iniciar el servidor Flask que expone los datos de `tbl_fuente`:

```bash
python api.py
```

La API estará disponible en `http://localhost:5000`

## Endpoints disponibles

- `GET http://localhost:5000/api/fuentes` - Obtiene todas las fuentes de la tabla `tbl_fuente`

## Ejecutar la aplicación React

En una terminal separada, ejecuta:

```bash
npm run dev
```

La aplicación React ahora obtendrá los datos de la base de datos a través de la API Python en lugar de usar las constantes mock.

**Nota:** Si la API no está disponible o hay un error de conexión, la aplicación React usará los datos mock como respaldo.



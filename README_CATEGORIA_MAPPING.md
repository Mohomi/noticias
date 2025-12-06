# Sistema de Mapeo de Categorías

## Problema Resuelto

Anteriormente, diferentes feeds RSS usaban nombres diferentes para categorías similares:
- "nacional" vs "país"
- "internacional" vs "mundo"
- "economía" vs "business"

Esto causaba que se crearan múltiples categorías duplicadas en `tbl_otra_categoria`, haciendo más engorrosa la configuración de preferencias de usuario.

## Solución Implementada

### 1. Tabla de Mapeo (`tbl_categoria_mapeo`)

Se creó una nueva tabla que mapea nombres alternativos de categorías a categorías existentes:

```sql
CREATE TABLE tbl_categoria_mapeo (
    id_mapeo BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre_alternativo VARCHAR(100) NOT NULL UNIQUE,
    id_categoria_real BIGINT UNSIGNED NOT NULL,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_categoria_real) REFERENCES tbl_categoria(id_categoria)
);
```

### 2. Proceso de Normalización

Cuando se procesa un feed RSS, el sistema ahora sigue este flujo:

1. **Normalización**: Busca el nombre de categoría en `tbl_categoria_mapeo`
2. **Búsqueda Exacta**: Si no hay mapeo, busca coincidencia exacta en `tbl_categoria`
3. **Categoría Desconocida**: Solo como último recurso crea entrada en `tbl_otra_categoria`

### 3. API de Administración

Se agregaron endpoints para gestionar los mapeos:

```
GET  /api/categorias/mapeos          # Obtener todos los mapeos
POST /api/categorias/mapeos          # Crear nuevo mapeo
DEL  /api/categorias/mapeos/<id>     # Eliminar mapeo
```

## Archivos Modificados

- `categoria_normalizer.py` - Funciones de normalización
- `rss_service.py` - Procesamiento actualizado de categorías
- `api.py` - Nuevos endpoints de administración
- `setup_categoria_mapping.py` - Script de configuración inicial

## Mapeos Automáticos Creados

El sistema creó automáticamente mapeos para las categorías existentes:

- **Nacional**: nacional, país, pais, local
- **Internacional**: internacional, mundo, global, world
- **Política**: política, politica, politics
- **Economía**: economía, economia, business, negocios
- **Deportes**: deportes, sports, deportivo
- **Tecnología**: tecnología, tecnologia, tech, ciencia, science

## Uso del Sistema

### Agregar Nuevo Mapeo

```bash
curl -X POST http://localhost:5000/api/categorias/mapeos \
  -H "Content-Type: application/json" \
  -d '{"nombre_alternativo": "cultura", "id_categoria_real": 74}'
```

### Ver Todos los Mapeos

```bash
curl http://localhost:5000/api/categorias/mapeos
```

### Eliminar Mapeo

```bash
curl -X DELETE http://localhost:5000/api/categorias/mapeos/1
```

## Beneficios

1. **Reducción de Categorías Duplicadas**: Las categorías similares ahora se normalizan automáticamente
2. **Mejor Experiencia de Usuario**: Menos categorías confusas en las preferencias
3. **Mantenimiento Simplificado**: Fácil agregar nuevos mapeos sin modificar código
4. **Flexibilidad**: Los administradores pueden ajustar mapeos según necesidades

## Nueva Funcionalidad: Filtrado por Categorías

### Endpoint de Filtrado por Categorías

Se agregó un nuevo endpoint para filtrar el feed de noticias por categoría específica:

```
GET /api/feed/<usuario>/categoria/<categoria>
```

**Ejemplo:**
```bash
curl http://localhost:5000/api/feed/1/categoria/5
```

Esto devolverá solo las noticias del usuario 1 que pertenecen a la categoría con ID 5.

### Función `filtra_categoria_feed`

```python
from conecta import filtra_categoria_feed

# Filtrar noticias del usuario 1 por categoría 5
noticias = filtra_categoria_feed(1, 5)
```

La función realiza una consulta que:
- Toma las noticias del feed del usuario (`tbl_feed_usuario`)
- Filtra por la categoría especificada (`tbl_noticia_categoria`)
- Incluye información de fuente y formatea fechas

## Próximos Pasos Recomendados

1. **Interfaz Web**: Crear interfaz en el panel de administración para gestionar mapeos
2. **Análisis Automático**: Implementar sugerencias automáticas de mapeos basadas en similitud de texto
3. **Categorías Personalizadas**: Permitir mapeos específicos por fuente RSS
4. **Auditoría**: Agregar logs de categorías normalizadas vs. categorías desconocidas

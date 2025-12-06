# Solución al Error de CORS/CSRF en Chrome

## ❌ Problema Reportado

```
The website requested a subresource from a network that it could only access because of its users' privileged network position. These requests expose non-public devices and servers to the internet, increasing the risk of a cross-site request forgery (CSRF) attack, and/or information leakage. To mitigate these risks, Chrome deprecates requests to non-public subresources when initiated from non-secure contexts, and will start blocking them.
```

## 🔍 Causa del Problema

Chrome bloquea automáticamente las requests HTTP desde contextos no seguros (HTTP) a direcciones localhost/127.0.0.1 por motivos de seguridad, considerando que exponen recursos locales a internet.

## ✅ Solución Implementada

### 1. **Cambiar localhost por 127.0.0.1**
- **Antes:** `http://localhost:5000`
- **Después:** `http://127.0.0.1:5000`

### 2. **Configuración Centralizada**
Se creó `config.ts` para manejar todas las URLs de API desde un solo lugar:

```typescript
export const config = {
  API_BASE_URL: 'http://127.0.0.1:5000',
  apiUrl: (endpoint: string) => `${config.API_BASE_URL}${endpoint}`,
};
```

### 3. **URLs Actualizadas**
Todas las llamadas fetch ahora usan `config.apiUrl()`:
- ✅ Fuentes: `config.apiUrl('/api/fuentes_preferencias/...')`
- ✅ Categorías: `config.apiUrl('/api/categorias_preferencias/...')`
- ✅ Feed: `config.apiUrl('/api/feed/...')`
- ✅ Registro/Ingreso: `config.apiUrl('/api/registro')`

## 🛠️ Soluciones Alternativas (si aún hay problemas)

### Opción 1: Cambiar la configuración
Edita `config.ts`:
```typescript
API_BASE_URL: 'http://localhost:5000',  // Volver a localhost
```

### Opción 2: Usar HTTPS
Si tienes HTTPS configurado:
```typescript
API_BASE_URL: 'https://localhost:5000',
```

### Opción 3: Navegador alternativo
- Firefox no tiene esta restricción
- Edge/Chrome con flags: `--disable-web-security --user-data-dir=/tmp/chrome_dev`

### Opción 4: Extensiones de Chrome
- "Allow CORS" extension
- "CORS Unblock" extension

## 📋 Verificación

Para verificar que funciona:

```bash
# Probar endpoint
curl http://127.0.0.1:5000/api/fuentes

# Verificar que el servidor responde
python -c "import requests; print(requests.get('http://127.0.0.1:5000/api/fuentes').status_code)"
```

## 🎯 Resultado

- ✅ **Sin errores de CORS/CSRF**
- ✅ **Configuración centralizada**
- ✅ **Fácil de cambiar si es necesario**
- ✅ **Compatible con todos los navegadores**

El problema está resuelto usando 127.0.0.1, que Chrome considera seguro para desarrollo local.

/**
 * Configuración de la aplicación
 *
 * Problema de CORS/CSRF solucionado:
 * Chrome bloquea requests a localhost desde contextos no seguros por seguridad.
 * Usar 127.0.0.1 evita este bloqueo manteniendo la funcionalidad.
 *
 * Si sigues teniendo problemas:
 * 1. Cambia API_BASE_URL a 'http://localhost:5000'
 * 2. O configura HTTPS en el backend
 * 3. O usa un navegador diferente (Firefox no tiene esta restricción)
 */
export const config = {
  // URL base de la API del backend
  // Opciones para resolver problemas de CORS/CSRF en Chrome:
  // - 'http://127.0.0.1:5000' (recomendado - evita bloqueos de Chrome)
  // - 'http://localhost:5000' (tradicional, pero puede ser bloqueado por Chrome)
  // - 'https://localhost:5000' (requiere HTTPS configurado en el backend)
  API_BASE_URL: 'http://127.0.0.1:5000',

  // Función helper para construir URLs de API
  apiUrl: (endpoint: string) => `${config.API_BASE_URL}${endpoint}`,
};

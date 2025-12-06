import { Tbl_Fuente, Tbl_Preferencia_Fuente, TblCategoria, Tbl_Preferenciacategoria } from './types';

// URL base de la API
export const API_BASE_URL = 'http://localhost:5000/api';

// ID de fuente genérica para usuarios sin preferencias
// Se usa para mostrar noticias por defecto si el usuario no configura nada.
// Actualmente configurado a 9.
// TODO: Cambiar este ID si la fuente genérica cambia en la base de datos.
// TODO: Implementar lógica de ordenamiento por fecha (id_noticia DESC) en la consulta SQL correspondiente.
export const ID_GENERICO = 9;

// --- FUNCIONES DE API ---

/**
 * Obtiene las fuentes desde la API de Python
 */
export async function obtenerFuentesDesdeBD(): Promise<Tbl_Fuente[]> {
  try {
    console.log(`🔍 Intentando conectar con la API en ${API_BASE_URL}/fuentes...`);
    const response = await fetch(`${API_BASE_URL}/fuentes`);

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`❌ Error HTTP ${response.status}: ${errorText}`);
      throw new Error(`Error al obtener fuentes: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    console.log(`✅ Datos obtenidos de la API: ${data.length} fuentes`, data);

    if (Array.isArray(data) && data.length > 0) {
      return data as Tbl_Fuente[];
    } else {
      console.warn('⚠️ La API retornó un array vacío o datos inválidos');
      return [];
    }
  } catch (error) {
    console.error('❌ Error al obtener fuentes desde la base de datos:', error);
    console.error('💡 Asegúrate de que la API Flask esté corriendo en http://localhost:5000');
    // Retornar array vacío para que use los datos mock como respaldo
    return [];
  }
}

/**
 * Obtiene las categorías desde la API de Python
 */
export async function obtenerCategoriasDesdeBD(): Promise<TblCategoria[]> {
  try {
    console.log('🔍 Intentando conectar con la API en http://localhost:5000/api/categorias...');
    const response = await fetch('http://localhost:5000/api/categorias');

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`❌ Error HTTP ${response.status}: ${errorText}`);
      throw new Error(`Error al obtener categorías: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    console.log(`✅ Datos obtenidos de la API: ${data.length} categorías`, data);

    if (Array.isArray(data) && data.length > 0) {
      return data as TblCategoria[];
    } else {
      console.warn('⚠️ La API retornó un array vacío o datos inválidos para categorías');
      return [];
    }
  } catch (error) {
    console.error('❌ Error al obtener categorías desde la base de datos:', error);
    return [];
  }
}

// Mantener datos mock como respaldo

export const MOCK_TBL_FUENTES: Tbl_Fuente[] = [
  { id_fuente: 1, nombre: 'EEEEE EEEEE', descripcion: 'Diario El País' },
  { id_fuente: 2, nombre: 'E Mundo', descripcion: 'Diario El Mundo' },
  { id_fuente: 3, nombre: 'La Vanguardia', descripcion: 'Diario La Vanguardia' },
  { id_fuente: 4, nombre: 'ABC', descripcion: 'Diario ABC' },
  { id_fuente: 5, nombre: 'E EEE EEE', descripcion: 'Diario El Confidencial' },
  { id_fuente: 6, nombre: '20  ', descripcion: 'Diario 20 Minutos' },
  { id_fuente: 7, nombre: 'ario', descripcion: 'El Diario.es' },
];

export const MOCK_TBL_CATEGORIAS: TblCategoria[] = [
  { id_categoria: 1, id_categoria_padre: 0, nombre: 'olítica' },
  { id_categoria: 2, id_categoria_padre: 0, nombre: 'conomía' },
  { id_categoria: 3, id_categoria_padre: 0, nombre: 'eportes' },
  { id_categoria: 4, id_categoria_padre: 0, nombre: 'ultura' },
  { id_categoria: 5, id_categoria_padre: 0, nombre: 'ecnología' },
  { id_categoria: 6, id_categoria_padre: 0, nombre: 'ociedad' },

  // Subcategorias Deportes (id 3)
  { id_categoria: 11, id_categoria_padre: 3, nombre: 'útbol' },
  { id_categoria: 12, id_categoria_padre: 3, nombre: 'aloncesto' },
  { id_categoria: 13, id_categoria_padre: 3, nombre: 'enis' },

  // Sub-subcategorias Tenis (id 13)
  { id_categoria: 131, id_categoria_padre: 13, nombre: 'TP' },
  { id_categoria: 132, id_categoria_padre: 13, nombre: 'TA' },

  // Subcategorias Sociedad (id 6)
  { id_categoria: 61, id_categoria_padre: 6, nombre: 'ucesos' },
  { id_categoria: 62, id_categoria_padre: 6, nombre: 'ducación' },
];

export const MOCK_TBL_PREF_FUENTES: Tbl_Preferencia_Fuente[] = [
  { id_preferencia: 101, id_fuente: 1, prioridad: 1, preferencias_fuentes_on_off: true },
  { id_preferencia: 102, id_fuente: 2, prioridad: 2, preferencias_fuentes_on_off: true },
  { id_preferencia: 103, id_fuente: 3, prioridad: 3, preferencias_fuentes_on_off: false },
  { id_preferencia: 104, id_fuente: 4, prioridad: 4, preferencias_fuentes_on_off: true },
  { id_preferencia: 105, id_fuente: 5, prioridad: 5, preferencias_fuentes_on_off: false },
  { id_preferencia: 106, id_fuente: 6, prioridad: 6, preferencias_fuentes_on_off: true },
  { id_preferencia: 107, id_fuente: 7, prioridad: 7, preferencias_fuentes_on_off: false },
];

export const MOCK_TBL_PREF_CAT: Tbl_Preferenciacategoria[] = [
  { id_preferencia_cat: 201, id_categoria: 1, prioridad: 1, orden: 1, preferencia_categoria_on_off: true },
  { id_preferencia_cat: 202, id_categoria: 2, prioridad: 2, orden: 2, preferencia_categoria_on_off: true },
  { id_preferencia_cat: 203, id_categoria: 3, prioridad: 3, orden: 3, preferencia_categoria_on_off: false },
  { id_preferencia_cat: 204, id_categoria: 4, prioridad: 4, orden: 4, preferencia_categoria_on_off: true },
  { id_preferencia_cat: 205, id_categoria: 5, prioridad: 5, orden: 5, preferencia_categoria_on_off: true },
  { id_preferencia_cat: 206, id_categoria: 6, prioridad: 6, orden: 6, preferencia_categoria_on_off: true },

  // Prefs subcategorias
  { id_preferencia_cat: 211, id_categoria: 11, prioridad: 1, orden: 1, preferencia_categoria_on_off: true },
  { id_preferencia_cat: 212, id_categoria: 12, prioridad: 2, orden: 2, preferencia_categoria_on_off: true },
  { id_preferencia_cat: 213, id_categoria: 13, prioridad: 3, orden: 3, preferencia_categoria_on_off: true },
  { id_preferencia_cat: 214, id_categoria: 131, prioridad: 1, orden: 1, preferencia_categoria_on_off: true },
  { id_preferencia_cat: 215, id_categoria: 132, prioridad: 2, orden: 2, preferencia_categoria_on_off: true },
  { id_preferencia_cat: 216, id_categoria: 61, prioridad: 1, orden: 1, preferencia_categoria_on_off: true },
  { id_preferencia_cat: 217, id_categoria: 62, prioridad: 2, orden: 2, preferencia_categoria_on_off: false },
];

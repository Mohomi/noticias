// Simulación de estructura de Base de Datos

export interface Tbl_Fuente {
  id_fuente: number;
  nombre: string;
  descripcion: string;
}

export interface Tbl_Preferencia_Fuente {
  id_preferencia: number;
  id_fuente: number;
  prioridad: number;
  preferencias_fuentes_on_off: boolean;
}

export interface TblCategoria {
  id_categoria: number;
  id_categoria_padre: number; // 0 si es raiz
  nombre: string;
}

export interface Tbl_Preferenciacategoria {
  id_preferencia_cat: number;
  id_categoria: number;
  prioridad: number;
  preferencia_categoria_on_off: boolean;
  orden: number; // En este caso, usaremos orden y prioridad como conceptos similares para el UI
}

// Tipos combinados para la vista (simulando un JOIN SQL)
export interface FuenteView extends Tbl_Fuente, Tbl_Preferencia_Fuente { }
export interface CategoriaView extends TblCategoria, Tbl_Preferenciacategoria { }

// Tipos para Google Calendar
export interface CalendarEvent {
  id: string;
  summary: string;
  description?: string;
  location?: string;
  start: {
    dateTime?: string;
    date?: string;
  };
  end: {
    dateTime?: string;
    date?: string;
  };
}

export interface FormattedEvent {
  date: string;
  time: string;
  title: string;
  location: string;
  notes: string;
  raw: CalendarEvent;
}

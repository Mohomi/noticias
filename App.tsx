import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Settings2, LayoutDashboard, Rss, Hash, Volume2, X, MapPin } from 'lucide-react';
import { PreferencesModal } from './components/PreferencesModal';
import { AdminPanel } from './components/AdminPanel';
import { ReadingAssistant } from './tts/components/ReadingAssistant';
import { ttsService } from './tts/services/ttsService';
import LocationsMenu from './menu_ubicaciones/App';
import { config } from './config';
import { FormattedEvent } from './types';
import { initializeGoogleApi, initTokenClient, triggerLogin, listUpcomingEvents, formatEventCivil, eventsToCSV } from './calendarService';

// Funciones auxiliares para formatear agenda (globales)
function getDiaSemana(fechaStr: string): string {
  const [dia, mes, anio] = fechaStr.split('/');
  const fecha = new Date(parseInt(anio), parseInt(mes) - 1, parseInt(dia));
  const dias = ['domingo', 'lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado'];
  return dias[fecha.getDay()];
}

function getMes(fechaStr: string): string {
  const [dia, mes, anio] = fechaStr.split('/');
  const fecha = new Date(parseInt(anio), parseInt(mes) - 1, parseInt(dia));
  const meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];
  return meses[fecha.getMonth()];
}

function getDiaNumero(fechaStr: string): number {
  const [dia] = fechaStr.split('/');
  return parseInt(dia);
}

function parseHoraMinutos(horaStr: string): { horas: number, minutos: number } | null {
  if (horaStr === 'Todo el día') return null;
  const [horas, minutos] = horaStr.split(':').map(n => parseInt(n));
  return { horas, minutos };
}

// Función para generar texto de agenda (global)
function genera_texto_agenda(events: FormattedEvent[]): string {
  if (!events || events.length === 0) return '';

  let sentences: string[] = [];
  let lastDate = '';

  for (const event of events) {
    let sentence = '';

    if (event.date !== lastDate) {
      lastDate = event.date;
      const diaSemana = getDiaSemana(event.date);
      const diaNumero = getDiaNumero(event.date);
      const mes = getMes(event.date);
      sentence += `El ${diaSemana} ${diaNumero} de ${mes}, `;
    }

    const horaMinutos = parseHoraMinutos(event.time);
    let timePart = '';

    if (horaMinutos) {
      if (horaMinutos.minutos === 0) {
        timePart = `a las ${horaMinutos.horas} horas`;
      } else {
        timePart = `a las ${horaMinutos.horas} horas ${horaMinutos.minutos} minutos`;
      }
    } else {
      timePart = 'todo el día';
    }

    if (sentence === '') {
      timePart = timePart.charAt(0).toUpperCase() + timePart.slice(1);
    }

    sentence += `${timePart} tienes agendado ${event.title}`;

    if (event.location && event.location.trim()) {
      sentence += ` en ${event.location}`;
    }

    if (event.notes && event.notes.trim()) {
      sentence += ` me pediste recordar ${event.notes}`;
    }

    sentences.push(sentence);
  }

  return sentences.join('. ');
}


// --- Componentes del Feed ---

const DespliegaIzquierda = ({ userId, onSelectSource, onSelectCategory, onResetFilters, refreshTrigger }: { userId: number | null, onSelectSource: (source: { id: number, name: string } | null) => void, onSelectCategory: (category: { id: number, name: string } | null) => void, onResetFilters: () => void, refreshTrigger?: number }) => {
  const [fuentes, setFuentes] = useState<any[]>([]);
  const [categorias, setCategorias] = useState<any[]>([]);

  useEffect(() => {
    if (!userId) return;

    // Cargar fuentes activas
    fetch(config.apiUrl(`/api/fuentes_preferencias/${userId}`))
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) {
          // Filtrar por esta_suscrito (alias en la query) y asegurar orden por prioridad
          const activas = data.filter((f: any) => f.esta_suscrito === 1);
          setFuentes(activas);
        } else {
          console.error("Formato de fuentes inválido:", data);
          setFuentes([]);
        }
      })
      .catch(err => console.error("Error cargando fuentes:", err));

    // Cargar categorías activas
    fetch(config.apiUrl(`/api/categorias_preferencias/${userId}`))
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) {
          // Filtrar por esta_suscrito (alias en la query)
          const activas = data.filter((c: any) => c.esta_suscrito === 1);
          setCategorias(activas);
        } else {
          console.error("Formato de categorías inválido:", data);
          setCategorias([]);
        }
      })
      .catch(err => console.error("Error cargando categorías:", err));
  }, [userId, refreshTrigger]);

  return (
    <div className="h-full flex flex-col p-4 overflow-y-auto bg-white/50 backdrop-blur-sm">
      <div className="mb-6">
        <h3
          className="font-bold text-slate-800 mb-2 flex items-center gap-2 cursor-pointer hover:text-blue-600 transition-colors"
          onClick={onResetFilters}
          title="Ver todas las noticias"
        >
          <Rss size={18} /> Fuentes Seguidas
        </h3>
        <ul className="space-y-2">
          {fuentes.map(f => (
            <li
              key={f.id_fuente}
              className="flex items-center gap-2 text-sm text-slate-700 bg-white/60 p-2 rounded shadow-sm hover:bg-white/80 transition-colors cursor-pointer hover:ring-2 hover:ring-blue-200"
              onClick={() => onSelectSource({ id: f.id_fuente, name: f.nombre })}
            >
              {f.avatar_url ? (
                <img
                  src={f.avatar_url}
                  alt={f.nombre}
                  className="w-6 h-6 rounded-full object-cover border border-slate-200"
                  onError={(e) => {
                    (e.target as HTMLImageElement).src = 'https://via.placeholder.com/24?text=' + f.nombre.charAt(0);
                  }}
                />
              ) : (
                <div className="w-6 h-6 rounded-full bg-slate-200 flex items-center justify-center text-xs font-bold text-slate-500">
                  {f.nombre.charAt(0)}
                </div>
              )}
              <span className="font-medium">{f.nombre}</span>
            </li>
          ))}
          {fuentes.length === 0 && <li className="text-xs text-slate-500 italic">No sigues ninguna fuente.</li>}
        </ul>
      </div>

      <div>
        <h3 className="font-bold text-slate-800 mb-2 flex items-center gap-2">
          <Hash size={18} /> Categorías
        </h3>
        <ul className="space-y-1">
          {categorias.map(c => (
            <li
              key={c.id_categoria}
              className={`text-sm text-slate-700 bg-white/60 p-2 rounded shadow-sm hover:bg-white/80 transition-colors cursor-pointer hover:ring-2 hover:ring-green-200 ${c.id_categoria_padre ? 'ml-4 border-l-2 border-blue-300' : ''}`}
              onClick={() => onSelectCategory({ id: c.id_categoria, name: c.nombre })}
            >
              {c.nombre}
            </li>
          ))}
          {categorias.length === 0 && <li className="text-xs text-slate-500 italic">No sigues ninguna categoría.</li>}
        </ul>
      </div>
    </div>
  );
};

const DespliegaCentro = ({
  userId,
  selectedSource,
  selectedCategory,
  onSelectNews,
  refreshTrigger,
  specialView,
  calendarEvents,
  calendarCsvOutput,
  calendarLoading,
  calendarError,
  lee_vozalta,
  Genera_mp3
}: {
  userId: number | null,
  selectedSource: { id: number, name: string } | null,
  selectedCategory: { id: number, name: string } | null,
  onSelectNews: (news: any) => void,
  refreshTrigger?: number,
  specialView?: string | null,
  calendarEvents?: FormattedEvent[],
  calendarCsvOutput?: string,
  calendarLoading?: boolean,
  calendarError?: string | null,
  lee_vozalta: (text: string) => void,
  Genera_mp3: (text: string, idNoticia?: number) => void
}) => {
  const [noticias, setNoticias] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!userId) return;
    setLoading(true);

    let url = config.apiUrl(`/api/feed/${userId}`);

    // Si hay filtro de fuente, usar el endpoint con source_id
    if (selectedSource) {
      url += `?source_id=${selectedSource.id}`;
    }
    // Si hay filtro de categoría, usar el endpoint específico de categoría
    else if (selectedCategory) {
      url = config.apiUrl(`/api/feed/${userId}/categoria/${selectedCategory.id}`);
    }

    fetch(url)
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) {
          setNoticias(data);
        } else {
          console.error("Formato de feed inválido:", data);
          setNoticias([]);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error("Error cargando feed:", err);
        setLoading(false);
      });
  }, [userId, selectedSource, selectedCategory, refreshTrigger]);

  // Si hay una vista especial activa, mostrarla
  if (specialView === 'clima') {
    return (
      <div className="h-full flex items-center justify-center bg-gradient-to-br from-blue-50 to-cyan-50">
        <div className="text-center">
          <h1 className="text-6xl font-bold text-blue-600 mb-4">Clima</h1>
          <p className="text-slate-500">Información del clima próximamente...</p>
        </div>
      </div>
    );
  }

  if (specialView === 'horoscopo') {
    return (
      <div className="h-full flex items-center justify-center bg-gradient-to-br from-purple-50 to-pink-50">
        <div className="text-center">
          <h1 className="text-6xl font-bold text-purple-600 mb-4">Horoscopo</h1>
          <p className="text-slate-500">Contenido del horóscopo próximamente...</p>
        </div>
      </div>
    );
  }

  if (specialView === 'agenda') {
    return (
      <div className="h-full overflow-y-auto p-4 space-y-6 bg-gradient-to-br from-green-50 to-emerald-50">
        <div className="text-center mb-6">
          <h1 className="text-4xl font-bold text-green-600 mb-2"> Agenda Google Calendar</h1>
          <p className="text-slate-600">Eventos de las próximas {calendarEvents?.length ? 'horas' : '48 horas'}</p>
        </div>

        {calendarLoading && (
          <div className="flex justify-center py-8">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
            <span className="ml-3 text-slate-600">Conectando con Google Calendar...</span>
          </div>
        )}

        {calendarError && (
          <div className="bg-red-50 text-red-700 p-4 rounded-lg border border-red-200">
            <p className="font-medium">Error de conexión</p>
            <p className="text-sm mt-1">{calendarError}</p>
          </div>
        )}

        {calendarEvents && calendarEvents.length > 0 && (
          <div className="space-y-4">
            <div className="bg-white p-4 rounded-lg shadow-sm border border-green-200">
              <h3 className="text-lg font-semibold text-green-800 mb-3 flex items-center justify-between">
                <span>📋 Eventos encontrados: {calendarEvents.length}</span>
                <button
                  onClick={() => {
                    const textoAgenda = genera_texto_agenda(calendarEvents || []);
                    // Llamar a la función de voz alta
                    lee_vozalta(textoAgenda);
                    // Luego generar el archivo MP3 (sin ID de noticia ya que no es una noticia específica)
                    Genera_mp3(textoAgenda);
                  }}
                  className="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded-lg text-sm font-medium transition-colors"
                >
                  🔊 Lee agenda
                </button>
              </h3>
              <div className="space-y-3">
                {calendarEvents.map((event, index) => (
                  <div key={index} className="bg-green-50 p-3 rounded-md border border-green-100">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h4 className="font-medium text-green-900">{event.title}</h4>
                        <div className="text-sm text-green-700 mt-1">
                          <p>📅 {event.date} • 🕐 {event.time}</p>
                          {event.location && <p>📍 {event.location}</p>}
                          {event.notes && <p className="mt-1 text-green-600">📝 {event.notes}</p>}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white p-4 rounded-lg shadow-sm border border-green-200">
              <h3 className="text-lg font-semibold text-green-800 mb-3">
                📝 Agenda en Texto
              </h3>
              <div className="p-3 bg-green-50 rounded-lg border border-green-200 text-green-800 leading-relaxed">
                {genera_texto_agenda(calendarEvents || [])}
              </div>
            </div>
          </div>
        )}

        {!calendarLoading && !calendarError && (!calendarEvents || calendarEvents.length === 0) && (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">📅</div>
            <h3 className="text-xl font-medium text-slate-700 mb-2">Agenda libre</h3>
            <p className="text-slate-500">No hay eventos programados en las próximas horas.</p>
          </div>
        )}
      </div>
    );
  }

  if (loading) return <div className="p-8 text-center text-slate-500">Cargando noticias...</div>;

  return (
    <div className="h-full overflow-y-auto p-4 space-y-4 bg-slate-50/50">
      <h2 className="text-xl font-bold text-slate-800 mb-4 sticky top-0 bg-slate-100/90 p-2 backdrop-blur z-10 flex justify-between items-center">
        <span>Tu Feed de Noticias</span>
        {selectedSource && (
          <span className="text-xs font-normal bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
            Solo {selectedSource.name} {selectedSource.id}
          </span>
        )}
        {selectedCategory && (
          <span className="text-xs font-normal bg-green-100 text-green-800 px-2 py-1 rounded-full">
            Categoría: {selectedCategory.name} {selectedCategory.id}
          </span>
        )}
      </h2>
      {noticias.map(noticia => (
        <div
          key={noticia.id_noticia}
          className="bg-white p-4 rounded-lg shadow hover:shadow-md transition-shadow cursor-pointer hover:ring-2 hover:ring-blue-200"
          onClick={() => onSelectNews(noticia)}
        >
          {noticia.imagen_principal_url && (
            <img
              src={noticia.imagen_principal_url}
              alt={noticia.titulo}
              className="w-full h-48 object-cover rounded-md mb-3"
              onError={(e) => (e.currentTarget.style.display = 'none')}
            />
          )}
          <div className="flex items-center gap-2 text-xs text-slate-500 mb-1">
            <span className="bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full">{noticia.nombre_fuente}</span>
            <span>{noticia.fecha_hora_publicacion}</span>
          </div>
          <h3 className="text-lg font-bold text-slate-900 mb-2 leading-tight">{noticia.titulo}</h3>
          <p className="text-sm text-slate-600 line-clamp-3">{noticia.resumen}</p>
        </div>
      ))}
      {noticias.length === 0 && (
        <div className="text-center text-slate-500 py-10">
          No hay noticias para mostrar.
        </div>
      )}
    </div>
  );
};

const DespliegaDerecha = ({ noticia, onReadNews, isPlaying }: { noticia: any | null, onReadNews: (noticia: any) => void, isPlaying: boolean }) => {
  if (!noticia) {
    return (
      <div className="h-full flex flex-col items-center justify-center bg-slate-100/30 text-slate-400 p-8 text-center">
        <p className="mb-2">Selecciona una noticia para leerla aquí</p>
      </div>
    );
  }

  return (
    <div className="h-full overflow-y-auto bg-white p-6 relative">
      {/* Botón TTS Flotante Superior */}
      <div className="absolute top-6 right-6 z-10">
        <button
          onClick={() => onReadNews(noticia)}
          className={`p-3 rounded-full shadow-lg transition-all duration-300 hover:scale-110 active:scale-95 flex items-center justify-center ${isPlaying
            ? 'bg-gray-500 hover:bg-gray-600 text-white'
            : 'bg-red-500 hover:bg-red-600 text-white'
            }`}
          title={isPlaying ? "Detener lectura" : "Leer noticia"}
        >
          <Volume2 size={24} />
        </button>
      </div>

      {/* Fuente, Fecha y Hora (Arriba Izquierda) */}
      <div className="flex items-center gap-2 text-xs text-slate-500 mb-4 pr-16">
        <span className="bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full font-semibold">{noticia.nombre_fuente}</span>
        <span>{noticia.fecha_hora_publicacion}</span>
      </div>

      {/* Título Destacado */}
      <h1 className="text-2xl font-bold text-slate-900 mb-6 leading-tight pr-12">
        {noticia.titulo}
      </h1>

      {/* Imagen Principal */}
      {noticia.imagen_principal_url && (
        <img
          src={noticia.imagen_principal_url}
          alt={noticia.titulo}
          className="w-full h-auto object-cover rounded-lg shadow-sm mb-6"
          onError={(e) => (e.currentTarget.style.display = 'none')}
        />
      )}

      {/* Cuerpo de la Noticia */}
      <div className="prose prose-slate max-w-none mb-8 text-slate-700 leading-relaxed whitespace-pre-wrap">
        {noticia.resumen} {/* Usamos resumen que contiene el cuerpo según la query */}
      </div>

      {/* Fuente, Fecha y Hora (Repetido al final) */}
      <div className="flex items-center justify-between border-t border-slate-100 pt-4 mt-8">
        <div className="flex items-center gap-2 text-xs text-slate-400">
          <span className="font-semibold">{noticia.nombre_fuente}</span>
          <span>•</span>
          <span>{noticia.fecha_hora_publicacion}</span>
        </div>

        {/* Botón TTS Inferior */}
        <button
          onClick={() => onReadNews(noticia)}
          className={`p-3 rounded-full shadow-lg transition-all duration-300 hover:scale-110 active:scale-95 flex items-center justify-center ${isPlaying
            ? 'bg-gray-500 hover:bg-gray-600 text-white'
            : 'bg-red-500 hover:bg-red-600 text-white'
            }`}
          title={isPlaying ? "Detener lectura" : "Leer noticia"}
        >
          <Volume2 size={24} />
        </button>
      </div>

      {/* Link original opcional */}
      {noticia.url && (
        <div className="mt-4 text-right">
          <a href={noticia.url} target="_blank" rel="noopener noreferrer" className="text-xs text-blue-500 hover:underline">
            Ver original
          </a>
        </div>
      )}
    </div>
  );
};

const DespliegaFeed = ({ userId, userName, onReadNews, refreshTrigger, isTTSPlaying, onOpenLocationsMenu, climaData, specialView, setSpecialView, conecta_agenda_google, lee_vozalta, Genera_mp3, calendarEvents, calendarCsvOutput, calendarLoading, calendarError }: { userId: number | null, userName: string, onReadNews: (noticia: any) => void, refreshTrigger?: number, isTTSPlaying?: boolean, onOpenLocationsMenu: () => void, climaData: any[], specialView: string | null, setSpecialView: (view: string | null) => void, conecta_agenda_google: () => void, lee_vozalta: (text: string) => void, Genera_mp3: (text: string, idNoticia?: number) => void, calendarEvents?: FormattedEvent[], calendarCsvOutput?: string, calendarLoading?: boolean, calendarError?: string | null }) => {

  // Estado para el ancho de las columnas (porcentajes)
  const [leftWidth, setLeftWidth] = useState(20);
  const [rightWidth, setRightWidth] = useState(40); // Aumentar ancho por defecto para lectura
  const containerRef = useRef<HTMLDivElement>(null);

  // Estado para filtros y noticia seleccionada
  const [selectedSource, setSelectedSource] = useState<{ id: number, name: string } | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<{ id: number, name: string } | null>(null);
  const [selectedNews, setSelectedNews] = useState<any | null>(null);

  // Fecha actual formateada (sin año)
  const currentDate = new Date().toLocaleDateString('es-ES', {
    weekday: 'long',
    month: 'long',
    day: 'numeric'
  });


  // Handlers para selección de filtros
  const handleSelectSource = (source: { id: number, name: string } | null) => {
    setSelectedSource(source);
    setSelectedCategory(null); // Resetear categoría cuando se selecciona fuente
  };

  const handleSelectCategory = (category: { id: number, name: string } | null) => {
    setSelectedCategory(category);
    setSelectedSource(null); // Resetear fuente cuando se selecciona categoría
  };

  const handleResetFilters = () => {
    setSelectedSource(null);
    setSelectedCategory(null);
    setSpecialView(null);
  };


  // Función para botón 1 - Clima
  const otra_fuente1 = () => {
    console.log('Activando vista Clima');
    setSpecialView('clima');
    setSelectedSource(null);
    setSelectedCategory(null);
  };

  // Función para botón 2 - Horoscopo
  const otra_fuente2 = () => {
    console.log('Activando vista Horoscopo');
    setSpecialView('horoscopo');
    setSelectedSource(null);
    setSelectedCategory(null);
  };

  // Función para el menú de ubicaciones
  const menu_ubicaciones = () => {
    return (
      <button
        onClick={onOpenLocationsMenu}
        className="flex items-center gap-2 bg-white hover:bg-slate-50 text-slate-700 px-3 py-1.5 rounded-full border border-slate-200 shadow-sm transition-all duration-200 hover:shadow-md active:scale-95 mr-4"
        title="Seleccionar Ubicación"
      >
        <MapPin size={18} className="text-blue-600" />
        <span className="text-sm font-medium">Ubicaciones</span>
      </button>
    );
  };

  // Función para desplegar el clima
  const despliega_clima = () => {
    if (climaData.length === 0) return null;

    return (
      <div className="flex items-center gap-3">
        {climaData.map((clima, index) => (
          <div
            key={index}
            className="flex items-center gap-1 bg-blue-50 px-3 py-1 rounded-full border border-blue-200 text-sm"
          >
            <span className="font-semibold text-blue-700">{clima.t_actual}°</span>
            <span className="text-blue-400">/</span>
            <span className="text-blue-600">{clima.t_maxima}°</span>
          </div>
        ))}
      </div>
    );
  };

  // Función para mostrar iconos de otras fuentes
  const iconos_otras_fuentes = () => {
    return (
      <div className="flex items-center gap-2 bg-slate-50 px-3 py-1 rounded-full border border-slate-200">
        <button
          className="w-8 h-8 bg-blue-500 hover:bg-blue-600 text-white rounded-full flex items-center justify-center transition-all duration-200 hover:scale-110"
          title="Clima"
          onClick={() => otra_fuente1()}
        >
          1
        </button>
        <button
          className="w-8 h-8 bg-green-500 hover:bg-green-600 text-white rounded-full flex items-center justify-center transition-all duration-200 hover:scale-110"
          title="Horoscopo"
          onClick={() => otra_fuente2()}
        >
          2
        </button>
        <button
          className="w-8 h-8 bg-purple-500 hover:bg-purple-600 text-white rounded-full flex items-center justify-center transition-all duration-200 hover:scale-110"
          title="Otra Fuente 3"
          onClick={() => console.log('otra_fuente3')}
        >
          3
        </button>
        <button
          className="w-8 h-8 bg-orange-500 hover:bg-orange-600 text-white rounded-full flex items-center justify-center transition-all duration-200 hover:scale-110"
          title="Otra Fuente 4"
          onClick={() => console.log('otra_fuente4')}
        >
          4
        </button>
        <button
          className="w-8 h-8 bg-pink-500 hover:bg-pink-600 text-white rounded-full flex items-center justify-center transition-all duration-200 hover:scale-110"
          title="Otra Fuente 5"
          onClick={() => console.log('otra_fuente5')}
        >
          5
        </button>
        <button
          className="w-8 h-8 bg-teal-500 hover:bg-teal-600 text-white rounded-full flex items-center justify-center transition-all duration-200 hover:scale-110"
          title="Otra Fuente 6"
          onClick={() => console.log('otra_fuente6')}
        >
          6
        </button>
      </div>
    );
  };

  // Manejadores de redimensionamiento
  const handleMouseDownLeft = (e: React.MouseEvent) => {
    e.preventDefault();
    document.addEventListener('mousemove', handleMouseMoveLeft);
    document.addEventListener('mouseup', handleMouseUpLeft);
  };

  const handleMouseMoveLeft = (e: MouseEvent) => {
    if (containerRef.current) {
      const containerWidth = containerRef.current.offsetWidth;
      const newLeftWidth = (e.clientX / containerWidth) * 100;
      if (newLeftWidth > 10 && newLeftWidth < 40) { // Límites
        setLeftWidth(newLeftWidth);
      }
    }
  };

  const handleMouseUpLeft = () => {
    document.removeEventListener('mousemove', handleMouseMoveLeft);
    document.removeEventListener('mouseup', handleMouseUpLeft);
  };

  const handleMouseDownRight = (e: React.MouseEvent) => {
    e.preventDefault();
    document.addEventListener('mousemove', handleMouseMoveRight);
    document.addEventListener('mouseup', handleMouseUpRight);
  };

  const handleMouseMoveRight = (e: MouseEvent) => {
    if (containerRef.current) {
      const containerWidth = containerRef.current.offsetWidth;
      // El ancho derecho se calcula desde el borde derecho
      const newRightWidth = ((containerWidth - e.clientX) / containerWidth) * 100;
      if (newRightWidth > 20 && newRightWidth < 60) { // Límites más amplios para lectura
        setRightWidth(newRightWidth);
      }
    }
  };

  const handleMouseUpRight = () => {
    document.removeEventListener('mousemove', handleMouseMoveRight);
    document.removeEventListener('mouseup', handleMouseUpRight);
  };

  return (
    <div className="w-full h-screen flex flex-col bg-slate-50">
      {/* Header Superior */}
      <div className="w-full h-12 bg-white border-b border-slate-200 flex items-center justify-between px-6 shadow-sm z-20">
        {/* Izquierda: Fecha */}
        <div className="flex-1 flex items-center gap-3">
          <span className="font-semibold text-slate-700 capitalize">
            {currentDate}
          </span>
          {despliega_clima()}
          <button
            className="w-10 h-10 rounded-full bg-white border-2 border-slate-300 hover:border-blue-500 shadow-sm hover:shadow-md transition-all duration-200 hover:scale-110 active:scale-95 flex items-center justify-center overflow-hidden"
            title="Agenda"
            onClick={conecta_agenda_google}
          >
            <img
              src="/img/agenda.png"
              alt="Agenda"
              className="w-full h-full object-cover"
            />
          </button>
        </div>

        {/* Centro: Iconos Otras Fuentes */}
        <div className="flex-1 flex justify-center items-center">
          {menu_ubicaciones()}
          {iconos_otras_fuentes()}
        </div>

        {/* Derecha: Info Usuario */}
        <div className="flex-1 flex justify-end items-center gap-4 text-sm">
          <div className="flex flex-col items-end leading-tight">
            <span className="font-bold text-slate-800">{userName}</span>
            {/*<span className="text-xs text-slate-500">ID: {userId}</span>*/}
          </div>
          <div className="w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-bold">
            {userName.charAt(0).toUpperCase()}
          </div>
        </div>
      </div>

      {/* Contenedor de 3 Columnas */}
      <div ref={containerRef} className="w-full flex-1 flex overflow-hidden relative">
        {/* Columna Izquierda */}
        <div style={{ width: `${leftWidth}%` }} className="h-full border-r border-slate-200">
          <DespliegaIzquierda
            userId={userId}
            onSelectSource={handleSelectSource}
            onSelectCategory={handleSelectCategory}
            onResetFilters={handleResetFilters}
            refreshTrigger={refreshTrigger}
          />
        </div>

        {/* Resizer Izquierdo */}
        <div
          className="w-1 hover:w-2 bg-transparent hover:bg-blue-400 cursor-col-resize absolute z-10 h-full transition-all"
          style={{ left: `${leftWidth}%` }}
          onMouseDown={handleMouseDownLeft}
        />

        {/* Columna Central */}
        <div style={{ width: `${100 - leftWidth - rightWidth}%` }} className="h-full">
          <DespliegaCentro
            userId={userId}
            selectedSource={selectedSource}
            selectedCategory={selectedCategory}
            onSelectNews={setSelectedNews}
            refreshTrigger={refreshTrigger}
            specialView={specialView}
            calendarEvents={calendarEvents}
            calendarCsvOutput={calendarCsvOutput}
            calendarLoading={calendarLoading}
            calendarError={calendarError}
            lee_vozalta={lee_vozalta}
            Genera_mp3={Genera_mp3}
          />
        </div>

        {/* Resizer Derecho */}
        <div
          className="w-1 hover:w-2 bg-transparent hover:bg-blue-400 cursor-col-resize absolute z-10 h-full transition-all"
          style={{ right: `${rightWidth}%` }}
          onMouseDown={handleMouseDownRight}
        />

        {/* Columna Derecha */}
        <div style={{ width: `${rightWidth}%` }} className="h-full border-l border-slate-200">
          <DespliegaDerecha noticia={selectedNews} onReadNews={onReadNews} isPlaying={isTTSPlaying || false} />
        </div>
      </div>
    </div>
  );
};

function App() {
  console.log('🚀 App component is rendering...');

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  const [showRegistro, setShowRegistro] = useState(false);
  const [showIngreso, setShowIngreso] = useState(false);
  const [showAdminPanel, setShowAdminPanel] = useState(false);
  const [isWelcomeMode, setIsWelcomeMode] = useState(false);
  const [userName, setUserName] = useState('');
  const [currentUserId, setCurrentUserId] = useState<number | null>(null);
  const [errorMessage, setErrorMessage] = useState('');
  const [specialView, setSpecialView] = useState<string | null>(null);

  // Estados para el formulario de registro
  const [formRegistro, setFormRegistro] = useState({
    nombre: '',
    email: '',
    password: '',
    direccion: ''
  });

  // Estados para el formulario de ingreso
  const [formIngreso, setFormIngreso] = useState({
    email: '',
    password: ''
  });

  // Estado para TTS
  const [showTTS, setShowTTS] = useState(false);
  const [ttsText, setTtsText] = useState('');
  const [isTTSPlaying, setIsTTSPlaying] = useState(false);
  const [showLocationsMenu, setShowLocationsMenu] = useState(false);
  const [locationSelection, setLocationSelection] = useState<Set<string>>(new Set());
  const [climaData, setClimaData] = useState<any[]>([]);

  // Estados para Google Calendar
  const [isCalendarApiLoaded, setIsCalendarApiLoaded] = useState(false);
  const [isCalendarAuthenticated, setIsCalendarAuthenticated] = useState(false);
  const [calendarEvents, setCalendarEvents] = useState<FormattedEvent[]>([]);
  const [calendarCsvOutput, setCalendarCsvOutput] = useState('');
  const [calendarLoading, setCalendarLoading] = useState(false);
  const [calendarError, setCalendarError] = useState<string | null>(null);
  const [extrae_de_google_calendar, setExtraeDeGoogleCalendar] = useState(48); // Horas para extraer eventos

  // Cargar ubicaciones guardadas al montar el componente
  useEffect(() => {
    if (currentUserId) {
      fetch(`http://localhost:5000/api/preferencias_ubicacion/${currentUserId}`)
        .then(res => res.json())
        .then(data => {
          if (data.success && Array.isArray(data.ubicaciones)) {
            const savedIds = new Set(data.ubicaciones.map((u: any) => u.id_ubicacion));
            setLocationSelection(savedIds);
            console.log(`✅ Cargadas ${savedIds.size} ubicaciones guardadas para usuario ${currentUserId}`);
          }
        })
        .catch(err => console.error("Error cargando ubicaciones guardadas:", err));
    }
  }, [currentUserId]);

  // Función para rescatar y actualizar clima
  const actualizarClima = async () => {
    if (!currentUserId) return;

    try {
      console.log('🌤️ Iniciando actualización de clima...');

      // 1. Trigger update from Open-Meteo
      const updateRes = await fetch(config.apiUrl('/api/rescata_clima'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id_usuario: currentUserId })
      });

      const updateData = await updateRes.json();
      console.log('Update result:', updateData);

      // 2. Fetch fresh data
      const dataRes = await fetch(config.apiUrl(`/api/clima/${currentUserId}`));
      const data = await dataRes.json();

      if (Array.isArray(data)) {
        setClimaData(data);
        console.log(`✅ Clima actualizado: ${data.length} registros`);
      }
    } catch (err) {
      console.error("❌ Error actualizando clima:", err);
    }
  };

  // Función para conectar con Google Calendar
  const conecta_agenda_google = async () => {
    const GOOGLE_CLIENT_ID = "804804679723-454aihvh1688m03qgi80o9om5l53c24m.apps.googleusercontent.com";

    setCalendarLoading(true);
    setCalendarError(null);

    try {
      // Si la API no está cargada, inicializarla
      if (!isCalendarApiLoaded) {
        await new Promise<void>((resolve, reject) => {
          initializeGoogleApi(
            () => {
              setIsCalendarApiLoaded(true);
              resolve();
            },
            (err: any) => {
              reject(new Error(`Error inicializando Google API: ${JSON.stringify(err)}`));
            }
          );
        });
      }

      // Inicializar el cliente OAuth
      initTokenClient(GOOGLE_CLIENT_ID);

      // Solicitar acceso
      await triggerLogin();
      setIsCalendarAuthenticated(true);

      // Obtener eventos
      const rawEvents = await listUpcomingEvents(extrae_de_google_calendar);
      const formatted = rawEvents.map(formatEventCivil);
      setCalendarEvents(formatted);
      const csv = eventsToCSV(formatted);
      setCalendarCsvOutput(csv);

      // Cambiar la vista especial a 'agenda' para mostrar los resultados
      setSpecialView('agenda');

      console.log(`✅ Eventos obtenidos: ${formatted.length} eventos en formato CSV`);

    } catch (err: any) {
      console.error("❌ Error conectando con Google Calendar:", err);
      setCalendarError(err.message || "Error conectando con Google Calendar");
      setIsCalendarAuthenticated(false);
    } finally {
      setCalendarLoading(false);
    }
  };

  // Inicializar Google Calendar API
  useEffect(() => {
    initializeGoogleApi(
      () => setIsCalendarApiLoaded(true),
      (err) => console.error("Error inicializando Google Calendar API:", err)
    );
  }, []);

  // Cargar datos del clima al iniciar y cada 30 minutos
  useEffect(() => {
    if (currentUserId) {
      // Carga inicial
      // actualizarClima();

      // Configurar intervalo de 30 minutos (30 * 60 * 1000)
      // const intervalId = setInterval(actualizarClima, 30 * 60 * 1000);

      // return () => clearInterval(intervalId);
    }
  }, [currentUserId]);

  // Estado para forzar refresh del feed
  const [refreshFeed, setRefreshFeed] = useState(0);

  // Monitorear el estado de reproducción del TTS
  useEffect(() => {
    const interval = setInterval(() => {
      const speaking = ttsService.isSpeaking();
      setIsTTSPlaying(speaking);
      // Si terminó de hablar, limpiar el estado
      if (!speaking && showTTS) {
        setShowTTS(false);
      }
    }, 200);
    return () => clearInterval(interval);
  }, [showTTS]);

  // Función para generar el texto de la noticia
  const genera_noticia_txt = (noticia: any): string => {
    // Construir el texto a leer
    // Formato: Titulo. Fecha. Fuente. Cuerpo.
    // Aseguramos que no haya valores nulos
    const titulo = noticia.titulo || '';
    const fecha = noticia.fecha_hora_publicacion || '';
    const fuente = noticia.nombre_fuente || '';
    const cuerpo = noticia.resumen || ''; // En la query 'cuerpo' se mapea a 'resumen'

    let noticia_txt = `Título: ${titulo}. `;
    if (fecha) noticia_txt += `Fecha: ${fecha}. `;
    if (fuente) noticia_txt += `Fuente: ${fuente}. `;
    if (cuerpo) noticia_txt += `Contenido: ${cuerpo}`;

    return noticia_txt;
  };

  // Función para leer en voz alta (ahora sin modal, auto-ejecuta)
  const lee_vozalta = (text: string) => {
    setTtsText(text);
    // Ya no mostramos el modal, el componente se renderiza invisible y auto-ejecuta
    setShowTTS(true);
  };

  // Función para generar archivo MP3 (llamada al backend)
  const Genera_mp3 = async (text: string, idNoticia?: number) => {
    try {
      console.log('🎵 Generando archivo MP3 para el texto...');

      // Hacer llamada a la API del backend para generar el MP3
      const response = await fetch(config.apiUrl('/api/generar_mp3'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          texto: text,
          id_noticia: idNoticia || null
        })
      });

      const data = await response.json();

      if (data.success) {
        console.log(`✅ Audio MP3 generado exitosamente: ${data.archivo_mp3}`);
        // Aquí podrías mostrar una notificación al usuario
        // alert(`✅ Audio MP3 generado: ${data.archivo_mp3}`);
      } else {
        console.error('❌ Error generando MP3:', data.message);
        // alert(`❌ Error generando MP3: ${data.message}`);
      }
    } catch (error) {
      console.error('❌ Error en la llamada API para generar MP3:', error);
      // alert('❌ Error conectando con el servidor para generar MP3');
    }
  };

  // Función para leer agenda en voz alta y generar MP3
  const Lee_agenda = async (texto: string) => {
    // Llamar a la función de voz alta
    lee_vozalta(texto);
    // Luego generar el archivo MP3 (sin ID de noticia ya que no es una noticia específica)
    Genera_mp3(texto);
  };

  // Handler principal para el botón TTS con toggle
  const handleReadNews = (noticia: any) => {
    // Si ya está reproduciendo, detener
    if (isTTSPlaying) {
      ttsService.cancel();
      setShowTTS(false);
      setIsTTSPlaying(false);
      return;
    }

    // Si no está reproduciendo, iniciar
    const text = genera_noticia_txt(noticia);
    lee_vozalta(text);
    Genera_mp3(text, noticia.id_noticia); // Generar archivo MP3 con el texto y ID de noticia
  };

  // Función para mostrar formulario de registro
  const registro_usuario = () => {
    console.log('🔐 Función registro_usuario llamada');
    setShowRegistro(true);
    setShowIngreso(false);
    setErrorMessage('');
    // Resetear formulario
    setFormRegistro({
      nombre: '',
      email: '',
      password: '',
      direccion: ''
    });
  };

  // Función para mostrar formulario de ingreso
  const ingreso_usuario = () => {
    console.log('🔐 Función ingreso_usuario llamada');
    setShowIngreso(true);
    setShowRegistro(false);
    setErrorMessage('');
    // Resetear formulario
    setFormIngreso({
      email: '',
      password: ''
    });
  };

  // Función para enviar el formulario de registro
  const handleRegistrarse = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage('');

    // Validar campos requeridos
    if (!formRegistro.nombre || !formRegistro.email || !formRegistro.password) {
      setErrorMessage('Por favor complete todos los campos requeridos (nombre, email, contraseña)');
      return;
    }

    // Validar email
    if (!formRegistro.email.includes('@')) {
      setErrorMessage('Por favor ingrese un email válido');
      return;
    }

    // Validar longitud de contraseña
    if (formRegistro.password.length > 10) {
      setErrorMessage('La contraseña debe tener máximo 10 caracteres');
      return;
    }

    try {
      console.log('📤 Enviando solicitud de registro a la API...');
      const response = await fetch(config.apiUrl('/api/registro'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          nombre: formRegistro.nombre,
          email: formRegistro.email,
          password: formRegistro.password,
          direccion: formRegistro.direccion || null
        })
      });

      const data = await response.json();
      console.log('📥 Respuesta de la API:', data);

      if (data.success) {
        console.log('✅ Registro exitoso');
        setIsAuthenticated(true);
        setShowRegistro(false);
        setErrorMessage('');

        // Configurar datos del usuario recién registrado
        setUserName(formRegistro.nombre);
        // data.id_usuario viene de la respuesta del registro
        if (data.id_usuario) {
          setCurrentUserId(data.id_usuario);
        }

        // Activar modo bienvenida inmediatamente después del registro
        console.log('✨ Usuario registrado. Iniciando modo bienvenida.');
        setIsWelcomeMode(true);
        setIsModalOpen(true);
      } else {
        setErrorMessage(data.message || 'Error al registrar usuario');
        console.log('❌ Error en el registro:', data.message);
      }
    } catch (error) {
      console.error('❌ Error al conectar con la API:', error);
      setErrorMessage('Error al conectar con el servidor. Asegúrate de que la API Flask esté corriendo.');
    }
  };

  // Función para enviar el formulario de ingreso
  const handleIngresar = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage('');

    // Validar campos requeridos
    if (!formIngreso.email || !formIngreso.password) {
      setErrorMessage('Por favor complete email y contraseña');
      return;
    }

    try {
      console.log('📤 Enviando solicitud de ingreso a la API...');
      const response = await fetch(config.apiUrl('/api/ingreso'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: formIngreso.email,
          password: formIngreso.password
        })
      });

      const data = await response.json();
      console.log('📥 Respuesta de la API:', data);

      if (data.success) {
        console.log('✅ Ingreso exitoso');
        setIsAuthenticated(true);
        // Verificar si es admin (convertir a booleano por si viene como 1/0)
        const userIsAdmin = Boolean(data.usuario?.admin);
        console.log('👤 Es admin:', userIsAdmin);
        setIsAdmin(userIsAdmin);
        setUserName(data.usuario?.nombre || '');
        setCurrentUserId(data.usuario?.id_usuario);

        setShowIngreso(false);
        setErrorMessage('');

        // Ya no verificamos preferencias aquí para mostrar el modal.
        // El modal de bienvenida solo se muestra tras el registro.
        // alert(`✅ ${data.message}. Bienvenido ${data.usuario?.nombre}!`);
      } else {
        setErrorMessage(data.message || 'Credenciales inválidas');
        console.log('❌ Error en el ingreso:', data.message);
      }
    } catch (error) {
      console.error('❌ Error al conectar con la API:', error);
      setErrorMessage('Error al conectar con el servidor. Asegúrate de que la API Flask esté corriendo.');
    }
  };

  // Función para cargar el panel de administración
  const carga_panel = () => {
    console.log('🚀 Cargando panel de administración...');
    setShowAdminPanel(true);
  };

  // Función para cerrar el panel de administración
  const cerrar_panel = () => {
    console.log('❌ Cerrando panel de administración...');
    setShowAdminPanel(false);
  };

  const handleCloseLocationsMenu = async () => {
    setShowLocationsMenu(false);

    // Guardar preferencias al cerrar
    if (currentUserId) {
      try {
        // Convertir Set a Array de objetos para la API
        // Asumimos que el ID contiene info del tipo (ej: 'reg-', 'com-') o lo inferimos
        // Para simplificar, enviaremos el ID y un tipo genérico o inferido
        const ubicacionesArray = Array.from(locationSelection).map((id: string) => {
          let type = 'pais';
          if (id.startsWith('reg-')) type = 'region';
          if (id.startsWith('prov-')) type = 'provincia';
          if (id.startsWith('com-')) type = 'comuna';
          return { id, type };
        });

        console.log('Guardando ubicaciones:', ubicacionesArray);

        const response = await fetch(config.apiUrl('/api/preferencias_ubicacion'), {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            id_usuario: currentUserId,
            ubicaciones: ubicacionesArray
          })
        });

        const data = await response.json();
        if (data.success) {
          console.log('✅ Preferencias de ubicación guardadas correctamente');
        } else {
          console.error('❌ Error al guardar preferencias de ubicación:', data.message);
        }
      } catch (error) {
        console.error('❌ Error de red al guardar preferencias de ubicación:', error);
      }
    }
  };

  // Función para abrir el panel de admin (ahora llama a carga_panel)
  const handleOpenAdminPanel = async () => {
    // Verificamos si realmente es admin antes de cargar el panel
    if (isAdmin) {
      carga_panel();
    } else {
      alert('⛔ Acceso denegado. Se requieren permisos de administrador.');
    }
  };

  // Si no está autenticado, mostrar pantalla de autenticación
  if (!isAuthenticated) {
    console.log('📱 Showing authentication screen');
    console.log('🔍 Estado actual - showRegistro:', showRegistro, 'showIngreso:', showIngreso);
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-100 to-slate-300 flex items-center justify-center p-4">
        <div className="bg-white rounded-xl shadow-2xl p-8 max-w-md w-full">
          <h1 className="text-2xl font-bold text-slate-800 mb-4 text-center">Sistema de Noticias</h1>

          {/* Mensaje1 */}
          <p className="text-sm text-slate-600 mb-6 text-center font-semibold">mensaje1</p>

          {/* Mensaje de error */}
          {errorMessage && (
            <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-lg text-xs">
              {errorMessage}
            </div>
          )}

          {/* Formulario de Registro */}
          {showRegistro && (
            <form onSubmit={handleRegistrarse} className="space-y-4">
              <h2 className="text-lg font-semibold text-slate-700 mb-4">Formulario de Registro</h2>

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Nombre *</label>
                <input
                  type="text"
                  value={formRegistro.nombre}
                  onChange={(e) => setFormRegistro({ ...formRegistro, nombre: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Email *</label>
                <input
                  type="email"
                  value={formRegistro.email}
                  onChange={(e) => setFormRegistro({ ...formRegistro, email: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Contraseña * (máx. 10 caracteres)</label>
                <input
                  type="password"
                  value={formRegistro.password}
                  onChange={(e) => setFormRegistro({ ...formRegistro, password: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  maxLength={10}
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Dirección (opcional)</label>
                <input
                  type="text"
                  value={formRegistro.direccion}
                  onChange={(e) => setFormRegistro({ ...formRegistro, direccion: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="flex gap-2 pt-2">
                <button
                  type="submit"
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg shadow-lg transition-all duration-300 hover:scale-105 active:scale-95 text-sm"
                >
                  Registrarse
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowRegistro(false);
                    setErrorMessage('');
                  }}
                  className="flex-1 bg-gray-400 hover:bg-gray-500 text-white font-medium py-2 px-4 rounded-lg shadow-lg transition-all duration-300 text-sm"
                >
                  Cancelar
                </button>
              </div>
            </form>
          )}

          {/* Formulario de Ingreso */}
          {showIngreso && (
            <form onSubmit={handleIngresar} className="space-y-4">
              <h2 className="text-lg font-semibold text-slate-700 mb-4">Formulario de Ingreso</h2>

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Email *</label>
                <input
                  type="email"
                  value={formIngreso.email}
                  onChange={(e) => setFormIngreso({ ...formIngreso, email: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Contraseña *</label>
                <input
                  type="password"
                  value={formIngreso.password}
                  onChange={(e) => setFormIngreso({ ...formIngreso, password: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                  required
                />
              </div>

              <div className="flex gap-2 pt-2">
                <button
                  type="submit"
                  className="flex-1 bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-lg shadow-lg transition-all duration-300 hover:scale-105 active:scale-95 text-sm"
                >
                  Ingresar
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowIngreso(false);
                    setErrorMessage('');
                  }}
                  className="flex-1 bg-gray-400 hover:bg-gray-500 text-white font-medium py-2 px-4 rounded-lg shadow-lg transition-all duration-300 text-sm"
                >
                  Cancelar
                </button>
              </div>
            </form>
          )}

          {/* Botones de autenticación (solo si no hay formulario visible) */}
          {!showRegistro && !showIngreso && (
            <div className="space-y-3">
              <p className="text-xs text-gray-500 mb-2 text-center">Seleccione una opción:</p>
              <button
                onClick={registro_usuario}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-6 rounded-lg shadow-lg transition-all duration-300 hover:scale-105 active:scale-95"
                type="button"
              >
                Registro de Usuario
              </button>

              <button
                onClick={ingreso_usuario}
                className="w-full bg-green-600 hover:bg-green-700 text-white font-medium py-3 px-6 rounded-lg shadow-lg transition-all duration-300 hover:scale-105 active:scale-95"
                type="button"
              >
                Ingresar
              </button>
            </div>
          )}
        </div>
      </div>
    );
  }

  // Si está autenticado, mostrar contenido principal
  console.log('✅ User is authenticated, showing main content');
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-100 to-slate-300 flex items-center justify-center">

      {/* Feed Principal */}
      <DespliegaFeed
        userId={currentUserId}
        userName={userName}
        onReadNews={handleReadNews}
        refreshTrigger={refreshFeed}
        isTTSPlaying={isTTSPlaying}
        onOpenLocationsMenu={() => setShowLocationsMenu(true)}
        climaData={climaData}
        specialView={specialView}
        setSpecialView={setSpecialView}
        conecta_agenda_google={conecta_agenda_google}
        lee_vozalta={lee_vozalta}
        Genera_mp3={Genera_mp3}
        calendarEvents={calendarEvents}
        calendarCsvOutput={calendarCsvOutput}
        calendarLoading={calendarLoading}
        calendarError={calendarError}
      />

      {/* Botón Flotante de Configuración (Requisito Principal) */}
      <div className="fixed bottom-8 right-8 z-40">
        <button
          onClick={() => setIsModalOpen(true)}
          className="group relative flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-full shadow-xl transition-all duration-300 hover:scale-105 active:scale-95"
          aria-label="Configuración de preferencias"
        >
          <Settings2 size={18} className="animate-spin-slow" />
          <span className="font-medium text-sm hidden group-hover:block transition-all duration-300">
            Configuración de preferencias
          </span>
        </button>
      </div>

      {/* Botón Panel Admin (Top Right) - Solo visible para admins */}
      {isAdmin && (
        <div className="fixed top-8 right-8 z-40">
          <button
            onClick={handleOpenAdminPanel}
            className="group relative flex items-center gap-2 bg-orange-600 hover:bg-orange-700 text-white px-4 py-2 rounded-full shadow-xl transition-all duration-300 hover:scale-105 active:scale-95"
            aria-label="Panel de Control"
          >
            <LayoutDashboard size={18} />
            <span className="font-medium text-sm hidden group-hover:block transition-all duration-300">
              Panel de Control
            </span>
          </button>
        </div>
      )}

      {/* Modal de Configuración */}
      <PreferencesModal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          // Forzar refresh del feed después de cerrar el modal
          setRefreshFeed(prev => prev + 1);
        }}
        isWelcomeMode={isWelcomeMode}
        userName={userName}
        userId={currentUserId}
      />

      {/* Panel de Administración */}
      {showAdminPanel && (
        <AdminPanel onClose={cerrar_panel} />
      )}

      {/* Modal de Ubicaciones */}
      {showLocationsMenu && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-3xl h-[90vh] overflow-hidden relative flex flex-col">
            <div className="flex justify-between items-center p-1 border-b border-gray-100 bg-gray-50">
              <h3 className="font-bold text-gray-800 flex items-center gap-2">
                <MapPin className="text-blue-600" size={20} />
                Selector de Ubicaciones
                <p className="text-xs text-gray-500">(Seleccione regiones, provincias o comunas.)</p>
              </h3>
              <div className="flex items-center gap-2 mr-2">
                <span className="text-sm font-medium text-gray-600">Guardar y Cerrar</span>
                <button
                  onClick={handleCloseLocationsMenu}
                  className="text-gray-400 hover:text-gray-600 transition-colors p-1 hover:bg-gray-200 rounded-full"
                >
                  <X size={24} />
                </button>
              </div>
            </div>
            <div className="flex-1 overflow-hidden bg-gray-50 relative">
              {/* Renderizamos el componente importado. 
                  Nota: El componente App de menu_ubicaciones tiene su propio layout (min-h-screen), 
                  así que lo envolvemos en un div que fuerce el scroll si es necesario o confiamos en su layout interno.
                  Dado que tiene min-h-screen, forzará scroll en este contenedor si no lo manejamos.
                  Vamos a intentar renderizarlo tal cual, pero dentro de este contenedor con overflow.
              */}
              <div className="absolute inset-0 overflow-auto">
                <LocationsMenu
                  initialSelection={locationSelection}
                  onSelectionChange={setLocationSelection}
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal TTS - COMENTADO: Ahora se ejecuta automáticamente sin ventana */}
      {/* El componente ReadingAssistant se renderiza invisible y auto-ejecuta la lectura */}
      {showTTS && (
        <div style={{ display: 'none' }}>
          <ReadingAssistant text={ttsText} />
        </div>
      )}

      {/* VENTANA MODAL COMENTADA - Ya no se muestra */}
      {/* 
      {showTTS && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl overflow-hidden relative">
            <div className="flex justify-between items-center p-4 border-b border-gray-100 bg-gray-50">
              <h3 className="font-bold text-gray-800 flex items-center gap-2">
                <Volume2 className="text-indigo-600" size={20} />
                Asistente de Lectura
              </h3>
              <button
                onClick={() => setShowTTS(false)}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <X size={24} />
              </button>
            </div>
            <div className="p-0">
              <ReadingAssistant text={ttsText} />
            </div>
          </div>
        </div>
      )}
      */}
    </div>
  );
}

export default App;

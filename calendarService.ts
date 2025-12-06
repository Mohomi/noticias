import { CalendarEvent, FormattedEvent } from './types';

// Extend Window interface to include Google global objects
declare global {
  interface Window {
    gapi: any;
    google: any;
  }
}

const SCOPES = 'https://www.googleapis.com/auth/calendar.events.readonly';

let tokenClient: any;
let gapiInited = false;
let gisInited = false;

export const initializeGoogleApi = (
  onInit: () => void,
  onError: (err: any) => void
) => {
  // Prevent duplicate script injection
  if (document.getElementById('gapi-script')) {
    if (gapiInited && gisInited) {
      onInit();
    }
    return;
  }

  const script1 = document.createElement('script');
  script1.src = 'https://apis.google.com/js/api.js';
  script1.id = 'gapi-script';
  script1.async = true;
  script1.defer = true;
  script1.onload = () => {
    window.gapi.load('client', async () => {
      try {
        await window.gapi.client.init({
          discoveryDocs: ['https://www.googleapis.com/discovery/v1/apis/calendar/v3/rest'],
        });
        gapiInited = true;
        if (gisInited) onInit();
      } catch (err) {
        onError(err);
      }
    });
  };
  document.body.appendChild(script1);

  const script2 = document.createElement('script');
  script2.src = 'https://accounts.google.com/gsi/client';
  script2.id = 'gis-script';
  script2.async = true;
  script2.defer = true;
  script2.onload = () => {
    gisInited = true;
    if (gapiInited) onInit();
  };
  document.body.appendChild(script2);
};

export const initTokenClient = (clientId: string) => {
  if (!window.google || !window.google.accounts) {
    throw new Error("Google Identity Services no está cargado.");
  }
  tokenClient = window.google.accounts.oauth2.initTokenClient({
    client_id: clientId,
    scope: SCOPES,
    callback: '', // defined at request time
  });
};

export const triggerLogin = (): Promise<string> => {
  return new Promise((resolve, reject) => {
    if (!tokenClient) {
      reject(new Error("Cliente OAuth no inicializado."));
      return;
    }
    try {
      tokenClient.callback = async (resp: any) => {
        if (resp.error !== undefined) {
          reject(resp);
          return;
        }
        // CRITICAL: Set the token for gapi client to authorize requests
        window.gapi.client.setToken(resp);
        resolve(resp.access_token);
      };
      tokenClient.requestAccessToken({ prompt: 'consent' });
    } catch (err) {
      reject(new Error("Fallo en la inicialización o configuración de Google Client ID."));
    }
  });
};

export const listUpcomingEvents = async (hours: number = 48): Promise<CalendarEvent[]> => {
  // Verify gapi client is ready
  if (!window.gapi?.client?.calendar) {
    throw new Error("Google API no está lista.");
  }

  const now = new Date();
  const nextHours = new Date(now.getTime() + hours * 60 * 60 * 1000);

  try {
    const response = await window.gapi.client.calendar.events.list({
      'calendarId': 'primary',
      'timeMin': now.toISOString(),
      'timeMax': nextHours.toISOString(),
      'showDeleted': false,
      'singleEvents': true,
      'maxResults': 50,
      'orderBy': 'startTime',
    });
    return response.result.items as CalendarEvent[];
  } catch (err) {
    console.error("Error fetching events", err);
    throw err;
  }
};

export const formatEventCivil = (event: CalendarEvent): FormattedEvent => {
  const start = event.start.dateTime || event.start.date || '';
  const dateObj = new Date(start);

  // Format Date: DD/MM/YYYY
  const dateStr = dateObj.toLocaleDateString('es-ES', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  });

  // Format Time: HH:mm (24h)
  const timeStr = event.start.dateTime
    ? dateObj.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit', hour12: false })
    : 'Todo el día';

  // Clean text fields to avoid breaking CSV with semicolons or newlines
  const clean = (str?: string) => str ? str.replace(/;/g, ',').replace(/[\r\n]+/g, ' ').trim() : '';

  return {
    date: dateStr,
    time: timeStr,
    title: clean(event.summary),
    location: clean(event.location),
    notes: clean(event.description),
    raw: event
  };
};

export const eventsToCSV = (events: FormattedEvent[]): string => {
  const header = "Fecha;Hora;Título;Ubicación;Notas";
  const rows = events.map(e => `${e.date};${e.time};${e.title};${e.location};${e.notes}`);
  return [header, ...rows].join('\n');
};

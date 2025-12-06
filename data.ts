import { GeoNode } from './types';

export const chileData: GeoNode = {
  id: 'cl',
  label: 'Chile',
  children: [
    {
      id: 'reg-coquimbo',
      label: 'Región de Coquimbo',
      children: [
        {
          id: 'prov-choapa',
          label: 'Provincia de Choapa',
          children: [
            { id: 'com-illapel', label: 'Illapel' },
            { id: 'com-canela', label: 'Canela' },
            { id: 'com-los-vilos', label: 'Los Vilos' },
            { id: 'com-salamanca', label: 'Salamanca' },
          ],
        },
        {
          id: 'prov-elqui',
          label: 'Provincia de Elqui',
          children: [
            { id: 'com-laserena', label: 'La Serena' },
            { id: 'com-coquimbo', label: 'Coquimbo' },
            { id: 'com-andacollo', label: 'Andacollo' },
            { id: 'com-lahiguera', label: 'La Higuera' },
            { id: 'com-paihuano', label: 'Paihuano' },
            { id: 'com-vicuna', label: 'Vicuña' },
          ],
        },
        {
          id: 'prov-limari',
          label: 'Provincia de Limarí',
          children: [
            { id: 'com-ovalle', label: 'Ovalle' },
            { id: 'com-riohurtado', label: 'Río Hurtado' },
            { id: 'com-montepatria', label: 'Monte Patria' },
            { id: 'com-combarbala', label: 'Combarbalá' },
            { id: 'com-punitaqui', label: 'Punitaqui' },
          ],
        },
      ],
    },
    // Adding a placeholder for another region to demonstrate scale
    {
      id: 'reg-metropolitana',
      label: 'Región Metropolitana',
      children: [
        {
          id: 'prov-santiago',
          label: 'Provincia de Santiago',
          children: [
            { id: 'com-santiago', label: 'Santiago' },
            { id: 'com-providencia', label: 'Providencia' },
            { id: 'com-lascondes', label: 'Las Condes' },
          ],
        },
      ],
    },
  ],
};
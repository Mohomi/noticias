import React, { useState, useMemo, useEffect } from 'react';
import { GeoNode, TreeContextType } from './types';
import { calculateNewSelection, getSelectionState, getAllDescendantIds } from './utils';
import TreeItem from './components/TreeItem';
import { MapPin, Trash2, CheckSquare } from 'lucide-react';

interface AppProps {
  onSelectionChange?: (selectedIds: Set<string>) => void;
  initialSelection?: Set<string>;
}

const App: React.FC<AppProps> = ({ onSelectionChange, initialSelection }) => {
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());
  const [selectedIds, setSelectedIds] = useState<Set<string>>(initialSelection || new Set());
  const [geoData, setGeoData] = useState<GeoNode | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Cargar datos geográficos desde la API
  useEffect(() => {
    fetch('http://localhost:5000/api/geografia')
      .then(res => res.json())
      .then(data => {
        setGeoData(data);
        setLoading(false);
        // Expandir el primer nivel por defecto
        if (data && data.id) {
          setExpandedIds(new Set([data.id]));
        }
      })
      .catch(err => {
        console.error('Error cargando geografía:', err);
        setError('Error cargando datos geográficos');
        setLoading(false);
      });
  }, []);

  // --- Logic ---

  const toggleExpand = (id: string) => {
    const newExpanded = new Set(expandedIds);
    if (newExpanded.has(id)) {
      newExpanded.delete(id);
    } else {
      newExpanded.add(id);
    }
    setExpandedIds(newExpanded);
  };

  const toggleSelection = (node: GeoNode) => {
    if (!geoData) return;
    const newSelection = calculateNewSelection(geoData, node, selectedIds);
    setSelectedIds(newSelection);
    onSelectionChange?.(newSelection);
  };

  const selectAll = () => {
    if (!geoData) return;
    const allIds = getAllDescendantIds(geoData);
    const newSelection = new Set(allIds);
    setSelectedIds(newSelection);
    onSelectionChange?.(newSelection);
  };

  const clearSelection = () => {
    const newSelection = new Set<string>();
    setSelectedIds(newSelection);
    onSelectionChange?.(newSelection);
  };

  // --- Derived State for UI ---

  const selectedCount = selectedIds.size;
  const treeContext: TreeContextType = useMemo(() => ({
    expandedIds,
    selectedIds,
    toggleExpand,
    toggleSelection
  }), [expandedIds, selectedIds]);

  return (
    <div className="h-full bg-gray-50 flex items-start justify-center p-1 font-sans text-gray-800">

      <div className="w-full max-w-2xl grid grid-cols-1 gap-8 h-full">

        {/* Left Panel: The Tree */}
        <div className="bg-white rounded-xl shadow-lg border border-gray-100 flex flex-col overflow-hidden">
          {/*<div className="p-5 border-b border-gray-100 bg-white z-10 sticky top-0">
            <div className="flex items-center space-x-2 mb-1">
              <MapPin className="text-blue-600" size={20} />
              <h2 className="text-lg font-bold text-gray-900">Selector Territorial</h2>
            </div>
          </div>*/}

          <div className="flex-1 overflow-y-auto p-4 custom-scrollbar">
            {loading && (
              <div className="flex items-center justify-center h-full text-gray-500">
                <p>Cargando ubicaciones...</p>
              </div>
            )}
            {error && (
              <div className="flex items-center justify-center h-full text-red-500">
                <p>{error}</p>
              </div>
            )}
            {geoData && (
              <TreeItem
                node={geoData}
                level={0}
                context={treeContext}
              />
            )}
          </div>

          <div className="p-2 border-t border-gray-100 bg-gray-50 flex justify-between items-center text-sm">
            <button
              onClick={selectAll}
              className="flex items-center text-gray-600 hover:text-blue-600 transition-colors font-medium"
            >
              <CheckSquare size={16} className="mr-1.5" />
              Seleccionar Todo
            </button>
            <button
              onClick={clearSelection}
              className="flex items-center text-gray-600 hover:text-red-500 transition-colors font-medium"
            >
              <Trash2 size={16} className="mr-1.5" />
              Limpiar
            </button>
          </div>
        </div>

        {/* Right Panel: Selection Summary - COMENTADO */}
        {/* <div className="bg-white rounded-xl shadow-lg border border-gray-100 flex flex-col overflow-hidden">
          <div className="p-5 border-b border-gray-100 bg-blue-600 text-white">
            <h2 className="text-lg font-bold">Resumen de Selección</h2>
            <div className="mt-1 opacity-90 text-sm">
              {selectedCount === 0
                ? "No hay elementos seleccionados"
                : `${selectedCount} elemento${selectedCount !== 1 ? 's' : ''} seleccionado${selectedCount !== 1 ? 's' : ''}`}
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-6 bg-gray-50">
            {selectedCount === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-gray-400">
                <MapPin size={48} className="mb-4 opacity-20" />
                <p className="text-center max-w-xs">
                  Navegue por el menú de la izquierda para seleccionar las zonas geográficas que desea incluir.
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                <SummaryView data={chileData} selectedIds={selectedIds} />
              </div>
            )}
          </div>
        </div> */}

      </div>
    </div>
  );
};

// Helper component to display summary clearly
const SummaryView: React.FC<{ data: GeoNode, selectedIds: Set<string> }> = ({ data, selectedIds }) => {
  const status = getSelectionState(data, selectedIds);

  if (status === 'unchecked') return null;

  // If node is checked (fully selected), just show the node
  if (status === 'checked') {
    return (
      <div className="bg-white p-3 rounded-lg border border-blue-100 shadow-sm flex items-start animate-in fade-in zoom-in-95 duration-200">
        <span className="w-2 h-2 mt-2 mr-3 rounded-full bg-green-500 flex-shrink-0"></span>
        <div>
          <p className="font-semibold text-gray-800">{data.label}</p>
          <p className="text-xs text-green-600 mt-0.5 font-medium">Cobertura total seleccionada</p>
        </div>
      </div>
    );
  }

  // If indeterminate, show children who are checked/indeterminate
  return (
    <div className="space-y-2">
      <div className="mb-2 pb-1 border-b border-gray-200 text-xs font-bold text-gray-400 uppercase tracking-wider">
        {data.label} (Parcial)
      </div>
      <div className="pl-2 space-y-2 border-l-2 border-gray-200 ml-1">
        {data.children?.map(child => (
          <SummaryView key={child.id} data={child} selectedIds={selectedIds} />
        ))}
      </div>
    </div>
  );
};

export default App;
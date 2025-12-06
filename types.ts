export interface GeoNode {
  id: string;
  label: string;
  children?: GeoNode[];
}

export type SelectionState = 'checked' | 'unchecked' | 'indeterminate';

export interface TreeContextType {
  expandedIds: Set<string>;
  selectedIds: Set<string>;
  toggleExpand: (id: string) => void;
  toggleSelection: (node: GeoNode) => void;
}
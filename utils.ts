import { GeoNode, SelectionState } from './types';

/**
 * Recursively collects all IDs from a node and its descendants.
 */
export const getAllDescendantIds = (node: GeoNode): string[] => {
  let ids = [node.id];
  if (node.children) {
    node.children.forEach((child) => {
      ids = ids.concat(getAllDescendantIds(child));
    });
  }
  return ids;
};

/**
 * Determines the visual state of a checkbox based on the selected IDs set.
 */
export const getSelectionState = (node: GeoNode, selectedIds: Set<string>): SelectionState => {
  // 1. If the node itself is explicitly selected
  if (selectedIds.has(node.id)) {
    return 'checked';
  }

  // 2. If no children, and not in set, it's unchecked
  if (!node.children || node.children.length === 0) {
    return 'unchecked';
  }

  // 3. Check children status
  const childrenStates = node.children.map(child => getSelectionState(child, selectedIds));
  
  const allChecked = childrenStates.every(status => status === 'checked');
  const someChecked = childrenStates.some(status => status === 'checked' || status === 'indeterminate');

  if (allChecked) return 'checked';
  if (someChecked) return 'indeterminate';
  
  return 'unchecked';
};

/**
 * Recursively finds parents of a specific node ID.
 * Returns an array of parent nodes (from root down to direct parent).
 */
export const findAncestors = (root: GeoNode, targetId: string, path: GeoNode[] = []): GeoNode[] | null => {
  if (root.id === targetId) {
    return path;
  }
  if (root.children) {
    for (const child of root.children) {
      const result = findAncestors(child, targetId, [...path, root]);
      if (result) return result;
    }
  }
  return null;
};

/**
 * Updates the selection set based on a toggle action.
 * Handles cascading select/deselect logic.
 */
export const calculateNewSelection = (
  root: GeoNode,
  targetNode: GeoNode,
  currentSelectedIds: Set<string>
): Set<string> => {
  const newSet = new Set(currentSelectedIds);
  const currentState = getSelectionState(targetNode, currentSelectedIds);
  const descendants = getAllDescendantIds(targetNode);

  // LOGIC 1: Toggle the target and its descendants
  if (currentState === 'checked') {
    // Deselect: Remove target and all descendants
    descendants.forEach(id => newSet.delete(id));
  } else {
    // Select (from unchecked or indeterminate): Add target and all descendants
    descendants.forEach(id => newSet.add(id));
  }

  // LOGIC 2: Update Ancestors
  // We need to traverse up from the target to the root to update parent statuses.
  // However, since `getSelectionState` computes parent state dynamically based on children,
  // we primarily need to ensure that if we just selected all children of a parent, 
  // the parent ID *could* technically be added for optimization, OR we just ensure
  // we remove ancestor IDs if we deselect a child.
  
  // To keep state clean:
  // 1. If we deselected the target, we must remove all its ancestors from the set
  //    (because an ancestor cannot be 'checked' if one of its children is not).
  if (currentState === 'checked') {
    const ancestors = findAncestors(root, targetNode.id);
    if (ancestors) {
      ancestors.forEach(a => newSet.delete(a.id));
    }
  } 
  
  // 2. If we selected the target, we might need to "check" ancestors if all their
  //    other children were already checked.
  //    Instead of complex logic here, we can rely on a self-correcting pass or 
  //    just simple ancestor verification.
  
  // Let's do a robust pass:
  // If we just selected nodes, walk up. Check if siblings are all selected. If yes, add parent.
  if (currentState !== 'checked') {
     const ancestors = findAncestors(root, targetNode.id);
     // Reverse to go from direct parent up to root
     if (ancestors) {
       for (let i = ancestors.length - 1; i >= 0; i--) {
         const parent = ancestors[i];
         // Check if this parent is now fully selected
         const childrenIds = parent.children?.map(c => c.id) || [];
         const allChildrenInSet = childrenIds.every(cid => {
             // We need to check if the child is effectively checked.
             // Since we just updated the set for the target branch, 
             // checking presence in newSet is a good proxy if we assume consistency,
             // but `getSelectionState` logic is recursive.
             // A simpler check: is the child ID in the newSet?
             // (This assumes we are adding parent IDs to the set when all kids are checked)
             return newSet.has(cid); 
         });

         if (allChildrenInSet) {
           newSet.add(parent.id);
         } else {
           // If not all children are selected, parent cannot be in the set
           // (It might be indeterminate, but that's not stored in the Set)
           newSet.delete(parent.id);
         }
       }
     }
  }

  return newSet;
};

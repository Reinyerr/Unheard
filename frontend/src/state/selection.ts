import { createContext, createElement, useContext, useMemo, useReducer, type ReactNode } from 'react';
import { experimentSchema, languageId, mapMetric, sampleSchema,
  type Experiment, type LanguageId, type MapMetric, type Sample } from '../types/research';

export type SelectedLanguage = LanguageId | 'all';
export type Selection = {
  language_id: SelectedLanguage; ward_id: number | null; map_metric: MapMetric;
  selected_sample: Sample | null; selected_result: Experiment | null;
  language_revision: number; error: string | null;
};
export const initialSelection: Selection = { language_id: 'all', ward_id: null, map_metric: 'count',
  selected_sample: null, selected_result: null, language_revision: 0, error: null };

type Action =
  | { type: 'language'; value: string }
  | { type: 'ward'; value: number | null }
  | { type: 'metric'; value: string }
  | { type: 'sample'; value: Sample | null; revision: number }
  | { type: 'result'; value: Experiment | null; revision: number }
  | { type: 'reset' | 'dismiss_error' };

/** Language revision binds future asynchronous audio/results to the language that requested them. */
export function selectionReducer(state: Selection, action: Action): Selection {
  switch (action.type) {
    case 'language': {
      const parsed = languageId.safeParse(action.value);
      const next = action.value === 'all' ? 'all' : parsed.success ? parsed.data : 'all';
      const error = action.value !== 'all' && !parsed.success ? 'Unknown language selection. Returned to all tracked languages.' : null;
      if (next === state.language_id && error === null) return { ...state, error: null };
      return { ...state, language_id: next, selected_sample: null, selected_result: null,
        language_revision: state.language_revision + 1, error };
    }
    case 'ward':
      return action.value === null || Number.isInteger(action.value) && action.value >= 1 && action.value <= 11
        ? { ...state, ward_id: action.value, error: null }
        : { ...state, ward_id: null, error: 'Unknown ward selection. Cleared the census ward filter.' };
    case 'metric': {
      const parsed = mapMetric.safeParse(action.value);
      return { ...state, map_metric: parsed.success ? parsed.data : 'count',
        error: parsed.success ? null : 'Unknown map metric. Returned to speaker count.' };
    }
    case 'sample': {
      if (action.revision !== state.language_revision) return state;
      if (action.value === null) return { ...state, selected_sample: null, selected_result: null };
      const parsed = sampleSchema.safeParse(action.value);
      if (!parsed.success || parsed.data.language_id !== state.language_id) return {
        ...state, selected_sample: null, selected_result: null, error: 'Recording selection does not match the selected language.' };
      return { ...state, selected_sample: parsed.data, selected_result: null, error: null };
    }
    case 'result': {
      if (action.revision !== state.language_revision) return state;
      if (action.value === null) return { ...state, selected_result: null };
      const parsed = experimentSchema.safeParse(action.value);
      if (!parsed.success || parsed.data.language_id !== state.language_id
        || parsed.data.sample_id !== state.selected_sample?.sample_id) return {
        ...state, selected_result: null, error: 'Recording comparison is unavailable or does not match the current selection.' };
      return { ...state, selected_result: parsed.data, error: null };
    }
    case 'reset': return { ...initialSelection, language_revision: state.language_revision + 1 };
    case 'dismiss_error': return { ...state, error: null };
  }
}

type SelectionStore = { selection: Selection; selectLanguage: (value: string) => void;
  selectWard: (value: number | null) => void; setMetric: (value: string) => void;
  selectSample: (value: Sample | null, revision?: number) => void;
  acceptResult: (value: Experiment | null, revision?: number) => void;
  reset: () => void; dismissError: () => void };
const Context = createContext<SelectionStore | null>(null);
export function SelectionProvider({ children }: { children: ReactNode }) {
  const [selection, dispatch] = useReducer(selectionReducer, initialSelection);
  const value = useMemo<SelectionStore>(() => ({ selection,
    selectLanguage: value => dispatch({ type: 'language', value }),
    selectWard: value => dispatch({ type: 'ward', value }), setMetric: value => dispatch({ type: 'metric', value }),
    selectSample: (value, revision = selection.language_revision) => dispatch({ type: 'sample', value, revision }),
    acceptResult: (value, revision = selection.language_revision) => dispatch({ type: 'result', value, revision }),
    reset: () => dispatch({ type: 'reset' }), dismissError: () => dispatch({ type: 'dismiss_error' }),
  }), [selection]);
  return createElement(Context.Provider, { value }, children);
}
export function useSelection(): SelectionStore {
  const value = useContext(Context);
  if (!value) throw new Error('SelectionProvider is required');
  return value;
}

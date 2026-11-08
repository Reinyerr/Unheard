import type { Wards } from '../types/research';

type Position = [number, number];
type Polygon = Position[][];
export type WardGeometryFeature = {
  type: 'Feature'; id: number; properties: { ward_id: number; source_ward: string | number };
  geometry: { type: 'Polygon'; coordinates: Polygon } | { type: 'MultiPolygon'; coordinates: Polygon[] };
};
export type WardGeometry = { type: 'FeatureCollection'; schema_version: '1.0';
  features: WardGeometryFeature[]; source: Record<string, unknown>; bbox: number[] };
export type WardGeometryResult =
  | { status: 'ready'; geometry: WardGeometry; warnings: string[] }
  | { status: 'unavailable'; geometry: null; message: string };

const fallback = 'Ward map unavailable. Show the verified ward chart or table; no boundaries have been inferred.';
const idsMatch = (ids: number[]) => ids.length === 11 && [...ids].sort((a, b) => a - b).every((id, i) => id === i + 1);
const object = (value: unknown): value is Record<string, unknown> => typeof value === 'object' && value !== null && !Array.isArray(value);

/** Structural browser guard; topology and source provenance are checked offline by validate_wards.py. */
function parseGeometry(input: unknown): WardGeometry {
  if (!object(input) || input.type !== 'FeatureCollection' || input.schema_version !== '1.0'
    || 'crs' in input || !object(input.source) || !Array.isArray(input.features)
    || !Array.isArray(input.bbox) || input.bbox.length !== 4 || !input.bbox.every(Number.isFinite)) throw new Error(fallback);
  const ids: number[] = [];
  for (const feature of input.features) {
    if (!object(feature) || feature.type !== 'Feature' || !object(feature.properties)
      || !Number.isInteger(feature.id) || feature.id !== feature.properties.ward_id
      || !object(feature.geometry)) throw new Error(fallback);
    const geometry = feature.geometry;
    const polygons = geometry.type === 'Polygon' ? [geometry.coordinates]
      : geometry.type === 'MultiPolygon' ? geometry.coordinates : null;
    if (!Array.isArray(polygons) || polygons.length === 0) throw new Error(fallback);
    for (const polygon of polygons) {
      if (!Array.isArray(polygon) || polygon.length === 0) throw new Error(fallback);
      for (const ring of polygon) {
        if (!Array.isArray(ring) || ring.length < 4) throw new Error(fallback);
        for (const point of ring) {
          if (!Array.isArray(point) || point.length !== 2 || !point.every(n => typeof n === 'number' && Number.isFinite(n))
            || point[0] < -180 || point[0] > 180 || point[1] < -90 || point[1] > 90) throw new Error(fallback);
        }
        if (ring[0][0] !== ring.at(-1)[0] || ring[0][1] !== ring.at(-1)[1]) throw new Error(fallback);
      }
    }
    ids.push(feature.id as number);
  }
  if (!idsMatch(ids)) throw new Error(fallback);
  return input as unknown as WardGeometry;
}

/** Fail closed: a missing/failed/hash-mismatched geometry can never enable a choropleth. */
export async function loadWardGeometry(wards: Wards, signal?: AbortSignal): Promise<WardGeometryResult> {
  try {
    if (wards.is_fixture || !idsMatch(wards.wards.map(ward => ward.ward_id))) throw new Error(fallback);
    const base = import.meta.env.BASE_URL;
    const statusResponse = await fetch(`${base}data/ward_geometry_status.json`, { signal, cache: 'no-store' });
    if (!statusResponse.ok) throw new Error(fallback);
    const status: unknown = await statusResponse.json();
    if (!object(status) || status.schema_version !== '1.0' || status.status !== 'validated' || status.map_ready !== true
      || status.geometry_file !== 'mississauga_wards.geojson' || typeof status.geometry_sha256 !== 'string'
      || !Array.isArray(status.ward_ids) || !idsMatch(status.ward_ids)) throw new Error(fallback);
    const response = await fetch(`${base}data/mississauga_wards.geojson`, { signal, cache: 'no-store' });
    if (!response.ok) throw new Error(fallback);
    const bytes = await response.arrayBuffer();
    if (bytes.byteLength > 8 * 1024 * 1024) throw new Error(fallback);
    const digest = await crypto.subtle.digest('SHA-256', bytes);
    const hex = [...new Uint8Array(digest)].map(n => n.toString(16).padStart(2, '0')).join('');
    if (hex !== status.geometry_sha256) throw new Error(fallback);
    const geometry = parseGeometry(JSON.parse(new TextDecoder('utf-8', { fatal: true }).decode(bytes)));
    return { status: 'ready', geometry,
      warnings: Array.isArray(status.warnings) ? status.warnings.filter((value): value is string => typeof value === 'string') : [] };
  } catch {
    return { status: 'unavailable', geometry: null, message: fallback };
  }
}

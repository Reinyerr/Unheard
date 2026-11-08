import { useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import * as L from 'leaflet';
import type { FeatureCollection } from 'geojson';
import 'leaflet/dist/leaflet.css';
import type { WardGeometry } from '../../data/wardGeometry';
import type { MapMetric } from '../../types/research';
import WardTooltip from '../../components/WardTooltip';
import { fillColor, formatCount, formatShare, maximum, unavailableColor, type WardMetricRow } from './metrics';

type Props = { geometry: WardGeometry; rows: WardMetricRow[]; metric: MapMetric;
  selectedWard: number | null; onSelect: (id: number) => void; context: string; coverage: string;
  onUnavailable: () => void };

export default function WardMap({ geometry, rows, metric, selectedWard, onSelect, context, coverage, onUnavailable }: Props) {
  const container = useRef<HTMLDivElement>(null);
  const map = useRef<L.Map | null>(null);
  const layers = useRef(new Map<number, L.Path>());
  const bounds = useRef<L.LatLngBounds | null>(null);
  const callbacks = useRef({ onSelect, onUnavailable });
  callbacks.current = { onSelect, onUnavailable };
  const [targets, setTargets] = useState<{ id: number; element: HTMLElement }[]>([]);

  useEffect(() => {
    if (!container.current) return;
    let instance: L.Map | undefined;
    let observer: ResizeObserver | undefined;
    try {
      instance = L.map(container.current, { scrollWheelZoom: false, zoomAnimation: false,
        fadeAnimation: false, markerZoomAnimation: false, inertia: false, zoomSnap: 0.25, maxZoom: 17 });
      // Leaflet keyboard panning animates in JavaScript, outside CSS motion rules.
      // Keep every pan immediate, including keyboard and bounds adjustments.
      const panBy = instance.panBy.bind(instance);
      instance.panBy = (offset, options) => panBy(offset, { ...options, animate: false });
      map.current = instance;
      const portals: { id: number; element: HTMLElement }[] = [];
      const collection: FeatureCollection = { type: 'FeatureCollection', features: geometry.features };
      const polygons = L.geoJSON(collection, {
        style: { color: '#52766b', fillColor: unavailableColor, weight: 1.2, fillOpacity: 0.9 },
        onEachFeature(feature, layer) {
          const id = feature.properties.ward_id as number;
          const path = layer as L.Path;
          layers.current.set(id, path);
          const element = document.createElement('div');
          portals.push({ id, element });
          path.bindTooltip(element, { sticky: true, className: 'ward-map-tooltip', opacity: 1 });
          path.on('click', () => callbacks.current.onSelect(id));
          path.on('add', () => {
            const node = path.getElement();
            if (!node) return;
            node.setAttribute('tabindex', '0');
            node.setAttribute('role', 'button');
            node.setAttribute('aria-describedby', `ward-map-tooltip-${id}`);
            node.addEventListener('focus', () => path.openTooltip());
            node.addEventListener('blur', () => path.closeTooltip());
            node.addEventListener('keydown', event => {
              const key = (event as KeyboardEvent).key;
              if (key === 'Enter' || key === ' ') {
                event.preventDefault(); event.stopPropagation(); callbacks.current.onSelect(id);
              }
              if (key === 'Escape') path.closeTooltip();
            });
          });
        },
      }).addTo(instance);
      bounds.current = polygons.getBounds();
      instance.fitBounds(bounds.current, { padding: [20, 20], animate: false });
      instance.setMinZoom(instance.getZoom() - 1);
      instance.setMaxBounds(bounds.current.pad(0.2));
      instance.attributionControl.addAttribution('<a href="https://data.mississauga.ca/datasets/mississauga::ward-boundaries/about">City of Mississauga</a>');
      setTargets(portals);
      observer = new ResizeObserver(() => instance?.invalidateSize({ animate: false }));
      observer.observe(container.current);
    } catch {
      callbacks.current.onUnavailable();
    }
    return () => { observer?.disconnect(); instance?.remove(); map.current = null; layers.current.clear(); };
  }, [geometry]);

  useEffect(() => {
    const max = maximum(rows, metric);
    for (const row of rows) {
      const layer = layers.current.get(row.ward_id);
      layer?.setStyle({ fillColor: fillColor(row, metric, max),
        color: row.ward_id === selectedWard ? '#a64419' : '#52766b', weight: row.ward_id === selectedWard ? 3 : 1.2 });
      const node = layer?.getElement();
      node?.setAttribute('aria-pressed', String(row.ward_id === selectedWard));
      node?.setAttribute('aria-label', `Ward ${row.ward_id}; ${context}; ${formatCount(row.count)} home speakers; share ${formatShare(row.share)}; population language base ${formatCount(row.base)}`);
    }
  }, [rows, metric, selectedWard, context, targets]);

  return <div className="ward-map-frame">
    <div ref={container} className="ward-map-canvas" role="region" aria-label="Mississauga ward census map" />
    <button className="ward-reset" onClick={() => {
      if (bounds.current) map.current?.fitBounds(bounds.current, { padding: [20, 20], animate: false });
    }}>Reset map view</button>
    {targets.map(({ id, element }) => {
      const row = rows.find(row => row.ward_id === id);
      return row ? createPortal(<WardTooltip row={row} context={context} coverage={coverage} id={`ward-map-tooltip-${id}`} />, element, id) : null;
    })}
  </div>;
}

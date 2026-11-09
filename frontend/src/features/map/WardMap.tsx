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
  selectedWard: number | null; onSelect: (id: number | null) => void; context: string; coverage: string;
  onUnavailable: () => void };

export default function WardMap({ geometry, rows, metric, selectedWard, onSelect, context, coverage, onUnavailable }: Props) {
  const container = useRef<HTMLDivElement>(null);
  const map = useRef<L.Map | null>(null);
  const layers = useRef(new Map<number, L.Path>());
  const bases = useRef(new Map<number, L.Path>());
  const bounds = useRef<L.LatLngBounds | null>(null);
  const callbacks = useRef({ onSelect, onUnavailable });
  callbacks.current = { onSelect, onUnavailable };
  const [targets, setTargets] = useState<{ id: number; element: HTMLElement }[]>([]);

  useEffect(() => {
    if (!container.current) return;
    let instance: L.Map | undefined;
    let observer: ResizeObserver | undefined;
    try {
      // Individual SVG translation leaves Leaflet's pane transforms and the
      // verified source coordinates intact. Canvas cannot provide this effect.
      instance = L.map(container.current, { renderer: L.svg({ padding: .3 }), scrollWheelZoom: false,
        zoomAnimation: false, fadeAnimation: false, markerZoomAnimation: false,
        inertia: false, zoomSnap: .25, maxZoom: 17 });
      map.current = instance;
      const basePane = instance.createPane('wardBases');
      basePane.style.zIndex = '399';
      basePane.style.pointerEvents = 'none';
      const collection: FeatureCollection = { type: 'FeatureCollection', features: geometry.features };
      // Stationary decorative footprint, same geometry, no duplicate hit target.
      const baseRenderer = L.svg({ pane: 'wardBases', padding: .3 });
      L.geoJSON(collection, { pane: 'wardBases', interactive: false,
        style: { renderer: baseRenderer, color: '#791448', fillColor: '#46182f', weight: 2, opacity: 0, fillOpacity: 0 },
        onEachFeature(feature, layer) {
          const path = layer as L.Path;
          bases.current.set(feature.properties.ward_id as number, path);
          path.on('add', () => path.getElement()?.setAttribute('aria-hidden', 'true'));
        },
      }).addTo(instance);
      const portals: { id: number; element: HTMLElement }[] = [];
      const polygons = L.geoJSON(collection, {
        style: { color: '#93657e', fillColor: unavailableColor, weight: 1.2, fillOpacity: .9, className: 'ward-surface' },
        onEachFeature(feature, layer) {
          const id = feature.properties.ward_id as number;
          const path = layer as L.Path;
          layers.current.set(id, path);
          const element = document.createElement('div');
          portals.push({ id, element });
          path.bindTooltip(element, { sticky: true, className: 'ward-map-tooltip', opacity: 1 });
          const select = () => { path.closeTooltip(); callbacks.current.onSelect(id); };
          path.on('click', select);
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
              if (key === 'Enter' || key === ' ') { event.preventDefault(); event.stopPropagation(); select(); }
              if (key === 'Escape') { path.closeTooltip(); callbacks.current.onSelect(null); }
            });
          });
        },
      }).addTo(instance);
      bounds.current = polygons.getBounds();
      instance.fitBounds(bounds.current, { padding: [30, 30], animate: false });
      instance.setMinZoom(instance.getZoom() - 1);
      instance.setMaxBounds(bounds.current.pad(.4));
      instance.attributionControl.addAttribution('<a href="https://data.mississauga.ca/datasets/mississauga::ward-boundaries/about">City of Mississauga</a>');
      setTargets(portals);
      observer = new ResizeObserver(entries => {
        // Hidden acts remain mounted; refit only when this map has a real size.
        if (entries.some(entry => entry.contentRect.width > 0 && entry.contentRect.height > 0)) {
          instance?.invalidateSize({ animate: false, pan: false });
          if (bounds.current) instance?.fitBounds(bounds.current, { padding: [30, 30], animate: false });
        }
      });
      observer.observe(container.current);
    } catch { callbacks.current.onUnavailable(); }
    return () => {
      observer?.disconnect(); instance?.remove(); map.current = null;
      layers.current.clear(); bases.current.clear();
    };
  }, [geometry]);

  useEffect(() => {
    const max = maximum(rows, metric);
    for (const row of rows) {
      const selected = row.ward_id === selectedWard;
      const muted = selectedWard !== null && !selected;
      const layer = layers.current.get(row.ward_id);
      layer?.setStyle({ fillColor: fillColor(row, metric, max), fillOpacity: muted ? .24 : .94,
        color: selected ? '#ffe1f1' : muted ? '#584153' : '#ae7594', weight: selected ? 2.5 : 1.2 });
      bases.current.get(row.ward_id)?.setStyle({ opacity: selected ? 1 : 0, fillOpacity: selected ? 1 : 0 });
      const node = layer?.getElement();
      node?.classList.toggle('ward-raised', selected);
      node?.setAttribute('aria-pressed', String(selected));
      node?.setAttribute('aria-label', `Ward ${row.ward_id}; ${context}; ${formatCount(row.count)} home speakers; share ${formatShare(row.share)}; population language base ${formatCount(row.base)}`);
    }
    if (selectedWard !== null) layers.current.get(selectedWard)?.bringToFront();
  }, [rows, metric, selectedWard, context, targets]);

  return <div className="ward-map-frame" data-selected-ward={selectedWard ?? undefined}>
    <div ref={container} className="ward-map-canvas" role="region" aria-label="Mississauga ward census map" />
    <span className="map-instruction">{selectedWard === null ? 'Select a ward' : `Ward ${selectedWard} selected`}</span>
    <span className="map-coordinate-label">Mississauga · 2021 census</span>
    <button className="ward-reset" onClick={() => {
      onSelect(null);
      if (bounds.current) map.current?.fitBounds(bounds.current, { padding: [30, 30], animate: false });
    }}>{selectedWard === null ? 'Reset map view' : 'Clear and reset'}</button>
    {targets.map(({ id, element }) => {
      const row = rows.find(row => row.ward_id === id);
      return row ? createPortal(<WardTooltip row={row} context={context} coverage={coverage} id={`ward-map-tooltip-${id}`} />, element, id) : null;
    })}
  </div>;
}

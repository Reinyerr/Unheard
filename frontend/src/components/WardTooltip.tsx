import { formatCount, formatShare, type WardMetricRow } from '../features/map/metrics';

export default function WardTooltip({ row, context, coverage, id }: {
  row: WardMetricRow; context: string; coverage: string; id?: string;
}) {
  return <div id={id} className="ward-tooltip-content">
    <strong>Ward {row.ward_id}</strong>
    <p className="ward-tooltip-context">{context}</p>
    <dl>
      <div><dt>Home speakers</dt><dd>{formatCount(row.count)}</dd></div>
      <div><dt>Share of language base</dt><dd>{formatShare(row.share)}</dd></div>
      <div><dt>Population language base</dt><dd>{formatCount(row.base)}</dd></div>
    </dl>
    {row.base === null || row.base <= 0 ? <p>Share is unavailable because the denominator is missing or nonpositive.</p> : null}
    {row.count === null ? <p>This language count is unavailable in the supplied census categories.</p> : null}
    <p className="ward-tooltip-note">{coverage}</p>
  </div>;
}

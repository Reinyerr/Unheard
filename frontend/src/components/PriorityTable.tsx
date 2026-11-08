import type { Languages, LanguageId, Recommendations } from '../types/research';
import { formatCount } from '../features/map/metrics';

export default function PriorityTable({ data, languages, selected, onSelect }: {
  data: Recommendations; languages: Languages; selected: LanguageId | 'all'; onSelect: (id: string) => void;
}) {
  return <div className="priority-table-scroll" role="region" tabIndex={0} aria-label="Scrollable language evaluation priorities"><table className="priority-table">
    <caption>Language evaluation priorities · missing supplied task audio first, then home-language count</caption>
    <thead><tr><th scope="col">Priority</th><th scope="col">Language</th><th scope="col">Supplied request coverage</th><th scope="col">2021 city home speakers</th></tr></thead>
    <tbody>{[...data.items].sort((a, b) => a.rank - b.rank).map(item => <tr key={item.language_id}>
      <td>{item.rank}</td><th scope="row"><button type="button" aria-pressed={selected === item.language_id} onClick={() => onSelect(item.language_id)}>{languages.languages.find(row => row.language_id === item.language_id)?.display_name ?? item.language_id}</button></th>
      <td>No task-request audio in supplied subsets</td><td>{formatCount(item.city_home_speakers)}</td>
    </tr>)}</tbody>
  </table></div>;
}

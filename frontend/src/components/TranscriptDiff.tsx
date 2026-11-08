/** Raw-text grapheme diff for inspection, independent of exported normalized CER. */
function segments(text: string): string[] | null {
  if (typeof Intl.Segmenter !== 'function') return null;
  return [...new Intl.Segmenter(undefined, { granularity: 'grapheme' }).segment(text)].map(part => part.segment);
}
function compare(reference: string, output: string) {
  const a = segments(reference), b = segments(output);
  if (!a || !b || a.length * b.length > 250000) return null;
  const grid = Array.from({ length: a.length + 1 }, () => new Uint32Array(b.length + 1));
  for (let i = a.length - 1; i >= 0; i--) for (let j = b.length - 1; j >= 0; j--)
    grid[i][j] = a[i] === b[j] ? 1 + grid[i + 1][j + 1] : Math.max(grid[i + 1][j], grid[i][j + 1]);
  const left: { text: string; changed: boolean }[] = [], right: typeof left = [];
  function append(parts: typeof left, text: string, changed: boolean) {
    const last = parts.at(-1);
    if (last?.changed === changed) last.text += text;
    else parts.push({ text, changed });
  }
  let i = 0, j = 0;
  while (i < a.length || j < b.length) {
    if (i < a.length && j < b.length && a[i] === b[j]) {
      append(left, a[i++], false); append(right, b[j++], false);
    } else if (i < a.length && (j === b.length || grid[i + 1][j] >= grid[i][j + 1])) append(left, a[i++], true);
    else append(right, b[j++], true);
  }
  return { left, right };
}
export default function TranscriptDiff({ reference, output, direction, language }: {
  reference: string; output: string; direction: 'rtl' | 'ltr'; language: string;
}) {
  const diff = compare(reference, output);
  return <div className="transcript-diff">
    <p className="speech-note">Raw-text comparison: removed reference graphemes are struck through; added output graphemes are underlined. This display does not calculate CER or translate text.</p>
    {diff ? <>
      <p className="speech-note">Reference alignment</p>
      <p className="speech-transcript" dir={direction} lang={language}>{diff.left.map((part, i) => part.changed ? <del key={i}>{part.text}</del> : part.text)}</p>
      <p className="speech-note">Raw output alignment</p>
      <p className="speech-transcript" dir={direction} lang={language}>{output === '' ? <em>Empty recorded transcript</em> : diff.right.map((part, i) => part.changed ? <ins key={i}>{part.text}</ins> : part.text)}</p>
    </> : <><p className="speech-note">Highlighting unavailable for this browser or text length; unchanged raw output follows.</p><p className="speech-transcript" dir={direction} lang={language}>{output === '' ? 'Empty recorded transcript' : output}</p></>}
  </div>;
}

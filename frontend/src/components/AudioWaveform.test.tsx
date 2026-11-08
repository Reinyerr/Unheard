import { expect, it } from 'vitest';
import { waveformPeaks } from './AudioWaveform';
it('retains actual time-local peaks and silence across channels', () => {
  expect(waveformPeaks([new Float32Array([0, 0, -.5, .2]), new Float32Array([0, .75, 0, 0])], 2)).toEqual([.75, .5]);
  expect(waveformPeaks([])).toEqual([]);
  expect(waveformPeaks([new Float32Array([0, 0])])).toEqual([0, 0]);
});

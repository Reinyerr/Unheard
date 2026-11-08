import { act, fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import App, { API_BASE_URL } from './App';

describe('bootstrap shell (mocked health responses)', () => {
  it('connects using the health contract without accepting invalid research payloads', async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ status: 'ok', mode: 'local' }) });
    vi.stubGlobal('fetch', fetchMock);
    render(<App />);
    expect(await screen.findByText('Backend connected')).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith(`${API_BASE_URL}/health`, expect.objectContaining({ signal: expect.any(AbortSignal) }));
    expect(await screen.findAllByText(/Verified census\/coverage assets could not be loaded/)).not.toHaveLength(0);
    expect(screen.getByRole('navigation', { name: 'Research journey' })).toBeInTheDocument();
  });

  it('offers an actionable retry after network failure and recovers', async () => {
    let healthCalls = 0;
    vi.stubGlobal('fetch', vi.fn(async (url: string) => {
      if (url !== `${API_BASE_URL}/health` || healthCalls++ === 0) throw new Error('offline');
      return { ok: true, json: async () => ({ status: 'ok', mode: 'local' }) };
    }));
    render(<App />);
    expect(await screen.findByText('Backend unavailable')).toBeInTheDocument();
    expect(screen.getByText(/Start FastAPI/)).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Retry connection' }));
    expect(await screen.findByText('Backend connected')).toBeInTheDocument();
  });

  it.each([
    { ok: false, json: async () => ({ status: 'ok', mode: 'local' }) },
    { ok: true, json: async () => ({ status: 'ok' }) },
    { ok: true, json: async () => { throw new Error('invalid JSON'); } },
  ])('rejects HTTP errors and invalid responses', async (response) => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(response));
    render(<App />);
    expect(await screen.findByText('Backend unavailable')).toBeInTheDocument();
  });

  it('times out a stalled backend after five seconds', async () => {
    vi.useFakeTimers();
    vi.stubGlobal('fetch', vi.fn((_url, { signal }: RequestInit) => new Promise((_resolve, reject) => {
      signal?.addEventListener('abort', () => reject(new DOMException('Aborted', 'AbortError')));
    })));
    render(<App />);
    expect(screen.getByText('Checking backend…')).toBeInTheDocument();
    await act(async () => { await vi.advanceTimersByTimeAsync(5000); });
    expect(screen.getByText('Backend unavailable')).toBeInTheDocument();
  });
});

import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import '../api/client';
import { DemoService } from '../api/generated';

type SeedRecord = {
  case_id: string;
  document_id: string;
  created_at: string;
};

const STORAGE_KEY = 'nexusleo.demo.seeds.v1';

function loadSeeds(): SeedRecord[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as SeedRecord[];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function saveSeeds(seeds: SeedRecord[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(seeds));
}

export default function HomePage() {
  const [seeds, setSeeds] = useState<SeedRecord[]>(() => loadSeeds());
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    saveSeeds(seeds);
  }, [seeds]);

  const rows = useMemo(() => {
    const dedup = new Map<string, SeedRecord>();
    for (const s of seeds) dedup.set(s.case_id, s);
    return Array.from(dedup.values()).sort((a, b) => a.created_at.localeCompare(b.created_at));
  }, [seeds]);

  async function onSeed() {
    setBusy(true);
    setError(null);
    try {
      const res = await DemoService.demoSeedDemoSeedPost();
      const rec: SeedRecord = {
        case_id: res.case_id,
        document_id: res.document_id,
        created_at: new Date().toISOString(),
      };
      setSeeds((prev) => [rec, ...prev]);
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }

  function onClear() {
    setSeeds([]);
  }

  return (
    <div className="card">
      <h2>Cases</h2>
      <p>
        This UI is seed-based (no assumptions about list endpoints). Use the existing{' '}
        <span className="mono">POST /_demo/seed</span> flow to create a demo case and track it locally.
      </p>

      <div className="row" style={{ marginBottom: 12 }}>
        <button className="button button--primary" onClick={onSeed} disabled={busy}>
          Seed demo case
        </button>
        <button className="button" onClick={onClear} disabled={busy || rows.length === 0}>
          Clear local list
        </button>
      </div>

      {error && (
        <div className="card" style={{ borderColor: '#fecaca', background: '#fef2f2', marginBottom: 12 }}>
          <div style={{ color: '#991b1b' }} className="mono">
            {error}
          </div>
        </div>
      )}

      {rows.length === 0 ? (
        <div className="mono">No cases yet. Click “Seed demo case”.</div>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>Created</th>
              <th>Case ID</th>
              <th>Document ID</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.case_id}>
                <td className="mono">{r.created_at}</td>
                <td className="mono">{r.case_id}</td>
                <td className="mono">{r.document_id}</td>
                <td>
                  <Link to={`/cases/${r.case_id}`} className="mono" state={{ document_id: r.document_id }}>
                    Open
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <div style={{ marginTop: 16 }} className="mono">
        Backend expected at <span className="mono">http://localhost:8000</span>
      </div>
    </div>
  );
}

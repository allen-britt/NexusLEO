import { useEffect, useMemo, useState } from 'react';
import { Link, useLocation, useParams } from 'react-router-dom';
import '../api/client';
import { CasesService, ClaimsService } from '../api/generated';
import { stableStringify } from '../api/stableJson';

type LocationState = {
  document_id?: string;
};

export default function CasePage() {
  const { id } = useParams<{ id: string }>();
  const location = useLocation();
  const state = (location.state || {}) as LocationState;

  const caseId = id || '';

  const [documentId, setDocumentId] = useState<string>(state.document_id || '');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [claims, setClaims] = useState<unknown | null>(null);
  const [exportBundle, setExportBundle] = useState<unknown | null>(null);
  const [runResult, setRunResult] = useState<unknown | null>(null);

  useEffect(() => {
    setDocumentId(state.document_id || '');
  }, [state.document_id]);

  const canRun = useMemo(() => {
    return caseId.length > 0 && documentId.length > 0;
  }, [caseId, documentId]);

  async function onRun() {
    if (!caseId) return;
    setBusy(true);
    setError(null);
    setRunResult(null);
    try {
      const res = await CasesService.runCaseCasesCaseIdRunPost(caseId, { document_id: documentId });
      setRunResult(res);
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }

  async function onLoadClaims() {
    if (!caseId) return;
    setBusy(true);
    setError(null);
    setClaims(null);
    try {
      const res = await ClaimsService.listClaimsCasesCaseIdClaimsGet(caseId, 100, 0);
      setClaims(res);
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }

  async function onExport() {
    if (!caseId) return;
    setBusy(true);
    setError(null);
    setExportBundle(null);
    try {
      const res = await CasesService.exportCaseCasesCaseIdExportGet(caseId, 100, 0);
      setExportBundle(res);
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="card">
      <div style={{ marginBottom: 12 }}>
        <Link to="/" className="mono">
          ← Back
        </Link>
      </div>

      <h2>Case</h2>
      <div className="kv" style={{ marginBottom: 12 }}>
        <div>case_id</div>
        <div className="mono">{caseId}</div>
        <div>document_id</div>
        <div>
          <input
            className="mono"
            value={documentId}
            onChange={(e) => setDocumentId(e.target.value)}
            placeholder="(from seed)"
            style={{ width: '100%', padding: 8, borderRadius: 8, border: '1px solid #d1d5db' }}
          />
        </div>
      </div>

      <div className="row" style={{ marginBottom: 12 }}>
        <button className="button button--primary" onClick={onRun} disabled={!canRun || busy}>
          Run case
        </button>
        <button className="button" onClick={onLoadClaims} disabled={!caseId || busy}>
          View claims
        </button>
        <button className="button" onClick={onExport} disabled={!caseId || busy}>
          Export JSON
        </button>
      </div>

      {error && (
        <div className="card" style={{ borderColor: '#fecaca', background: '#fef2f2', marginBottom: 12 }}>
          <div style={{ color: '#991b1b' }} className="mono">
            {error}
          </div>
        </div>
      )}

      <section style={{ marginTop: 14 }}>
        <h3>Run response</h3>
        {runResult ? <pre className="pre mono">{stableStringify(runResult)}</pre> : <div className="mono">(not run)</div>}
      </section>

      <section style={{ marginTop: 14 }}>
        <h3>Claims</h3>
        {claims ? <pre className="pre mono">{stableStringify(claims)}</pre> : <div className="mono">(not loaded)</div>}
      </section>

      <section style={{ marginTop: 14 }}>
        <h3>Export bundle</h3>
        {exportBundle ? (
          <pre className="pre mono">{stableStringify(exportBundle)}</pre>
        ) : (
          <div className="mono">(not exported)</div>
        )}
      </section>
    </div>
  );
}

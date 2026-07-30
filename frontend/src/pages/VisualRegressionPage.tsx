import React, { useEffect, useState } from 'react';
import {
  compareImagesFormData,
  createBaselineFormData,
  fetchBaselineHistory,
  fetchBaselines,
  fetchVisualHistory,
  getArtifactImageUrl,
} from '../services/visualRegressionService';
import {
  VisualBaseline,
  VisualBaselineHistory,
  VisualComparisonRun,
} from '../types/visualRegression';

export const VisualRegressionPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'gallery' | 'baselines'>('gallery');
  const [comparisons, setComparisons] = useState<VisualComparisonRun[]>([]);
  const [baselines, setBaselines] = useState<VisualBaseline[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [severityFilter, setSeverityFilter] = useState<string>('ALL');
  const [browserFilter, setBrowserFilter] = useState<string>('ALL');
  const [moduleFilter, setModuleFilter] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');

  // Selected Comparison for Viewer Modal
  const [selectedComp, setSelectedComp] = useState<VisualComparisonRun | null>(null);
  const [viewerMode, setViewerMode] = useState<'sideBySide' | 'diff' | 'overlay' | 'heatmap' | 'boundingBox'>('sideBySide');
  const [overlaySlider, setOverlaySlider] = useState<number>(50);

  // Selected Baseline for History Modal
  const [selectedBaseline, setSelectedBaseline] = useState<VisualBaseline | null>(null);
  const [baselineHistory, setBaselineHistory] = useState<VisualBaselineHistory[]>([]);

  // Create Baseline Modal State
  const [showCreateModal, setShowCreateModal] = useState<boolean>(false);
  const [createForm, setCreateForm] = useState({
    projectId: '1',
    name: '',
    module: 'GENERAL',
    browser: 'chromium',
    viewportWidth: '1280',
    viewportHeight: '720',
    routePath: '/',
    captureType: 'VIEWPORT',
    elementSelector: '',
  });
  const [createFile, setCreateFile] = useState<File | null>(null);

  // Quick Run Comparison Modal State
  const [showCompareModal, setShowCompareModal] = useState<boolean>(false);
  const [compareForm, setCompareForm] = useState({
    projectId: '1',
    name: 'Manual Visual Comparison',
    module: 'GENERAL',
    browser: 'chromium',
    viewportWidth: '1280',
    viewportHeight: '720',
    routePath: '/',
  });
  const [compareFile, setCompareFile] = useState<File | null>(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const historyData = await fetchVisualHistory({
        severity: severityFilter !== 'ALL' ? severityFilter : undefined,
        browser: browserFilter !== 'ALL' ? browserFilter : undefined,
        module: moduleFilter !== 'ALL' ? moduleFilter : undefined,
        limit: 50,
      });
      setComparisons(historyData.comparisons);

      const baselineData = await fetchBaselines(undefined, moduleFilter !== 'ALL' ? moduleFilter : undefined, browserFilter !== 'ALL' ? browserFilter : undefined);
      setBaselines(baselineData);
    } catch (err: any) {
      setError(err.message || 'Failed to load visual regression data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [severityFilter, browserFilter, moduleFilter]);

  const handleOpenBaselineHistory = async (b: VisualBaseline) => {
    setSelectedBaseline(b);
    try {
      const hist = await fetchBaselineHistory(b.id);
      setBaselineHistory(hist);
    } catch (err) {
      console.error(err);
    }
  };

  const handleCreateBaselineSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!createForm.name) return;
    try {
      const formData = new FormData();
      formData.append('project_id', createForm.projectId);
      formData.append('name', createForm.name);
      formData.append('module', createForm.module);
      formData.append('browser', createForm.browser);
      formData.append('viewport_width', createForm.viewportWidth);
      formData.append('viewport_height', createForm.viewportHeight);
      formData.append('route_path', createForm.routePath);
      formData.append('capture_type', createForm.captureType);
      if (createForm.elementSelector) formData.append('element_selector', createForm.elementSelector);
      if (createFile) formData.append('file', createFile);

      await createBaselineFormData(formData);
      setShowCreateModal(false);
      setCreateFile(null);
      loadData();
    } catch (err: any) {
      alert(err.message || 'Failed to create baseline.');
    }
  };

  const handleCompareSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!compareFile) {
      alert('Please select an image file to compare.');
      return;
    }
    try {
      const formData = new FormData();
      formData.append('project_id', compareForm.projectId);
      formData.append('name', compareForm.name);
      formData.append('module', compareForm.module);
      formData.append('browser', compareForm.browser);
      formData.append('viewport_width', compareForm.viewportWidth);
      formData.append('viewport_height', compareForm.viewportHeight);
      formData.append('route_path', compareForm.routePath);
      formData.append('file', compareFile);

      const comp = await compareImagesFormData(formData);
      setShowCompareModal(false);
      setCompareFile(null);
      setSelectedComp(comp);
      loadData();
    } catch (err: any) {
      alert(err.message || 'Failed to execute comparison.');
    }
  };

  const filteredComparisons = comparisons.filter((c) => {
    if (searchQuery && !c.name.toLowerCase().includes(searchQuery.toLowerCase()) && !c.module.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }
    return true;
  });

  const criticalCount = comparisons.filter((c) => c.ai_severity === 'CRITICAL').length;
  const diffCount = comparisons.filter((c) => c.status === 'DIFF_DETECTED' || c.status === 'FAILED').length;
  const passCount = comparisons.filter((c) => c.status === 'PASSED').length;

  return (
    <div style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto', color: '#f8fafc', fontFamily: 'system-ui, -apple-system, sans-serif' }}>
      {/* Top Banner Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: '700', margin: 0, background: 'linear-gradient(90deg, #38bdf8, #818cf8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            Visual Regression Engine
          </h1>
          <p style={{ margin: '4px 0 0', color: '#94a3b8', fontSize: '14px' }}>
            Autonomous UI baseline comparison, pixel difference detection & AI visual defect analysis
          </p>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button
            onClick={() => setShowCompareModal(true)}
            style={{
              padding: '10px 18px',
              borderRadius: '8px',
              border: 'none',
              background: 'linear-gradient(135deg, #0284c7, #2563eb)',
              color: '#fff',
              fontWeight: '600',
              cursor: 'pointer',
              boxShadow: '0 4px 12px rgba(37,99,235,0.3)',
            }}
          >
            + Run Comparison
          </button>
          <button
            onClick={() => setShowCreateModal(true)}
            style={{
              padding: '10px 18px',
              borderRadius: '8px',
              border: '1px solid #334155',
              background: '#1e293b',
              color: '#f8fafc',
              fontWeight: '600',
              cursor: 'pointer',
            }}
          >
            + Create Baseline
          </button>
        </div>
      </div>

      {/* Metrics Cards Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', marginBottom: '28px' }}>
        <div style={{ background: '#1e293b', padding: '20px', borderRadius: '12px', border: '1px solid #334155' }}>
          <span style={{ fontSize: '12px', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Registered Baselines</span>
          <div style={{ fontSize: '32px', fontWeight: '700', color: '#38bdf8', marginTop: '6px' }}>{baselines.length}</div>
        </div>
        <div style={{ background: '#1e293b', padding: '20px', borderRadius: '12px', border: '1px solid #334155' }}>
          <span style={{ fontSize: '12px', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Diffs Detected</span>
          <div style={{ fontSize: '32px', fontWeight: '700', color: '#f59e0b', marginTop: '6px' }}>{diffCount}</div>
        </div>
        <div style={{ background: '#1e293b', padding: '20px', borderRadius: '12px', border: '1px solid #334155' }}>
          <span style={{ fontSize: '12px', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Critical Visual Regressions</span>
          <div style={{ fontSize: '32px', fontWeight: '700', color: '#ef4444', marginTop: '6px' }}>{criticalCount}</div>
        </div>
        <div style={{ background: '#1e293b', padding: '20px', borderRadius: '12px', border: '1px solid #334155' }}>
          <span style={{ fontSize: '12px', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Passing Baselines</span>
          <div style={{ fontSize: '32px', fontWeight: '700', color: '#10b981', marginTop: '6px' }}>{passCount}</div>
        </div>
      </div>

      {/* Tabs Header */}
      <div style={{ display: 'flex', borderBottom: '1px solid #334155', marginBottom: '20px', gap: '24px' }}>
        <button
          onClick={() => setActiveTab('gallery')}
          style={{
            padding: '12px 4px',
            background: 'none',
            border: 'none',
            borderBottom: activeTab === 'gallery' ? '3px solid #38bdf8' : '3px solid transparent',
            color: activeTab === 'gallery' ? '#38bdf8' : '#94a3b8',
            fontWeight: '600',
            fontSize: '15px',
            cursor: 'pointer',
          }}
        >
          Diff Gallery ({filteredComparisons.length})
        </button>
        <button
          onClick={() => setActiveTab('baselines')}
          style={{
            padding: '12px 4px',
            background: 'none',
            border: 'none',
            borderBottom: activeTab === 'baselines' ? '3px solid #38bdf8' : '3px solid transparent',
            color: activeTab === 'baselines' ? '#38bdf8' : '#94a3b8',
            fontWeight: '600',
            fontSize: '15px',
            cursor: 'pointer',
          }}
        >
          Baseline Repository ({baselines.length})
        </button>
      </div>

      {/* Filters Toolbar */}
      <div style={{ display: 'flex', gap: '12px', marginBottom: '24px', flexWrap: 'wrap', alignItems: 'center', background: '#0f172a', padding: '16px', borderRadius: '10px', border: '1px solid #1e293b' }}>
        <div style={{ flex: '1', minWidth: '200px' }}>
          <input
            type="text"
            placeholder="Search test name or module..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{ width: '100%', padding: '9px 14px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#fff', fontSize: '14px' }}
          />
        </div>

        <select
          value={severityFilter}
          onChange={(e) => setSeverityFilter(e.target.value)}
          style={{ padding: '9px 14px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#fff', fontSize: '14px' }}
        >
          <option value="ALL">Severity: All</option>
          <option value="COSMETIC">Cosmetic</option>
          <option value="MINOR">Minor</option>
          <option value="MEDIUM">Medium</option>
          <option value="CRITICAL">Critical</option>
        </select>

        <select
          value={browserFilter}
          onChange={(e) => setBrowserFilter(e.target.value)}
          style={{ padding: '9px 14px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#fff', fontSize: '14px' }}
        >
          <option value="ALL">Browser: All</option>
          <option value="chromium">Chromium</option>
          <option value="firefox">Firefox</option>
          <option value="webkit">WebKit</option>
        </select>

        <select
          value={moduleFilter}
          onChange={(e) => setModuleFilter(e.target.value)}
          style={{ padding: '9px 14px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#fff', fontSize: '14px' }}
        >
          <option value="ALL">Module: All</option>
          <option value="GENERAL">GENERAL</option>
          <option value="ERP">ERP</option>
          <option value="HRMS">HRMS</option>
          <option value="INVENTORY">INVENTORY</option>
          <option value="AUTHENTICATION">AUTHENTICATION</option>
          <option value="DASHBOARD">DASHBOARD</option>
        </select>

        <button onClick={loadData} style={{ padding: '9px 16px', borderRadius: '6px', border: '1px solid #334155', background: '#334155', color: '#fff', cursor: 'pointer' }}>
          Refresh
        </button>
      </div>

      {loading && <div style={{ padding: '40px', textAlign: 'center', color: '#94a3b8' }}>Loading visual regression data...</div>}
      {error && <div style={{ padding: '16px', background: '#450a0a', border: '1px solid #991b1b', borderRadius: '8px', color: '#fca5a5', marginBottom: '20px' }}>{error}</div>}

      {/* GALLERY TAB */}
      {activeTab === 'gallery' && !loading && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '20px' }}>
          {filteredComparisons.length === 0 ? (
            <div style={{ gridColumn: '1 / -1', padding: '48px', textAlign: 'center', background: '#1e293b', borderRadius: '12px', color: '#94a3b8' }}>
              No visual regression comparisons found matching your filters.
            </div>
          ) : (
            filteredComparisons.map((c) => (
              <div
                key={c.id}
                onClick={() => {
                  setSelectedComp(c);
                  setViewerMode('sideBySide');
                }}
                style={{
                  background: '#1e293b',
                  borderRadius: '12px',
                  border: c.ai_severity === 'CRITICAL' ? '1px solid #ef4444' : '1px solid #334155',
                  overflow: 'hidden',
                  cursor: 'pointer',
                  transition: 'transform 0.15s ease, box-shadow 0.15s ease',
                }}
                onMouseEnter={(e) => (e.currentTarget.style.transform = 'translateY(-2px)')}
                onMouseLeave={(e) => (e.currentTarget.style.transform = 'translateY(0)')}
              >
                {/* Thumbnail Header */}
                <div style={{ height: '180px', background: '#090d16', position: 'relative', overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <img
                    src={getArtifactImageUrl(c.id, 'bounding_box')}
                    alt={c.name}
                    style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                    onError={(e) => {
                      (e.target as HTMLElement).style.display = 'none';
                    }}
                  />
                  <div style={{ position: 'absolute', top: '10px', right: '10px', display: 'flex', gap: '6px' }}>
                    <span
                      style={{
                        padding: '4px 8px',
                        borderRadius: '4px',
                        fontSize: '11px',
                        fontWeight: '700',
                        background: c.ai_severity === 'CRITICAL' ? '#991b1b' : c.ai_severity === 'MEDIUM' ? '#9a3412' : c.ai_severity === 'MINOR' ? '#854d0e' : '#065f46',
                        color: '#fff',
                      }}
                    >
                      {c.ai_severity}
                    </span>
                    <span
                      style={{
                        padding: '4px 8px',
                        borderRadius: '4px',
                        fontSize: '11px',
                        fontWeight: '700',
                        background: c.status === 'PASSED' ? '#065f46' : '#991b1b',
                        color: '#fff',
                      }}
                    >
                      {c.status}
                    </span>
                  </div>
                </div>

                {/* Card Content */}
                <div style={{ padding: '16px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <span style={{ fontSize: '11px', textTransform: 'uppercase', color: '#38bdf8', fontWeight: '700' }}>{c.module}</span>
                    <span style={{ fontSize: '12px', color: '#94a3b8' }}>{c.browser} • {c.viewport_width}x{c.viewport_height}</span>
                  </div>
                  <h3 style={{ margin: '0 0 8px', fontSize: '16px', fontWeight: '600', color: '#f8fafc', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {c.name}
                  </h3>

                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', color: '#cbd5e1', marginTop: '12px', borderTop: '1px solid #334155', paddingTop: '10px' }}>
                    <span>Diff: <strong>{c.diff_percentage}%</strong> ({c.total_pixels_changed} px)</span>
                    <span>Confidence: <strong>{c.ai_confidence_score}%</strong></span>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* BASELINES TAB */}
      {activeTab === 'baselines' && !loading && (
        <div style={{ background: '#1e293b', borderRadius: '12px', border: '1px solid #334155', overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '14px' }}>
            <thead>
              <tr style={{ background: '#0f172a', borderBottom: '1px solid #334155', color: '#94a3b8' }}>
                <th style={{ padding: '14px 16px' }}>ID</th>
                <th style={{ padding: '14px 16px' }}>Baseline Name</th>
                <th style={{ padding: '14px 16px' }}>Module</th>
                <th style={{ padding: '14px 16px' }}>Browser</th>
                <th style={{ padding: '14px 16px' }}>Resolution</th>
                <th style={{ padding: '14px 16px' }}>Route</th>
                <th style={{ padding: '14px 16px' }}>Version</th>
                <th style={{ padding: '14px 16px' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {baselines.length === 0 ? (
                <tr>
                  <td colSpan={8} style={{ padding: '32px', textAlign: 'center', color: '#94a3b8' }}>
                    No baselines registered yet. Click "+ Create Baseline" to register one.
                  </td>
                </tr>
              ) : (
                baselines.map((b) => (
                  <tr key={b.id} style={{ borderBottom: '1px solid #334155' }}>
                    <td style={{ padding: '14px 16px', color: '#94a3b8' }}>#{b.id}</td>
                    <td style={{ padding: '14px 16px', fontWeight: '600', color: '#f8fafc' }}>{b.name}</td>
                    <td style={{ padding: '14px 16px' }}>
                      <span style={{ padding: '3px 8px', borderRadius: '4px', background: '#334155', fontSize: '12px', color: '#38bdf8' }}>{b.module}</span>
                    </td>
                    <td style={{ padding: '14px 16px', textTransform: 'capitalize' }}>{b.browser}</td>
                    <td style={{ padding: '14px 16px', color: '#94a3b8' }}>{b.viewport_width}x{b.viewport_height}</td>
                    <td style={{ padding: '14px 16px', color: '#cbd5e1' }}>{b.route_path}</td>
                    <td style={{ padding: '14px 16px' }}>
                      <span style={{ padding: '2px 8px', borderRadius: '12px', background: '#065f46', fontSize: '12px', fontWeight: '700', color: '#6ee7b7' }}>
                        v{b.version}
                      </span>
                    </td>
                    <td style={{ padding: '14px 16px' }}>
                      <button
                        onClick={() => handleOpenBaselineHistory(b)}
                        style={{ padding: '6px 12px', borderRadius: '6px', border: '1px solid #334155', background: '#0f172a', color: '#38bdf8', cursor: 'pointer', fontSize: '12px' }}
                      >
                        Version History
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* COMPARISON VIEWER MODAL */}
      {selectedComp && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.85)', backdropFilter: 'blur(4px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: '20px' }}>
          <div style={{ background: '#0f172a', borderRadius: '16px', border: '1px solid #334155', width: '100%', maxWidth: '1200px', maxHeight: '90vh', display: 'flex', flexDirection: 'column', overflow: 'hidden', boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)' }}>
            {/* Modal Header */}
            <div style={{ padding: '16px 24px', borderBottom: '1px solid #1e293b', display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#1e293b' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <h2 style={{ margin: 0, fontSize: '20px', fontWeight: '700', color: '#fff' }}>{selectedComp.name}</h2>
                  <span style={{ padding: '3px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: '700', background: selectedComp.ai_severity === 'CRITICAL' ? '#ef4444' : '#f59e0b', color: '#fff' }}>
                    {selectedComp.ai_severity}
                  </span>
                </div>
                <div style={{ fontSize: '13px', color: '#94a3b8', marginTop: '2px' }}>
                  {selectedComp.module} • {selectedComp.browser} • {selectedComp.viewport_width}x{selectedComp.viewport_height} • Baseline v{selectedComp.baseline_version}
                </div>
              </div>
              <button onClick={() => setSelectedComp(null)} style={{ background: 'none', border: 'none', color: '#94a3b8', fontSize: '24px', cursor: 'pointer' }}>
                ✕
              </button>
            </div>

            {/* Modal Subnav Viewer Modes */}
            <div style={{ padding: '12px 24px', background: '#090d16', borderBottom: '1px solid #1e293b', display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
              {[
                { key: 'sideBySide', label: 'Side-by-Side' },
                { key: 'diff', label: 'Pixel Diff' },
                { key: 'overlay', label: 'Overlay Slider' },
                { key: 'heatmap', label: 'Heatmap' },
                { key: 'boundingBox', label: 'Bounding Boxes' },
              ].map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => setViewerMode(tab.key as any)}
                  style={{
                    padding: '8px 16px',
                    borderRadius: '6px',
                    border: 'none',
                    background: viewerMode === tab.key ? '#0284c7' : '#1e293b',
                    color: viewerMode === tab.key ? '#fff' : '#94a3b8',
                    fontWeight: '600',
                    fontSize: '13px',
                    cursor: 'pointer',
                  }}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Modal Body / Image Stage */}
            <div style={{ flex: 1, padding: '24px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '24px' }}>
              {/* Image View Stage */}
              <div style={{ background: '#020617', borderRadius: '12px', border: '1px solid #1e293b', minHeight: '380px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '20px' }}>
                {viewerMode === 'sideBySide' && (
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', width: '100%' }}>
                    <div>
                      <div style={{ fontSize: '12px', fontWeight: '700', color: '#38bdf8', marginBottom: '8px', textAlign: 'center' }}>BASELINE IMAGE (v{selectedComp.baseline_version})</div>
                      <img src={getArtifactImageUrl(selectedComp.id, 'baseline')} alt="Baseline" style={{ width: '100%', borderRadius: '8px', border: '1px solid #334155' }} />
                    </div>
                    <div>
                      <div style={{ fontSize: '12px', fontWeight: '700', color: '#f59e0b', marginBottom: '8px', textAlign: 'center' }}>CURRENT EXECUTION IMAGE</div>
                      <img src={getArtifactImageUrl(selectedComp.id, 'current')} alt="Current" style={{ width: '100%', borderRadius: '8px', border: '1px solid #334155' }} />
                    </div>
                  </div>
                )}

                {viewerMode === 'diff' && (
                  <div style={{ width: '100%', textAlign: 'center' }}>
                    <div style={{ fontSize: '12px', fontWeight: '700', color: '#ef4444', marginBottom: '8px' }}>PIXEL DIFFERENCE HIGHLIGHT (RED = CHANGED PIXELS)</div>
                    <img src={getArtifactImageUrl(selectedComp.id, 'diff')} alt="Diff" style={{ maxWidth: '100%', maxHeight: '450px', borderRadius: '8px', border: '1px solid #334155' }} />
                  </div>
                )}

                {viewerMode === 'overlay' && (
                  <div style={{ width: '100%', textAlign: 'center' }}>
                    <div style={{ fontSize: '12px', fontWeight: '700', color: '#38bdf8', marginBottom: '12px' }}>
                      ALPHA BLEND OVERLAY ({overlaySlider}% Current / {100 - overlaySlider}% Baseline)
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="100"
                      value={overlaySlider}
                      onChange={(e) => setOverlaySlider(Number(e.target.value))}
                      style={{ width: '300px', marginBottom: '16px' }}
                    />
                    <div style={{ position: 'relative', width: '100%', maxWidth: '800px', margin: '0 auto' }}>
                      <img src={getArtifactImageUrl(selectedComp.id, 'overlay')} alt="Overlay" style={{ width: '100%', borderRadius: '8px', border: '1px solid #334155', opacity: overlaySlider / 100 }} />
                    </div>
                  </div>
                )}

                {viewerMode === 'heatmap' && (
                  <div style={{ width: '100%', textAlign: 'center' }}>
                    <div style={{ fontSize: '12px', fontWeight: '700', color: '#f97316', marginBottom: '8px' }}>DIFF INTENSITY HEATMAP</div>
                    <img src={getArtifactImageUrl(selectedComp.id, 'heatmap')} alt="Heatmap" style={{ maxWidth: '100%', maxHeight: '450px', borderRadius: '8px', border: '1px solid #334155' }} />
                  </div>
                )}

                {viewerMode === 'boundingBox' && (
                  <div style={{ width: '100%', textAlign: 'center' }}>
                    <div style={{ fontSize: '12px', fontWeight: '700', color: '#a855f7', marginBottom: '8px' }}>STRUCTURAL BOUNDING BOX REGIONS</div>
                    <img src={getArtifactImageUrl(selectedComp.id, 'bounding_box')} alt="Bounding Boxes" style={{ maxWidth: '100%', maxHeight: '450px', borderRadius: '8px', border: '1px solid #334155' }} />
                  </div>
                )}
              </div>

              {/* AI Visual Analysis Card */}
              <div style={{ background: '#1e293b', borderRadius: '12px', padding: '20px', border: '1px solid #334155' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', borderBottom: '1px solid #334155', paddingBottom: '12px' }}>
                  <h3 style={{ margin: 0, fontSize: '16px', color: '#38bdf8', fontWeight: '700' }}>AI Visual Analysis Report</h3>
                  <span style={{ fontSize: '14px', color: '#10b981', fontWeight: '700' }}>AI Confidence: {selectedComp.ai_confidence_score}%</span>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                  <div>
                    <h4 style={{ margin: '0 0 6px', fontSize: '13px', color: '#94a3b8', textTransform: 'uppercase' }}>Root Cause Diagnosis</h4>
                    <p style={{ margin: 0, color: '#f8fafc', fontSize: '14px', lineHeight: '1.5', background: '#0f172a', padding: '12px', borderRadius: '8px', border: '1px solid #334155' }}>
                      {selectedComp.ai_root_cause || 'No root cause available.'}
                    </p>
                  </div>
                  <div>
                    <h4 style={{ margin: '0 0 6px', fontSize: '13px', color: '#94a3b8', textTransform: 'uppercase' }}>Actionable Recommendation</h4>
                    <p style={{ margin: 0, color: '#6ee7b7', fontSize: '14px', lineHeight: '1.5', background: '#064e3b', padding: '12px', borderRadius: '8px', border: '1px solid #047857' }}>
                      {selectedComp.ai_recommendation || 'No recommendation available.'}
                    </p>
                  </div>
                </div>

                {/* Metrics Breakdown Grid */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '12px', marginTop: '20px', paddingTop: '16px', borderTop: '1px solid #334155' }}>
                  <div style={{ background: '#0f172a', padding: '10px', borderRadius: '6px', textAlign: 'center' }}>
                    <div style={{ fontSize: '11px', color: '#94a3b8' }}>Layout Shifts</div>
                    <div style={{ fontSize: '18px', fontWeight: '700', color: '#f8fafc' }}>{selectedComp.layout_shifts}</div>
                  </div>
                  <div style={{ background: '#0f172a', padding: '10px', borderRadius: '6px', textAlign: 'center' }}>
                    <div style={{ fontSize: '11px', color: '#94a3b8' }}>Missing Elements</div>
                    <div style={{ fontSize: '18px', fontWeight: '700', color: '#f8fafc' }}>{selectedComp.missing_elements_count}</div>
                  </div>
                  <div style={{ background: '#0f172a', padding: '10px', borderRadius: '6px', textAlign: 'center' }}>
                    <div style={{ fontSize: '11px', color: '#94a3b8' }}>Color Changes</div>
                    <div style={{ fontSize: '18px', fontWeight: '700', color: '#f8fafc' }}>{selectedComp.color_changes_count}</div>
                  </div>
                  <div style={{ background: '#0f172a', padding: '10px', borderRadius: '6px', textAlign: 'center' }}>
                    <div style={{ fontSize: '11px', color: '#94a3b8' }}>Font Changes</div>
                    <div style={{ fontSize: '18px', fontWeight: '700', color: '#f8fafc' }}>{selectedComp.font_changes_count}</div>
                  </div>
                  <div style={{ background: '#0f172a', padding: '10px', borderRadius: '6px', textAlign: 'center' }}>
                    <div style={{ fontSize: '11px', color: '#94a3b8' }}>Icon Changes</div>
                    <div style={{ fontSize: '18px', fontWeight: '700', color: '#f8fafc' }}>{selectedComp.icon_changes_count}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* BASELINE HISTORY MODAL */}
      {selectedBaseline && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.85)', backdropFilter: 'blur(4px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: '20px' }}>
          <div style={{ background: '#0f172a', borderRadius: '16px', border: '1px solid #334155', width: '100%', maxWidth: '750px', padding: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', borderBottom: '1px solid #1e293b', paddingBottom: '12px' }}>
              <h2 style={{ margin: 0, fontSize: '18px', color: '#fff' }}>Baseline Version History: {selectedBaseline.name}</h2>
              <button onClick={() => setSelectedBaseline(null)} style={{ background: 'none', border: 'none', color: '#94a3b8', fontSize: '20px', cursor: 'pointer' }}>✕</button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', maxHeight: '400px', overflowY: 'auto' }}>
              {baselineHistory.map((h) => (
                <div key={h.id} style={{ background: '#1e293b', padding: '14px', borderRadius: '8px', border: '1px solid #334155', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                      <span style={{ padding: '2px 8px', borderRadius: '12px', background: '#065f46', color: '#6ee7b7', fontSize: '12px', fontWeight: '700' }}>Version {h.version}</span>
                      <span style={{ fontSize: '12px', color: '#94a3b8' }}>{new Date(h.created_at).toLocaleString()}</span>
                    </div>
                    <p style={{ margin: '6px 0 0', fontSize: '13px', color: '#cbd5e1' }}>{h.change_summary || 'No summary notes.'}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* CREATE BASELINE MODAL */}
      {showCreateModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.85)', backdropFilter: 'blur(4px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: '20px' }}>
          <div style={{ background: '#0f172a', borderRadius: '16px', border: '1px solid #334155', width: '100%', maxWidth: '560px', padding: '24px' }}>
            <h2 style={{ margin: '0 0 16px', fontSize: '20px', color: '#fff' }}>Register New Visual Baseline</h2>
            <form onSubmit={handleCreateBaselineSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label style={{ fontSize: '12px', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Baseline Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. ERP Dashboard Navigation Header"
                  value={createForm.name}
                  onChange={(e) => setCreateForm({ ...createForm, name: e.target.value })}
                  style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#fff' }}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div>
                  <label style={{ fontSize: '12px', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Module</label>
                  <select
                    value={createForm.module}
                    onChange={(e) => setCreateForm({ ...createForm, module: e.target.value })}
                    style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#fff' }}
                  >
                    <option value="GENERAL">GENERAL</option>
                    <option value="ERP">ERP</option>
                    <option value="HRMS">HRMS</option>
                    <option value="INVENTORY">INVENTORY</option>
                    <option value="AUTHENTICATION">AUTHENTICATION</option>
                    <option value="DASHBOARD">DASHBOARD</option>
                  </select>
                </div>
                <div>
                  <label style={{ fontSize: '12px', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Browser Target</label>
                  <select
                    value={createForm.browser}
                    onChange={(e) => setCreateForm({ ...createForm, browser: e.target.value })}
                    style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#fff' }}
                  >
                    <option value="chromium">Chromium</option>
                    <option value="firefox">Firefox</option>
                    <option value="webkit">WebKit</option>
                  </select>
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div>
                  <label style={{ fontSize: '12px', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Viewport Width</label>
                  <input
                    type="number"
                    value={createForm.viewportWidth}
                    onChange={(e) => setCreateForm({ ...createForm, viewportWidth: e.target.value })}
                    style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#fff' }}
                  />
                </div>
                <div>
                  <label style={{ fontSize: '12px', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Viewport Height</label>
                  <input
                    type="number"
                    value={createForm.viewportHeight}
                    onChange={(e) => setCreateForm({ ...createForm, viewportHeight: e.target.value })}
                    style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#fff' }}
                  />
                </div>
              </div>

              <div>
                <label style={{ fontSize: '12px', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Route Path</label>
                <input
                  type="text"
                  value={createForm.routePath}
                  onChange={(e) => setCreateForm({ ...createForm, routePath: e.target.value })}
                  style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#fff' }}
                />
              </div>

              <div>
                <label style={{ fontSize: '12px', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Baseline Image File (PNG)</label>
                <input
                  type="file"
                  accept="image/png,image/jpeg"
                  onChange={(e) => setCreateFile(e.target.files ? e.target.files[0] : null)}
                  style={{ width: '100%', padding: '8px', color: '#94a3b8' }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '12px' }}>
                <button type="button" onClick={() => setShowCreateModal(false)} style={{ padding: '9px 16px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#fff' }}>
                  Cancel
                </button>
                <button type="submit" style={{ padding: '9px 16px', borderRadius: '6px', border: 'none', background: '#0284c7', color: '#fff', fontWeight: '600' }}>
                  Save Baseline
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* QUICK COMPARISON MODAL */}
      {showCompareModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.85)', backdropFilter: 'blur(4px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: '20px' }}>
          <div style={{ background: '#0f172a', borderRadius: '16px', border: '1px solid #334155', width: '100%', maxWidth: '520px', padding: '24px' }}>
            <h2 style={{ margin: '0 0 16px', fontSize: '20px', color: '#fff' }}>Execute Visual Comparison</h2>
            <form onSubmit={handleCompareSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label style={{ fontSize: '12px', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Test Name</label>
                <input
                  type="text"
                  required
                  value={compareForm.name}
                  onChange={(e) => setCompareForm({ ...compareForm, name: e.target.value })}
                  style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#fff' }}
                />
              </div>

              <div>
                <label style={{ fontSize: '12px', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Upload Current Execution Screenshot (PNG)</label>
                <input
                  type="file"
                  required
                  accept="image/png,image/jpeg"
                  onChange={(e) => setCompareFile(e.target.files ? e.target.files[0] : null)}
                  style={{ width: '100%', padding: '8px', color: '#94a3b8' }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '12px' }}>
                <button type="button" onClick={() => setShowCompareModal(false)} style={{ padding: '9px 16px', borderRadius: '6px', border: '1px solid #334155', background: '#1e293b', color: '#fff' }}>
                  Cancel
                </button>
                <button type="submit" style={{ padding: '9px 16px', borderRadius: '6px', border: 'none', background: '#0284c7', color: '#fff', fontWeight: '600' }}>
                  Compare & Analyze
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

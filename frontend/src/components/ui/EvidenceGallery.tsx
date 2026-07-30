import React, { useState } from 'react';
import { Image as ImageIcon, Video, FileText, Download, Eye, X } from 'lucide-react';

export interface EvidenceItem {
  id: number | string;
  name: string;
  type: 'screenshot' | 'video' | 'trace' | 'log' | string;
  url: string;
  sizeBytes?: number;
  timestamp?: string;
}

interface EvidenceGalleryProps {
  items: EvidenceItem[];
}

export function EvidenceGallery({ items }: EvidenceGalleryProps) {
  const [selectedItem, setSelectedItem] = useState<EvidenceItem | null>(null);

  if (!items || items.length === 0) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.875rem' }}>
        No evidence artifacts attached to this run.
      </div>
    );
  }

  const getIcon = (type: string) => {
    const t = type.toLowerCase();
    if (t.includes('image') || t.includes('screenshot')) return <ImageIcon size={20} style={{ color: 'var(--color-accent)' }} />;
    if (t.includes('video')) return <Video size={20} style={{ color: 'var(--color-primary)' }} />;
    return <FileText size={20} style={{ color: 'var(--color-warning)' }} />;
  };

  return (
    <div>
      <div className="grid grid-cols-3">
        {items.map((item) => (
          <div key={item.id} className="card" style={{ padding: '0.875rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                {getIcon(item.type)}
                <span style={{ fontWeight: 600, fontSize: '0.85rem', color: 'var(--text-main)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: '140px' }} title={item.name}>
                  {item.name}
                </span>
              </div>
              <span style={{ fontSize: '0.7rem', padding: '0.15rem 0.4rem', borderRadius: 'var(--radius-sm)', background: 'var(--bg-card-subtle)', color: 'var(--text-muted)' }}>
                {item.type.toUpperCase()}
              </span>
            </div>

            {item.type.toLowerCase().includes('screenshot') || item.type.toLowerCase().includes('image') ? (
              <div 
                onClick={() => setSelectedItem(item)}
                style={{ height: '120px', borderRadius: 'var(--radius-md)', overflow: 'hidden', cursor: 'pointer', background: '#000', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px solid var(--border-color)' }}
              >
                <img src={item.url} alt={item.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} onError={(e) => { (e.target as HTMLElement).style.display = 'none'; }} />
              </div>
            ) : (
              <div style={{ height: '120px', borderRadius: 'var(--radius-md)', background: 'var(--bg-app)', border: '1px solid var(--border-color)', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
                {getIcon(item.type)}
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{item.name}</span>
              </div>
            )}

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '0.25rem' }}>
              <button className="btn btn-ghost btn-sm" onClick={() => setSelectedItem(item)}>
                <Eye size={13} />
                Preview
              </button>
              <a href={item.url} download target="_blank" rel="noreferrer" className="btn btn-secondary btn-sm">
                <Download size={13} />
                Download
              </a>
            </div>
          </div>
        ))}
      </div>

      {selectedItem && (
        <div className="modal-overlay" onClick={() => setSelectedItem(null)}>
          <div className="modal-content" style={{ maxWidth: '800px' }} onClick={(e) => e.stopPropagation()}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
              <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-main)' }}>{selectedItem.name}</h3>
              <button className="btn btn-ghost btn-sm" onClick={() => setSelectedItem(null)}>
                <X size={16} />
              </button>
            </div>

            <div style={{ textAlign: 'center', backgroundColor: '#000', padding: '1rem', borderRadius: 'var(--radius-md)', maxHeight: '70vh', overflow: 'auto' }}>
              {selectedItem.type.toLowerCase().includes('video') ? (
                <video src={selectedItem.url} controls style={{ maxWidth: '100%', maxHeight: '60vh' }} />
              ) : selectedItem.type.toLowerCase().includes('screenshot') || selectedItem.type.toLowerCase().includes('image') ? (
                <img src={selectedItem.url} alt={selectedItem.name} style={{ maxWidth: '100%', maxHeight: '60vh', objectFit: 'contain' }} />
              ) : (
                <iframe src={selectedItem.url} style={{ width: '100%', height: '400px', border: 'none', background: '#fff' }} title="Preview" />
              )}
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '1rem' }}>
              <a href={selectedItem.url} download target="_blank" rel="noreferrer" className="btn btn-primary">
                <Download size={14} />
                Download File
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

import { useUIStore } from '../stores/uiStore';
import { useHotkey } from '@tanstack/react-hotkeys';
import { Search } from 'lucide-react';
import { useState, useEffect, useRef } from 'react';

export function SearchPalette() {
  const isOpen = useUIStore((s) => s.searchModalOpen);
  const setOpen = useUIStore((s) => s.setSearchModalOpen);
  const [query, setQuery] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  // Close on Escape
  useHotkey('Escape', () => {
    if (isOpen) {
      setOpen(false);
    }
  });

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    } else {
      setQuery('');
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div 
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        backdropFilter: 'blur(4px)',
        zIndex: 9999,
        display: 'flex',
        alignItems: 'flex-start',
        justifyContent: 'center',
        paddingTop: '10vh'
      }}
      onClick={() => setOpen(false)}
    >
      <div 
        style={{
          width: '100%',
          maxWidth: 600,
          backgroundColor: "#09090b",
          borderRadius: 'var(--ws-r-lg)',
          boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
          overflow: 'hidden',
          border: '1px solid var(--ws-edge-soft)'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{ display: 'flex', alignItems: 'center', padding: '16px 20px', borderBottom: '1px solid var(--ws-edge-soft)' }}>
          <Search size={20} style={{ color: "#71717a", marginRight: 12 }} />
          <input
            ref={inputRef}
            type="text"
            placeholder="Search commands, documents, and workflows..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            style={{
              flex: 1,
              background: 'transparent',
              border: 'none',
              outline: 'none',
              fontSize: 16,
              color: "#f4f4f5",
            }}
          />
          <div style={{ display: 'flex', gap: 4 }}>
            <kbd style={{ fontSize: 12, padding: '2px 6px', background: 'var(--ws-surface)', border: '1px solid var(--ws-edge-soft)', borderRadius: 4, color: "#71717a" }}>ESC</kbd>
          </div>
        </div>

        <div style={{ padding: 16 }}>
          <p style={{ color: "#71717a", fontSize: 13, margin: 0, textAlign: 'center' }}>
            No recent searches. Try searching for "React" or "Design Patterns".
          </p>
        </div>
      </div>
    </div>
  );
}

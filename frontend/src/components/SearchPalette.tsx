import { useUIStore } from '../stores/uiStore';
import { useHotkey } from '@tanstack/react-hotkeys';
import { Search } from 'lucide-react';
import { useState, useEffect, useRef } from 'react';
import { ModalShell } from './ModalShell';

export function SearchPalette() {
  const isOpen = useUIStore((s) => s.searchModalOpen);
  const setOpen = useUIStore((s) => s.setSearchModalOpen);
  const [query, setQuery] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

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

  return (
    <ModalShell open={isOpen} onClose={() => setOpen(false)} title="Search" maxWidth={600} showEscBadge>
      <div style={{ display: 'flex', alignItems: 'center', padding: '16px 20px', borderBottom: '1px solid var(--ws-line)' }}>
        <Search size={20} style={{ color: "var(--ws-muted)", marginRight: 12 }} />
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
            color: "var(--ws-ink)",
          }}
        />
      </div>

      <div style={{ padding: '0 20px 20px' }}>
        <p style={{ color: "var(--ws-muted)", fontSize: 13, margin: 0, textAlign: 'center' }}>
          No recent searches. Try searching for "React" or "Design Patterns".
        </p>
      </div>
    </ModalShell>
  );
}

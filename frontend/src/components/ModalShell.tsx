import type { ReactNode } from 'react'
import { X } from 'lucide-react'

interface ModalShellProps {
  open: boolean
  onClose: () => void
  title: string
  children: ReactNode
  maxWidth?: number
  showEscBadge?: boolean
}

export function ModalShell({
  open,
  onClose,
  title,
  children,
  maxWidth = 420,
  showEscBadge = false,
}: ModalShellProps) {
  if (!open) return null

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 9999,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 16,
      }}
    >
      <div
        onClick={onClose}
        style={{
          position: 'absolute',
          inset: 0,
          background: 'rgba(0, 0, 0, 0.5)',
          backdropFilter: 'blur(4px)',
        }}
      />
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          position: 'relative',
          zIndex: 1,
          width: '100%',
          maxWidth,
          background: 'var(--ws-surface)',
          border: '1px solid var(--ws-line-strong)',
          borderRadius: 8,
          boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 10px 10px -5px rgba(0, 0, 0, 0.4)',
          padding: 20,
        }}
      >
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: 16,
        }}>
          <h2 style={{
            margin: 0,
            fontSize: 16,
            fontWeight: 700,
            color: 'var(--ws-ink)',
            flex: 1,
          }}>{title}</h2>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            {showEscBadge && (
              <kbd style={{
                fontSize: 11,
                padding: '2px 6px',
                background: 'var(--ws-surface)',
                border: '1px solid var(--ws-line)',
                borderRadius: 4,
                color: 'var(--ws-muted)',
              }}>ESC</kbd>
            )}
            <button
              type="button"
              onClick={onClose}
              style={{
                background: 'none',
                border: 'none',
                color: 'var(--ws-muted)',
                cursor: 'pointer',
                display: 'flex',
                padding: 4,
                borderRadius: 4,
              }}
              onMouseEnter={e => (e.currentTarget.style.color = 'var(--ws-ink)')}
              onMouseLeave={e => (e.currentTarget.style.color = 'var(--ws-muted)')}
            >
              <X size={16} />
            </button>
          </div>
        </div>
        {children}
      </div>
    </div>
  )
}

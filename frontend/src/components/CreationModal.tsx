import { X } from 'lucide-react';
import { useUIStore } from '../stores/uiStore';
import { useWorkspaceStore } from '../stores/workspaceStore';

export function CreationModal() {
  const modal = useUIStore(s => s.creationModal);
  const setModal = useUIStore(s => s.setCreationModal);
  const modalName = useUIStore(s => s.modalName);
  const setModalName = useUIStore(s => s.setModalName);
  const modalDesc = useUIStore(s => s.modalDesc);
  const setModalDesc = useUIStore(s => s.setModalDesc);

  const addDomain = useWorkspaceStore(s => s.addDomain);
  const addSubject = useWorkspaceStore(s => s.addSubject);
  const addChapter = useWorkspaceStore(s => s.addChapter);
  const addTopic = useWorkspaceStore(s => s.addTopic);

  if (!modal || !modal.open) return null;

  const handleClose = () => {
    setModal(null);
    setModalName('');
    setModalDesc('');
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!modalName.trim()) return;

    if (modal.type === 'domain') {
      addDomain(modalName.trim());
    } else if (modal.type === 'subject' && modal.domainId) {
      addSubject(modal.domainId, modalName.trim(), modalDesc.trim());
    } else if (modal.type === 'chapter' && modal.domainId && modal.subjectId) {
      addChapter(modal.domainId, modal.subjectId, modalName.trim(), modalDesc.trim());
    } else if (modal.type === 'topic' && modal.domainId && modal.subjectId && modal.chapterId) {
      addTopic(modal.domainId, modal.subjectId, modal.chapterId, modalName.trim());
    }

    handleClose();
  };

  const title = `New ${modal.type.charAt(0).toUpperCase() + modal.type.slice(1)}`;

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      zIndex: 9999,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: 16,
    }}>
      {/* Backdrop */}
      <div 
        onClick={handleClose}
        style={{
          position: 'absolute',
          inset: 0,
          background: 'rgba(5, 5, 5, 0.75)',
          backdropFilter: 'blur(4px)',
        }} 
      />

      {/* Modal Content */}
      <div style={{
        position: 'relative',
        zIndex: 1,
        width: '100%',
        maxWidth: 420,
        background: 'var(--ws-surface)',
        border: '1px solid var(--ws-line-strong)',
        borderRadius: 8,
        boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 10px 10px -5px rgba(0, 0, 0, 0.4)',
        padding: 20,
      }}>
        {/* Header */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'between',
          marginBottom: 16,
        }}>
          <h2 style={{
            margin: 0,
            fontSize: 16,
            fontWeight: 700,
            color: 'var(--ws-ink)',
            flex: 1,
          }}>{title}</h2>
          <button 
            type="button"
            onClick={handleClose}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--ws-muted)',
              cursor: 'pointer',
              display: 'flex',
              padding: 4,
              borderRadius: 4,
            }}
            onMouseEnter={e => e.currentTarget.style.color = 'var(--ws-ink)'}
            onMouseLeave={e => e.currentTarget.style.color = 'var(--ws-muted)'}
          >
            <X size={16} />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            <label style={{ fontSize: 11, fontWeight: 600, color: 'var(--ws-soft)', textTransform: 'uppercase', letterSpacing: 0.5 }}>Name</label>
            <input 
              type="text"
              required
              autoFocus
              value={modalName}
              onChange={e => setModalName(e.target.value)}
              placeholder={`Enter ${modal.type} name...`}
              style={{
                width: '100%',
                padding: '8px 12px',
                background: 'var(--ws-bg)',
                border: '1px solid var(--ws-line)',
                borderRadius: 6,
                color: 'var(--ws-ink)',
                fontSize: 13,
                outline: 'none',
              }}
              onFocus={e => e.currentTarget.style.borderColor = 'var(--ws-accent)'}
              onBlur={e => e.currentTarget.style.borderColor = 'var(--ws-line)'}
            />
          </div>

          {(modal.type === 'subject' || modal.type === 'chapter') && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              <label style={{ fontSize: 11, fontWeight: 600, color: 'var(--ws-soft)', textTransform: 'uppercase', letterSpacing: 0.5 }}>Description</label>
              <textarea 
                value={modalDesc}
                onChange={e => setModalDesc(e.target.value)}
                placeholder="Optional description..."
                rows={3}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  background: 'var(--ws-bg)',
                  border: '1px solid var(--ws-line)',
                  borderRadius: 6,
                  color: 'var(--ws-ink)',
                  fontSize: 13,
                  outline: 'none',
                  resize: 'none',
                }}
                onFocus={e => e.currentTarget.style.borderColor = 'var(--ws-accent)'}
                onBlur={e => e.currentTarget.style.borderColor = 'var(--ws-line)'}
              />
            </div>
          )}

          {/* Footer Actions */}
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10, marginTop: 6 }}>
            <button 
              type="button"
              onClick={handleClose}
              style={{
                padding: '8px 16px',
                background: 'transparent',
                border: '1px solid var(--ws-line)',
                borderRadius: 6,
                color: 'var(--ws-soft)',
                fontSize: 12,
                fontWeight: 600,
                cursor: 'pointer',
              }}
              onMouseEnter={e => e.currentTarget.style.color = 'var(--ws-ink)'}
              onMouseLeave={e => e.currentTarget.style.color = 'var(--ws-soft)'}
            >
              Cancel
            </button>
            <button 
              type="submit"
              style={{
                padding: '8px 16px',
                background: 'var(--ws-accent)',
                border: 'none',
                borderRadius: 6,
                color: 'var(--ws-bg)',
                fontSize: 12,
                fontWeight: 700,
                cursor: 'pointer',
              }}
              onMouseEnter={e => e.currentTarget.style.opacity = '0.9'}
              onMouseLeave={e => e.currentTarget.style.opacity = '1'}
            >
              Create
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

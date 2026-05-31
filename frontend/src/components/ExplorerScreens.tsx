import {Plus, Folder, FileText, ArrowLeft, Pin, Archive, Trash2, Edit2, MoreHorizontal, BookOpen, Layers} from 'lucide-react';
import {useState, useMemo} from 'react';
import type {Domain, NavLocation} from '../workspaceTypes';

/* ── ROOT SCREEN (All Domains) ────────────────────────────────────── */
type RootProps = {
  domains: Domain[];
  onNavigate: (loc: NavLocation) => void;
  onOpenCreateModal: (type: 'domain' | 'subject' | 'chapter' | 'topic', domainId?: string, subjectId?: string, chapterId?: string) => void;
  onRenameDomain: (id: string, name: string) => void;
  onDeleteDomain: (id: string) => void;
  onTogglePinDomain: (id: string) => void;
  onToggleArchiveDomain: (id: string) => void;
};

export function RootScreen({
  domains,
  onNavigate,
  onOpenCreateModal,
  onRenameDomain,
  onDeleteDomain,
  onTogglePinDomain,
  onToggleArchiveDomain
}: RootProps) {
  const [contextMenu, setContextMenu] = useState<{id: string; x: number; y: number} | null>(null);
  const [renamingId, setRenamingId] = useState<string | null>(null);
  const [renameValue, setRenameValue] = useState('');

  const activeDomains = useMemo(() => {
    return domains.filter(d => !d.archived).sort((a, b) => (b.pinned ? 1 : 0) - (a.pinned ? 1 : 0));
  }, [domains]);



  const handleRename = (id: string) => {
    if (renameValue.trim()) {
      onRenameDomain(id, renameValue.trim());
      setRenamingId(null);
    }
  };

  return (
    <div style={{padding: '32px 24px', maxWidth: 1000, margin: '0 auto', height: '100%', overflowY: 'auto'}}>
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 28}}>
        <div>
          <h1 style={{fontSize: 24, fontWeight: 800, color: 'var(--ws-ink)', margin: '0 0 6px', letterSpacing: '-0.02em'}}>
            Learning Domains
          </h1>
          <p style={{fontSize: 13, color: 'var(--ws-ink-2)', margin: 0}}>
            Explore your structured practice workspace hierarchy and coordinate resource notebook extraction.
          </p>
        </div>
        <button
          type="button"
          className="bg-ws-glow text-ws-floor font-semibold rounded-md py-2 px-4 flex items-center gap-2 hover:brightness-110 transition-all cursor-pointer shadow-md"
          onClick={() => onOpenCreateModal('domain')}
        >
          <Plus size={16} /> New Domain
        </button>
      </div>

      <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 16}}>
        {activeDomains.map(domain => {
          const totalSubjects = domain.subjects.length;
          const totalChapters = domain.subjects.reduce((acc, s) => acc + s.chapters.length, 0);

          return (
            <div
              key={domain.id}
              onClick={() => onNavigate({level: 'domain', domainId: domain.id})}
              style={{
                background: 'var(--ws-bench)', border: '1px solid var(--ws-edge-soft)',
                borderRadius: 'var(--ws-r-lg)', padding: 20, cursor: 'pointer',
                position: 'relative', display: 'flex', flexDirection: 'column',
                transition: 'all 200ms cubic-bezier(0.4, 0, 0.2, 1)',
                boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
              }}
              onMouseEnter={e => {
                e.currentTarget.style.borderColor = 'var(--ws-glow)';
                e.currentTarget.style.transform = 'translateY(-2px)';
              }}
              onMouseLeave={e => {
                e.currentTarget.style.borderColor = 'var(--ws-edge-soft)';
                e.currentTarget.style.transform = 'translateY(0)';
              }}
            >
              <div style={{display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8}}>
                <Folder size={18} style={{color: 'var(--ws-glow)'}} />
                {renamingId === domain.id ? (
                  <input
                    type="text"
                    value={renameValue}
                    onChange={e => setRenameValue(e.target.value)}
                    onKeyDown={e => { if (e.key === 'Enter') handleRename(domain.id); if (e.key === 'Escape') setRenamingId(null); }}
                    onClick={e => e.stopPropagation()}
                    onBlur={() => handleRename(domain.id)}
                    autoFocus
                    style={{
                      flex: 1, padding: '2px 6px', background: 'var(--ws-floor)',
                      border: '1px solid var(--ws-glow)', borderRadius: 'var(--ws-r-sm)',
                      color: 'var(--ws-ink)', fontSize: 16, fontWeight: 700, outline: 'none'
                    }}
                  />
                ) : (
                  <h2 style={{
                    fontSize: 16, fontWeight: 700, color: 'var(--ws-ink)', margin: 0,
                    overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', flex: 1
                  }}>
                    {domain.name}
                  </h2>
                )}
                
                {domain.pinned && <Pin size={12} style={{color: 'var(--ws-glow)'}} />}
                
                <button
                  type="button"
                  style={{background: 'none', border: 'none', color: 'var(--ws-ink-muted)', cursor: 'pointer', padding: 4}}
                  onClick={e => {
                    e.stopPropagation();
                    setContextMenu({id: domain.id, x: e.clientX, y: e.clientY});
                  }}
                >
                  <MoreHorizontal size={16} />
                </button>
              </div>

              {/* Subjects Preview List inside Domain Card */}
              <div style={{flex: 1, marginBottom: 16, display: 'flex', flexDirection: 'column', gap: 8}} onClick={e => e.stopPropagation()}>
                {domain.subjects.slice(0, 3).map(sub => {
                  const firstChId = sub.chapters[0]?.id;
                  return (
                    <div
                      key={sub.id}
                      style={{
                        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                        background: 'var(--ws-floor)', border: '1px solid var(--ws-edge-soft)',
                        padding: '6px 10px', borderRadius: 'var(--ws-r-md)',
                        cursor: 'pointer',
                        transition: 'all 150ms ease'
                      }}
                      onClick={() => onNavigate({level: 'subject', domainId: domain.id, subjectId: sub.id})}
                      onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--ws-glow)'; }}
                      onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--ws-edge-soft)'; }}
                    >
                      <span style={{fontSize: 12, fontWeight: 600, color: 'var(--ws-ink)', display: 'flex', alignItems: 'center', gap: 6, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', flex: 1}}>
                        <BookOpen size={12} style={{color: 'var(--ws-glow)', flexShrink: 0}} />
                        {sub.name}
                      </span>
                      <div style={{display: 'flex', gap: 6}} onClick={e => e.stopPropagation()}>
                        <button
                          type="button"
                          onClick={() => onOpenCreateModal('chapter', domain.id, sub.id)}
                          title="Add Chapter to this subject"
                          style={{
                            background: 'none', border: 'none', cursor: 'pointer',
                            color: 'var(--ws-ink-muted)', fontSize: 10, padding: 2, display: 'flex', alignItems: 'center', gap: 2
                          }}
                          onMouseEnter={e => e.currentTarget.style.color = 'var(--ws-glow)'}
                          onMouseLeave={e => e.currentTarget.style.color = 'var(--ws-ink-muted)'}
                        >
                          <Layers size={10} /> <span>+Ch</span>
                        </button>
                        <button
                          type="button"
                          onClick={() => onOpenCreateModal('topic', domain.id, sub.id, firstChId)}
                          title="Add Topic to this subject"
                          style={{
                            background: 'none', border: 'none', cursor: 'pointer',
                            color: 'var(--ws-ink-muted)', fontSize: 10, padding: 2, display: 'flex', alignItems: 'center', gap: 2
                          }}
                          onMouseEnter={e => e.currentTarget.style.color = 'var(--ws-glow)'}
                          onMouseLeave={e => e.currentTarget.style.color = 'var(--ws-ink-muted)'}
                        >
                          <Plus size={10} /> <span>+Topic</span>
                        </button>
                      </div>
                    </div>
                  );
                })}
                {totalSubjects > 3 && (
                  <div
                    onClick={() => onNavigate({level: 'domain', domainId: domain.id})}
                    style={{fontSize: 11, color: 'var(--ws-glow)', cursor: 'pointer', fontWeight: 600, paddingLeft: 4}}
                    onMouseEnter={e => e.currentTarget.style.textDecoration = 'underline'}
                    onMouseLeave={e => e.currentTarget.style.textDecoration = 'none'}
                  >
                    View all {totalSubjects} subjects ›
                  </div>
                )}
                {totalSubjects === 0 && (
                  <span style={{fontSize: 12, color: 'var(--ws-ink-muted)', fontStyle: 'italic', paddingLeft: 4}}>No subjects inside yet.</span>
                )}
              </div>

              {/* Stats footer */}
              <div style={{
                display: 'flex', justifyContent: 'space-between', fontSize: 11,
                color: 'var(--ws-ink-muted)', borderTop: '1px solid var(--ws-edge-soft)', paddingTop: 12
              }}>
                <span style={{display: 'flex', alignItems: 'center', gap: 4}}>
                  <Layers size={11} /> {totalSubjects} Subject{totalSubjects !== 1 ? 's' : ''}
                </span>
                <span style={{display: 'flex', alignItems: 'center', gap: 4}}>
                  <BookOpen size={11} /> {totalChapters} Chapter{totalChapters !== 1 ? 's' : ''}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {contextMenu && (
        <>
          <div
            style={{position: 'fixed', inset: 0, zIndex: 999}}
            onClick={() => setContextMenu(null)}
          />
          <div style={{
            position: 'fixed', left: contextMenu.x, top: contextMenu.y, zIndex: 1000,
            background: 'var(--ws-bench)', border: '1px solid var(--ws-edge)',
            borderRadius: 'var(--ws-r-md)', padding: 4, minWidth: 145,
            boxShadow: '0 8px 24px rgba(0,0,0,0.5)',
          }}>
            {[
              {
                icon: Pin,
                label: domains.find(d => d.id === contextMenu.id)?.pinned ? 'Unpin' : 'Pin',
                action: () => { onTogglePinDomain(contextMenu.id); setContextMenu(null); }
              },
              {
                icon: Archive,
                label: 'Archive',
                action: () => { onToggleArchiveDomain(contextMenu.id); setContextMenu(null); }
              },
              {
                icon: Edit2,
                label: 'Rename',
                action: () => {
                  setRenamingId(contextMenu.id);
                  setRenameValue(domains.find(d => d.id === contextMenu.id)?.name || '');
                  setContextMenu(null);
                }
              },
              {
                icon: Trash2,
                label: 'Delete',
                action: () => {
                  if (confirm('Delete this Domain and all its subjects?')) {
                    onDeleteDomain(contextMenu.id);
                  }
                  setContextMenu(null);
                },
                danger: true
              },
            ].map(item => (
              <button
                key={item.label}
                type="button"
                onClick={item.action}
                style={{
                  display: 'flex', alignItems: 'center', gap: 8, width: '100%',
                  padding: '6px 10px', background: 'none', border: 'none', borderRadius: 'var(--ws-r-sm)',
                  color: (item as {danger?: boolean}).danger ? 'var(--ws-signal-fail)' : 'var(--ws-ink-2)',
                  fontSize: 12, cursor: 'pointer', textAlign: 'left',
                }}
                onMouseEnter={e => (e.currentTarget.style.background = 'var(--ws-shelf)')}
                onMouseLeave={e => (e.currentTarget.style.background = 'none')}
              >
                <item.icon size={12} /> {item.label}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}


/* ── DOMAIN SCREEN (Subjects inside a Domain) ──────────────────────── */
type DomainProps = {
  domain: Domain;
  onNavigate: (loc: NavLocation) => void;
  onOpenCreateModal: (type: 'domain' | 'subject' | 'chapter' | 'topic', domainId?: string, subjectId?: string, chapterId?: string) => void;
  onRenameSubject: (domainId: string, subjectId: string, name: string) => void;
  onDeleteSubject: (domainId: string, subjectId: string) => void;
};

export function DomainScreen({
  domain,
  onNavigate,
  onOpenCreateModal,
  onRenameSubject,
  onDeleteSubject
}: DomainProps) {
  const [contextMenu, setContextMenu] = useState<{id: string; x: number; y: number} | null>(null);
  const [renamingId, setRenamingId] = useState<string | null>(null);
  const [renameValue, setRenameValue] = useState('');

  const activeSubjects = useMemo(() => {
    return domain.subjects.filter(s => !s.archived).sort((a, b) => (b.pinned ? 1 : 0) - (a.pinned ? 1 : 0));
  }, [domain]);



  const handleRename = (id: string) => {
    if (renameValue.trim()) {
      onRenameSubject(domain.id, id, renameValue.trim());
      setRenamingId(null);
    }
  };

  return (
    <div style={{padding: '32px 24px', maxWidth: 1000, margin: '0 auto', height: '100%', overflowY: 'auto'}}>
      <button
        type="button"
        onClick={() => onNavigate({level: 'root'})}
        style={{
          display: 'flex', alignItems: 'center', gap: 6, background: 'none', border: 'none',
          color: 'var(--ws-ink-muted)', fontSize: 12, cursor: 'pointer', padding: 0, marginBottom: 16
        }}
      >
        <ArrowLeft size={14} /> Back to Domains
      </button>

      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 28}}>
        <div>
          <h1 style={{fontSize: 24, fontWeight: 800, color: 'var(--ws-ink)', margin: '0 0 6px', letterSpacing: '-0.02em'}}>
            {domain.name} Subjects
          </h1>
          <p style={{fontSize: 13, color: 'var(--ws-ink-2)', margin: 0}}>
            Select a subject to open the workspace study dashboard, practice tests, and workflows.
          </p>
        </div>
        <button
          type="button"
          className="bg-ws-glow text-ws-floor font-semibold rounded-md py-2 px-4 flex items-center gap-2 hover:brightness-110 transition-all cursor-pointer shadow-md"
          onClick={() => onOpenCreateModal('subject', domain.id)}
        >
          <Plus size={16} /> New Subject
        </button>
      </div>

      <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 16}}>
        {activeSubjects.map(subject => {
          return (
            <div
              key={subject.id}
              onClick={() => onNavigate({level: 'subject', domainId: domain.id, subjectId: subject.id})}
              style={{
                background: 'var(--ws-bench)', border: '1px solid var(--ws-edge-soft)',
                borderRadius: 'var(--ws-r-lg)', padding: 20, cursor: 'pointer',
                position: 'relative', display: 'flex', flexDirection: 'column', gap: 8,
                transition: 'all 200ms cubic-bezier(0.4, 0, 0.2, 1)',
                boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
              }}
              onMouseEnter={e => {
                e.currentTarget.style.borderColor = 'var(--ws-glow)';
                e.currentTarget.style.transform = 'translateY(-2px)';
              }}
              onMouseLeave={e => {
                e.currentTarget.style.borderColor = 'var(--ws-edge-soft)';
                e.currentTarget.style.transform = 'translateY(0)';
              }}
            >
              <div style={{display: 'flex', alignItems: 'center', gap: 8}}>
                <FileText size={18} style={{color: 'var(--ws-glow)'}} />
                {renamingId === subject.id ? (
                  <input
                    type="text"
                    value={renameValue}
                    onChange={e => setRenameValue(e.target.value)}
                    onKeyDown={e => { if (e.key === 'Enter') handleRename(subject.id); if (e.key === 'Escape') setRenamingId(null); }}
                    onClick={e => e.stopPropagation()}
                    onBlur={() => handleRename(subject.id)}
                    autoFocus
                    style={{
                      flex: 1, padding: '2px 6px', background: 'var(--ws-floor)',
                      border: '1px solid var(--ws-glow)', borderRadius: 'var(--ws-r-sm)',
                      color: 'var(--ws-ink)', fontSize: 15, fontWeight: 700, outline: 'none'
                    }}
                  />
                ) : (
                  <h2 style={{
                    fontSize: 15, fontWeight: 700, color: 'var(--ws-ink)', margin: 0,
                    overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', flex: 1
                  }}>
                    {subject.name}
                  </h2>
                )}

                <button
                  type="button"
                  style={{background: 'none', border: 'none', color: 'var(--ws-ink-muted)', cursor: 'pointer', padding: 4}}
                  onClick={e => {
                    e.stopPropagation();
                    setContextMenu({id: subject.id, x: e.clientX, y: e.clientY});
                  }}
                >
                  <MoreHorizontal size={16} />
                </button>
              </div>

              {subject.description && (
                <p style={{
                  fontSize: 12, color: 'var(--ws-ink-2)', margin: '4px 0 12px', lineHeight: 1.5,
                  overflow: 'hidden', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical'
                }}>
                  {subject.description}
                </p>
              )}

              {/* Chapters Preview vertical list inside Subject Card */}
              <div style={{flex: 1, marginBottom: 12, display: 'flex', flexDirection: 'column', gap: 6}} onClick={e => e.stopPropagation()}>
                {subject.chapters.slice(0, 3).map(ch => (
                  <div
                    key={ch.id}
                    style={{
                      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                      background: 'var(--ws-floor)', border: '1px solid var(--ws-edge-soft)',
                      padding: '5px 8px', borderRadius: 'var(--ws-r-md)',
                      cursor: 'pointer',
                      transition: 'all 150ms ease'
                    }}
                    onClick={() => onNavigate({level: 'chapter', domainId: domain.id, subjectId: subject.id, chapterId: ch.id})}
                    onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--ws-glow)'; }}
                    onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--ws-edge-soft)'; }}
                  >
                    <span style={{fontSize: 11, fontWeight: 600, color: 'var(--ws-ink-2)', display: 'flex', alignItems: 'center', gap: 4, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', flex: 1}}>
                      <Layers size={11} style={{color: 'var(--ws-glow)', flexShrink: 0}} />
                      {ch.name}
                    </span>
                    <button
                      type="button"
                      onClick={() => onOpenCreateModal('topic', domain.id, subject.id, ch.id)}
                      title="Add topic/concept directly inside this chapter"
                      style={{
                        background: 'none', border: 'none', cursor: 'pointer',
                        color: 'var(--ws-ink-muted)', fontSize: 10, padding: 2, display: 'flex', alignItems: 'center', gap: 2
                      }}
                      onMouseEnter={e => e.currentTarget.style.color = 'var(--ws-glow)'}
                      onMouseLeave={e => e.currentTarget.style.color = 'var(--ws-ink-muted)'}
                    >
                      <Plus size={10} /> <span>Topic</span>
                    </button>
                  </div>
                ))}
                {subject.chapters.length > 3 && (
                  <div
                    onClick={() => onNavigate({level: 'subject', domainId: domain.id, subjectId: subject.id})}
                    style={{fontSize: 10.5, color: 'var(--ws-glow)', fontWeight: 600, cursor: 'pointer', paddingLeft: 4}}
                    onMouseEnter={e => e.currentTarget.style.textDecoration = 'underline'}
                    onMouseLeave={e => e.currentTarget.style.textDecoration = 'none'}
                  >
                    +{subject.chapters.length - 3} more chapters ›
                  </div>
                )}
              </div>

              {/* Subject card footer with quick creation triggers */}
              <div style={{display: 'flex', gap: 6, borderTop: '1px solid var(--ws-edge-soft)', paddingTop: 10, marginTop: 'auto'}} onClick={e => e.stopPropagation()}>
                <button
                  type="button"
                  onClick={() => onOpenCreateModal('chapter', domain.id, subject.id)}
                  style={{
                    flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 4,
                    background: 'none', border: '1px dashed var(--ws-edge)', borderRadius: 'var(--ws-r-sm)',
                    color: 'var(--ws-glow)', padding: '5px 8px', fontSize: 11, fontWeight: 600, cursor: 'pointer',
                    transition: 'all 150ms ease'
                  }}
                  onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--ws-glow)'; e.currentTarget.style.background = 'var(--ws-glow-wash)'; }}
                  onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--ws-edge)'; e.currentTarget.style.background = 'none'; }}
                >
                  <Plus size={11} /> Chapter
                </button>
                <button
                  type="button"
                  onClick={() => {
                    const firstChId = subject.chapters[0]?.id;
                    onOpenCreateModal('topic', domain.id, subject.id, firstChId);
                  }}
                  style={{
                    flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 4,
                    background: 'none', border: '1px dashed var(--ws-edge)', borderRadius: 'var(--ws-r-sm)',
                    color: 'var(--ws-glow)', padding: '5px 8px', fontSize: 11, fontWeight: 600, cursor: 'pointer',
                    transition: 'all 150ms ease'
                  }}
                  onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--ws-glow)'; e.currentTarget.style.background = 'var(--ws-glow-wash)'; }}
                  onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--ws-edge)'; e.currentTarget.style.background = 'none'; }}
                >
                  <Plus size={11} /> Topic
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {contextMenu && (
        <>
          <div
            style={{position: 'fixed', inset: 0, zIndex: 999}}
            onClick={() => setContextMenu(null)}
          />
          <div style={{
            position: 'fixed', left: contextMenu.x, top: contextMenu.y, zIndex: 1000,
            background: 'var(--ws-bench)', border: '1px solid var(--ws-edge)',
            borderRadius: 'var(--ws-r-md)', padding: 4, minWidth: 120,
            boxShadow: '0 8px 24px rgba(0,0,0,0.5)',
          }}>
            {[
              {
                icon: Edit2,
                label: 'Rename',
                action: () => {
                  setRenamingId(contextMenu.id);
                  setRenameValue(domain.subjects.find(s => s.id === contextMenu.id)?.name || '');
                  setContextMenu(null);
                }
              },
              {
                icon: Trash2,
                label: 'Delete',
                action: () => {
                  if (confirm('Delete this subject and all its chapters?')) {
                    onDeleteSubject(domain.id, contextMenu.id);
                  }
                  setContextMenu(null);
                },
                danger: true
              },
            ].map(item => (
              <button
                key={item.label}
                type="button"
                onClick={item.action}
                style={{
                  display: 'flex', alignItems: 'center', gap: 8, width: '100%',
                  padding: '6px 10px', background: 'none', border: 'none', borderRadius: 'var(--ws-r-sm)',
                  color: (item as {danger?: boolean}).danger ? 'var(--ws-signal-fail)' : 'var(--ws-ink-2)',
                  fontSize: 12, cursor: 'pointer', textAlign: 'left',
                }}
                onMouseEnter={e => (e.currentTarget.style.background = 'var(--ws-shelf)')}
                onMouseLeave={e => (e.currentTarget.style.background = 'none')}
              >
                <item.icon size={12} /> {item.label}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

import {Search, ChevronRight, ChevronDown, ChevronLeft, FolderOpen, Folder, LayoutGrid, Workflow, GitBranch, Pin, Archive, Trash2, Edit2, Plus, MoreHorizontal, BookOpen, Layers, FileCode, History, Settings2, Check, ArrowUpRight} from 'lucide-react';
import {useState, useMemo} from 'react';
import type {RecentItem} from '../workspaceTypes';

import { useWorkspaceStore } from '../stores/workspaceStore';
import { useQuery } from '@tanstack/react-query';
import { api } from '../api/workspaceApi';
import { useUIStore } from '../stores/uiStore';
import { Link, useRouterState, useNavigate, useRouter } from '@tanstack/react-router';

function LeftNav() {
  const recentItems = useWorkspaceStore(s => s.recentItems);
  const onRenameDomain = useWorkspaceStore(s => s.renameDomain);
  const onDeleteDomain = useWorkspaceStore(s => s.deleteDomain);
  const onTogglePinDomain = useWorkspaceStore(s => s.togglePinDomain);
  const onToggleArchiveDomain = useWorkspaceStore(s => s.toggleArchiveDomain);
  
  const collapsed = useUIStore(s => s.leftCollapsed);
  const onSearchTrigger = () => useUIStore.getState().setSearchModalOpen(true);
  
  // Note: create modal logic should ideally be moved to store or root layout.
  // For now, we'll keep it as a stub or move the state here if needed.
  const onOpenCreateModal = (_type: string, _domainId?: string, _subjectId?: string) => {}; // TODO: Wire to UI store
  
  const routerState = useRouterState();
  const location = routerState.location;
  const navigate = useNavigate();
  const router = useRouter();
  
  const { data: domains = [], isLoading: isLoadingDomains } = useQuery({
    queryKey: ['domains'],
    queryFn: api.getDomains,
  });

  const canGoBack = true; // window.history logic handled by router
  const canGoForward = true;
  const onBack = () => router.history.back();
  const onForward = () => router.history.forward();

  const [search, setSearch] = useState('');
  const [expanded, setExpanded] = useState<Set<string>>(new Set([domains[0]?.id]));
  const [contextMenu, setContextMenu] = useState<{id: string; type: 'domain'; x: number; y: number} | null>(null);
  const [renaming, setRenaming] = useState<string | null>(null);
  const [renameValue, setRenameValue] = useState('');
  const [showArchived, setShowArchived] = useState(false);
  const [recentGroupBy, setRecentGroupBy] = useState<'None' | 'Date' | 'Project'>('None');
  const [showRecentMenu, setShowRecentMenu] = useState(false);

  const toggleExpand = (id: string) => {
    setExpanded(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id); else next.add(id);
      return next;
    });
  };

  const filteredDomains = useMemo(() => {
    let list = domains;
    if (!showArchived) list = list.filter(d => !d.archived);
    if (search) {
      const needle = search.toLowerCase();
      list = list.filter(d =>
        d.name.toLowerCase().includes(needle) ||
        d.subjects.some(s => s.name.toLowerCase().includes(needle))
      );
    }
    return [...list].sort((a, b) => (b.pinned ? 1 : 0) - (a.pinned ? 1 : 0));
  }, [domains, search, showArchived]);

  const handleContextMenu = (e: React.MouseEvent, id: string) => {
    e.preventDefault();
    e.stopPropagation();
    setContextMenu({id, type: 'domain', x: e.clientX, y: e.clientY});
  };

  const closeContext = () => setContextMenu(null);

  const startRename = (id: string) => {
    const d = domains.find(dom => dom.id === id);
    setRenaming(id);
    setRenameValue(d?.name || '');
    closeContext();
  };

  const finishRename = () => {
    if (renaming && renameValue.trim()) {
      onRenameDomain(renaming, renameValue.trim());
    }
    setRenaming(null);
  };


  // Use pathname parts for active route detection
  const pathParts = location.pathname.split('/');
  const activeDomainFromPath = pathParts[2] ?? null; // used for domain highlighting
  const activeSubjectFromPath = pathParts[3] ?? null; // used for subject highlighting
  void activeDomainFromPath; void activeSubjectFromPath; // referenced in JSX below

  const renderRecentItem = (item: RecentItem, paddingLeft: number = 8) => {
    let toStr = '/';
    let paramsObj: any = {};
    if (item.loc.level === 'domain') { toStr = '/domain/$domainId'; paramsObj = { domainId: item.loc.domainId }; }
    else if (item.loc.level === 'subject') { toStr = '/subject/$domainId/$subjectId'; paramsObj = { domainId: item.loc.domainId, subjectId: item.loc.subjectId }; }
    else if (item.loc.level === 'chapter') { toStr = '/chapter/$domainId/$subjectId/$chapterId'; paramsObj = { domainId: item.loc.domainId, subjectId: item.loc.subjectId, chapterId: item.loc.chapterId }; }
    else if (item.loc.level === 'topic') { toStr = '/topic/$domainId/$subjectId/$chapterId/$topicId'; paramsObj = { domainId: item.loc.domainId, subjectId: item.loc.subjectId, chapterId: item.loc.chapterId, topicId: item.loc.topicId }; }
    
    return (
      <Link
        key={item.id}
        to={toStr as any}
        params={paramsObj}
        style={{
          textDecoration: 'none',
          display: 'flex', alignItems: 'center', gap: 8, width: '100%',
          padding: `5px 8px 5px ${paddingLeft}px`, background: 'none', border: 'none', borderRadius: "4px",
          color: "#a1a1aa", fontSize: 12, cursor: 'pointer', textAlign: 'left',
          textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap',
          transition: 'background 100ms ease'
        }}
        onMouseEnter={e => (e.currentTarget.style.background = "#27272a")}
        onMouseLeave={e => (e.currentTarget.style.background = 'none')}
      >
        <span className="text-sm font-medium" style={{overflow: 'hidden', textOverflow: 'ellipsis', flex: 1}}>
          {item.label}
        </span>
        <span style={{
          fontSize: 9, opacity: 0.6, color: "#10b981",
          padding: '1px 4px', background: "rgba(16,185,129,0.1)", border: '1px solid rgba(16, 185, 129, 0.25)',
          borderRadius: 3, textTransform: 'capitalize', flexShrink: 0
        }}>
          {item.type}
        </span>
      </Link>
    );
  };

  const renderGroupedByDate = () => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    const groups: { [key: string]: RecentItem[] } = {
      'Today': [],
      'Yesterday': [],
      'Older': [],
    };

    recentItems.forEach(item => {
      const d = new Date(item.time);
      if (d >= today) groups['Today'].push(item);
      else if (d >= yesterday) groups['Yesterday'].push(item);
      else groups['Older'].push(item);
    });

    return (
      <div style={{display: 'flex', flexDirection: 'column', gap: 12}}>
        {['Today', 'Yesterday', 'Older'].map(g => {
          if (groups[g].length === 0) return null;
          return (
            <div key={g}>
              <div style={{fontSize: 10, color: "#71717a", marginBottom: 4, paddingLeft: 8}}>{g}</div>
              {groups[g].map(item => renderRecentItem(item))}
            </div>
          );
        })}
      </div>
    );
  };

  const renderGroupedByProject = () => {
    const domainMap = new Map<string, RecentItem[]>();
    const noDomainItems: RecentItem[] = [];

    recentItems.forEach(item => {
      const dId = 'domainId' in item.loc ? item.loc.domainId : null;
      if (dId) {
        if (!domainMap.has(dId)) domainMap.set(dId, []);
        domainMap.get(dId)!.push(item);
      } else {
        noDomainItems.push(item);
      }
    });

    return (
      <div style={{display: 'flex', flexDirection: 'column', gap: 12}}>
        {Array.from(domainMap.entries()).map(([dId, items]) => {
          const domain = domains.find(d => d.id === dId);
          if (!domain) return null;

          const subjectMap = new Map<string, RecentItem[]>();
          const domainDirectItems: RecentItem[] = [];

          items.forEach(item => {
            const sId = 'subjectId' in item.loc ? item.loc.subjectId : null;
            if (sId) {
              if (!subjectMap.has(sId)) subjectMap.set(sId, []);
              subjectMap.get(sId)!.push(item);
            } else {
              domainDirectItems.push(item);
            }
          });

          return (
            <div key={dId}>
              <div style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '4px 8px', color: "#a1a1aa", fontSize: 11, fontWeight: 500}}>
                <div style={{display: 'flex', alignItems: 'center', gap: 6, overflow: 'hidden'}}>
                  <span style={{overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap'}}>{domain.name}</span>
                  <Link 
                    to="/domain/$domainId"
                    params={{ domainId: domain.id }}
                    style={{background: 'none', border: 'none', cursor: 'pointer', padding: 2, display: 'flex', color: "#71717a"}}
                    onMouseEnter={e => e.currentTarget.style.color = "#10b981"}
                    onMouseLeave={e => e.currentTarget.style.color = "#71717a"}
                    title="Go to domain"
                  >
                    <ArrowUpRight size={10} />
                  </Link>
                </div>
              </div>
              {domainDirectItems.map(item => renderRecentItem(item, 16))}
              {Array.from(subjectMap.entries()).map(([sId, sItems]) => {
                const subject = domain.subjects.find(s => s.id === sId);
                if (!subject) return null;

                const chapterMap = new Map<string, RecentItem[]>();
                const subjectDirectItems: RecentItem[] = [];

                sItems.forEach(item => {
                   const cId = 'chapterId' in item.loc ? item.loc.chapterId : null;
                   if (cId) {
                     if (!chapterMap.has(cId)) chapterMap.set(cId, []);
                     chapterMap.get(cId)!.push(item);
                   } else {
                     subjectDirectItems.push(item);
                   }
                });

                return (
                  <div key={sId} style={{marginLeft: 8, marginTop: 4}}>
                    <div style={{display: 'flex', alignItems: 'center', gap: 6, padding: '2px 8px', color: "#71717a", fontSize: 11}}>
                      <span style={{overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap'}}>{subject.name}</span>
                      <Link 
                        to="/subject/$domainId/$subjectId"
                        params={{ domainId: domain.id, subjectId: subject.id }}
                        style={{background: 'none', border: 'none', cursor: 'pointer', padding: 2, display: 'flex', color: "#71717a"}}
                        onMouseEnter={e => e.currentTarget.style.color = "#10b981"}
                        onMouseLeave={e => e.currentTarget.style.color = "#71717a"}
                        title="Go to subject"
                      >
                        <ArrowUpRight size={10} />
                      </Link>
                    </div>
                    {subjectDirectItems.map(item => renderRecentItem(item, 16))}
                    {Array.from(chapterMap.entries()).map(([cId, cItems]) => {
                       const chapter = subject.chapters.find(c => c.id === cId);
                       if (!chapter) return null;
                       return (
                         <div key={cId} style={{marginLeft: 8, marginTop: 4}}>
                           <div style={{display: 'flex', alignItems: 'center', gap: 6, padding: '2px 8px', color: "#71717a", fontSize: 10}}>
                             <span style={{overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap'}}>{chapter.name}</span>
                             <Link 
                               to="/chapter/$domainId/$subjectId/$chapterId"
                               params={{ domainId: domain.id, subjectId: subject.id, chapterId: chapter.id }}
                               style={{background: 'none', border: 'none', cursor: 'pointer', padding: 2, display: 'flex', color: "#71717a"}}
                               onMouseEnter={e => e.currentTarget.style.color = "#10b981"}
                               onMouseLeave={e => e.currentTarget.style.color = "#71717a"}
                               title="Go to chapter"
                             >
                               <ArrowUpRight size={10} />
                             </Link>
                           </div>
                           {cItems.map(item => renderRecentItem(item, 16))}
                         </div>
                       )
                    })}
                  </div>
                )
              })}
            </div>
          );
        })}
        {noDomainItems.length > 0 && (
          <div>
            <div style={{fontSize: 10, color: "#71717a", marginBottom: 4, paddingLeft: 8}}>Other</div>
            {noDomainItems.map(item => renderRecentItem(item))}
          </div>
        )}
      </div>
    );
  };

  return (
    <nav className="flex flex-col bg-ws-bg border-r border-ws-line transition-[width]" style={{width: collapsed ? 48 : 220}} aria-label="Domain navigation" onClick={closeContext}>
      {/* Search + nav arrows */}
      {!collapsed && (
        <div className="flex items-center gap-1 p-2">
          <button type="button" className="flex items-center justify-center rounded hover:bg-ws-surface-2 text-ws-muted hover:text-ws-ink transition-colors" onClick={onBack} disabled={!canGoBack} style={{width: 24, height: 24, opacity: canGoBack ? 1 : 0.3}} title="Back">
            <ChevronLeft size={14} />
          </button>
          <button type="button" className="flex items-center justify-center rounded hover:bg-ws-surface-2 text-ws-muted hover:text-ws-ink transition-colors" onClick={onForward} disabled={!canGoForward} style={{width: 24, height: 24, opacity: canGoForward ? 1 : 0.3}} title="Forward">
            <ChevronRight size={14} />
          </button>
          <div className="relative flex-1 min-w-0 ml-1">
            <Search size={11} className="absolute left-1.5 top-1.5 text-ws-muted" />
            <input
              type="text"
              placeholder="Search..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="w-full pl-5 pr-1.5 py-1 text-[11px] bg-ws-bg text-ws-ink border border-ws-line rounded outline-none focus:border-ws-success/50 focus:ring-1 focus:ring-ws-success/50 placeholder-zinc-600 transition-all"
            />
          </div>
        </div>
      )}

      <div className="flex-1 overflow-y-auto overflow-x-hidden min-h-0 p-2 scrollbar">
        {/* Domain section header */}
        {!collapsed && (
          <div className="flex items-center justify-between px-2 py-1 mb-1">
            <span className="text-[10px] font-bold text-ws-muted uppercase tracking-wider">Domains</span>
            <div className="flex items-center gap-0.5">
              <button
                type="button"
                onClick={() => setShowArchived(!showArchived)}
                title={showArchived ? 'Hide archived' : 'Show archived'}
                className={`flex p-0.5 rounded hover:bg-ws-surface-2 transition-colors ${showArchived ? 'text-ws-success' : 'text-ws-muted'}`}
              >
                <Archive size={11} />
              </button>
              <button
                type="button"
                onClick={() => onOpenCreateModal('domain')}
                title="New domain"
                className="flex p-0.5 rounded hover:bg-ws-surface-2 text-ws-muted transition-colors"
              >
                <Plus size={11} />
              </button>
            </div>
          </div>
        )}

        {/* Domain tree */}
        {collapsed ? (
          (() => {
            const isDomainsActive = ['/', '/domain', '/subject', '/chapter', '/topic'].some(p => location.pathname.startsWith(p.length > 1 ? p : '/') && (p === '/' ? location.pathname === '/' || location.pathname.startsWith('/domain') || location.pathname.startsWith('/subject') || location.pathname.startsWith('/chapter') || location.pathname.startsWith('/topic') : true));
            return (
              <>
                {/* Topmost Domain Folder */}
                <Link
                  to="/"
                  style={{
                    textDecoration: 'none',
                    display: 'flex', justifyContent: 'center', padding: '8px 0',
                    cursor: 'pointer', borderRadius: "4px",
                    background: isDomainsActive ? "rgba(16,185,129,0.1)" : 'transparent',
                    marginBottom: 6
                  }}
                  onMouseEnter={e => { if (!isDomainsActive) e.currentTarget.style.background = "#27272a"; }}
                  onMouseLeave={e => { if (!isDomainsActive) e.currentTarget.style.background = 'transparent'; }}
                  title="All Domains"
                >
                  <Folder size={18} style={{color: isDomainsActive ? "#10b981" : "#a1a1aa"}} />
                </Link>

                {/* Global search launcher icon */}
                <div
                  style={{
                    display: 'flex', justifyContent: 'center', padding: '8px 0',
                    cursor: 'pointer', borderRadius: "4px",
                    background: 'transparent',
                    marginBottom: 12,
                    borderBottom: '1px solid var(--ws-edge-soft)',
                    paddingBottom: 14
                  }}
                  onClick={() => onSearchTrigger?.()}
                  onMouseEnter={e => e.currentTarget.style.background = "#27272a"}
                  onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                  title="Search specializations and concepts (Ctrl+K)"
                >
                  <Search size={18} style={{color: "#a1a1aa"}} />
                </div>
              </>
            );
          })()
        ) : isLoadingDomains ? (
          <div style={{padding: '16px 8px', textAlign: 'center', color: "#71717a", fontSize: 11}}>
            Loading...
          </div>
        ) : (
          filteredDomains.map(domain => {
            const isDomainExpanded = expanded.has(domain.id);
            const isDomainActive = location.pathname === `/domain/${domain.id}`;

          return (
            <div key={domain.id} style={{marginBottom: 2}}>
              {/* Domain row */}
              <div
                style={{
                  display: 'flex', alignItems: 'center', gap: 6, padding: '5px 8px',
                  borderRadius: "4px", cursor: 'pointer',
                  background: isDomainActive ? "rgba(16,185,129,0.1)" : 'transparent',
                  opacity: domain.archived ? 0.5 : 1,
                  textDecoration: 'none',
                  color: 'inherit'
                }}
                onClick={() => { toggleExpand(domain.id); navigate({to: '/domain/$domainId', params: { domainId: domain.id }}); }}
                onContextMenu={e => handleContextMenu(e, domain.id)}
              >
                <span style={{color: "#71717a", display: 'flex', flexShrink: 0, width: 14, justifyContent: 'center'}}>
                  {isDomainExpanded ? <ChevronDown size={13} /> : <ChevronRight size={13} />}
                </span>
                <span style={{color: "#71717a", display: 'flex', flexShrink: 0}}>
                  {isDomainExpanded ? <FolderOpen size={14} style={{color: "#10b981"}} /> : <Folder size={14} />}
                </span>
                {renaming === domain.id ? (
                  <input
                    type="text"
                    value={renameValue}
                    onChange={e => setRenameValue(e.target.value)}
                    onKeyDown={e => { if (e.key === 'Enter') finishRename(); if (e.key === 'Escape') setRenaming(null); }}
                    onBlur={finishRename}
                    onClick={e => e.stopPropagation()}
                    autoFocus
                    style={{
                      flex: 1, padding: '1px 4px', background: "#0a0a0b",
                      border: '1px solid var(--ws-glow)', borderRadius: 2,
                      color: "#f4f4f5", fontSize: 12, outline: 'none', minWidth: 0,
                    }}
                  />
                ) : (
                  <span style={{fontSize: 12, fontWeight: 600, color: "#f4f4f5", flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', minWidth: 0}}>
                    {domain.name}
                  </span>
                )}
                {domain.pinned && <Pin size={10} style={{color: "#10b981", flexShrink: 0}} />}
                <button
                  type="button"
                  onClick={e => { e.stopPropagation(); onOpenCreateModal('subject', domain.id); }}
                  title="Add subject"
                  style={{background: 'none', border: 'none', cursor: 'pointer', color: "#71717a", display: 'flex', flexShrink: 0, padding: 2, marginRight: 2, opacity: 0.6}}
                  onMouseEnter={e => e.currentTarget.style.color = "#10b981"}
                  onMouseLeave={e => e.currentTarget.style.color = "#71717a"}
                >
                  <Plus size={12} />
                </button>
                <button
                  type="button"
                  onClick={e => handleContextMenu(e, domain.id)}
                  style={{background: 'none', border: 'none', cursor: 'pointer', color: "#71717a", display: 'flex', flexShrink: 0, padding: 0, opacity: 0.6}}
                >
                  <MoreHorizontal size={12} />
                </button>
              </div>

              {/* Subjects (Level 2) */}
              {isDomainExpanded && domain.subjects.map(subject => {
                const isSubExpanded = expanded.has(subject.id);
                const isSubActive = location.pathname === `/subject/${domain.id}/${subject.id}`;

                return (
                  <div key={subject.id} style={{marginLeft: 14}}>
                    <div
                      style={{
                        display: 'flex', alignItems: 'center', gap: 6, padding: '5px 8px',
                        borderRadius: "4px", cursor: 'pointer',
                        background: isSubActive ? "rgba(16,185,129,0.1)" : 'transparent',
                        textDecoration: 'none',
                        color: 'inherit'
                      }}
                      onClick={() => { toggleExpand(subject.id); navigate({to: '/subject/$domainId/$subjectId', params: { domainId: domain.id, subjectId: subject.id }}); }}
                      onMouseEnter={e => { if (!isSubActive) e.currentTarget.style.background = "#27272a"; }}
                      onMouseLeave={e => { if (!isSubActive) e.currentTarget.style.background = 'transparent'; }}
                    >
                      <span style={{color: "#71717a", display: 'flex', flexShrink: 0, width: 14, justifyContent: 'center'}}>
                        {isSubExpanded ? <ChevronDown size={13} /> : <ChevronRight size={13} />}
                      </span>
                      <span style={{color: "#71717a", display: 'flex', flexShrink: 0}}>
                        <BookOpen size={14} style={{color: isSubActive ? "#10b981" : "#71717a"}} />
                      </span>
                      <span style={{fontSize: 12, fontWeight: 500, color: isSubActive ? "#f4f4f5" : "#a1a1aa", flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', minWidth: 0}}>
                        {subject.name}
                      </span>
                      <button
                        type="button"
                        onClick={e => { e.stopPropagation(); onOpenCreateModal('chapter', domain.id, subject.id); }}
                        title="Add chapter"
                        style={{background: 'none', border: 'none', cursor: 'pointer', color: "#71717a", display: 'flex', flexShrink: 0, padding: 2, opacity: 0.6}}
                        onMouseEnter={e => e.currentTarget.style.color = "#10b981"}
                        onMouseLeave={e => e.currentTarget.style.color = "#71717a"}
                      >
                        <Plus size={11} />
                      </button>
                    </div>

                    {/* Chapters (Level 3) */}
                    {isSubExpanded && subject.chapters.map(chapter => {
                      const isChExpanded = expanded.has(chapter.id);
                      const isChActive = location.pathname === `/chapter/${domain.id}/${subject.id}/${chapter.id}`;

                      return (
                        <div key={chapter.id} style={{marginLeft: 14}}>
                          <div
                            style={{
                              display: 'flex', alignItems: 'center', gap: 6, padding: '5px 8px',
                              borderRadius: "4px", cursor: 'pointer',
                              background: isChActive ? "rgba(16,185,129,0.1)" : 'transparent',
                              textDecoration: 'none', color: 'inherit'
                            }}
                            onClick={() => { toggleExpand(chapter.id); navigate({to: '/chapter/$domainId/$subjectId/$chapterId', params: { domainId: domain.id, subjectId: subject.id, chapterId: chapter.id }}); }}
                            onMouseEnter={e => { if (!isChActive) e.currentTarget.style.background = "#27272a"; }}
                            onMouseLeave={e => { if (!isChActive) e.currentTarget.style.background = 'transparent'; }}
                          >
                            <span style={{color: "#71717a", display: 'flex', flexShrink: 0, width: 14, justifyContent: 'center'}}>
                              {isChExpanded ? <ChevronDown size={13} /> : <ChevronRight size={13} />}
                            </span>
                            <span style={{color: "#71717a", display: 'flex', flexShrink: 0}}>
                              <Layers size={14} style={{color: isChActive ? "#10b981" : "#71717a"}} />
                            </span>
                            <span style={{fontSize: 12, fontWeight: 500, color: isChActive ? "#f4f4f5" : "#a1a1aa", flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', minWidth: 0}}>
                              {chapter.name}
                            </span>
                          </div>

                          {/* Topics/Concepts (Level 4) */}
                          {isChExpanded && chapter.topics.map(topic => {
                            const isTopicActive = location.pathname === `/topic/${domain.id}/${subject.id}/${chapter.id}/${topic.id}`;

                            return (
                              <div
                                key={topic.id}
                                style={{
                                  display: 'flex', alignItems: 'center', gap: 6, padding: '5px 8px',
                                  borderRadius: "4px", cursor: 'pointer',
                                  background: isTopicActive ? "rgba(16,185,129,0.1)" : 'transparent',
                                  textDecoration: 'none', color: 'inherit'
                                }}
                                onClick={() => navigate({to: '/topic/$domainId/$subjectId/$chapterId/$topicId', params: { domainId: domain.id, subjectId: subject.id, chapterId: chapter.id, topicId: topic.id }})}
                                onMouseEnter={e => { if (!isTopicActive) e.currentTarget.style.background = "#27272a"; }}
                                onMouseLeave={e => { if (!isTopicActive) e.currentTarget.style.background = 'transparent'; }}
                              >
                                <span style={{display: 'flex', flexShrink: 0, width: 14}} />
                                <span style={{color: "#71717a", display: 'flex', flexShrink: 0}}>
                                  <FileCode size={14} style={{color: isTopicActive ? "#10b981" : "#71717a"}} />
                                </span>
                                <span style={{fontSize: 12, fontWeight: 400, color: isTopicActive ? "#f4f4f5" : "#71717a", flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', minWidth: 0}}>
                                  {topic.name}
                                </span>
                              </div>
                            );
                          })}
                        </div>
                      );
                    })}
                  </div>
                );
              })}
            </div>
          );
        }))}

        {filteredDomains.length === 0 && (
          <div style={{padding: '16px 8px', textAlign: 'center', color: "#71717a", fontSize: 11}}>
            {search ? 'No results' : 'No domains yet'}
          </div>
        )}

        {/* Global nav items at bottom */}
        <div style={{marginTop: 16, borderTop: '1px solid var(--ws-edge-soft)', paddingTop: 8}}>
          {!collapsed && <div className="text-xs font-bold text-ws-muted uppercase tracking-wider px-3 mb-2 mt-4">Tools</div>}
          <Link
            to="/notebook"
            className={`ws-nav-item${location.pathname.startsWith('/notebook') ? ' active' : ''}`}
            style={collapsed ? { justifyContent: 'center', padding: '8px 0', textDecoration: 'none' } : { textDecoration: 'none' }}
            title="Notebooks"
          >
            <BookOpen size={16} />
            {!collapsed && <span className="text-sm font-medium">Notebooks</span>}
          </Link>
          <Link
            to="/workflows"
            className={`ws-nav-item${location.pathname.startsWith('/workflow') ? ' active' : ''}`}
            style={collapsed ? { justifyContent: 'center', padding: '8px 0', textDecoration: 'none' } : { textDecoration: 'none' }}
            title="Workflows"
          >
            <Workflow size={16} />
            {!collapsed && <span className="text-sm font-medium">Workflows</span>}
          </Link>
          <Link
            to="/artifacts"
            className={`ws-nav-item${location.pathname.startsWith('/artifact') ? ' active' : ''}`}
            style={collapsed ? { justifyContent: 'center', padding: '8px 0', textDecoration: 'none' } : { textDecoration: 'none' }}
            title="Artifacts"
          >
            <LayoutGrid size={16} />
            {!collapsed && <span className="text-sm font-medium">Artifacts</span>}
          </Link>
          <Link
            to="/graph"
            className={`ws-nav-item${location.pathname.startsWith('/graph') ? ' active' : ''}`}
            style={collapsed ? { justifyContent: 'center', padding: '8px 0', textDecoration: 'none' } : { textDecoration: 'none' }}
            title="Knowledge Graph"
          >
            <GitBranch size={16} />
            {!collapsed && <span className="text-sm font-medium">Knowledge Graph</span>}
          </Link>
        </div>

        {/* Recents Section */}
        {!collapsed && recentItems && recentItems.length > 0 && (
          <div style={{marginTop: 16, borderTop: '1px solid var(--ws-edge-soft)', paddingTop: 8, paddingBottom: 16}}>
            <div className="text-xs font-bold text-ws-muted uppercase tracking-wider px-3 mb-2 mt-4" style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 4}}>
              <div style={{display: 'flex', alignItems: 'center', gap: 6}}>
                <History size={11} className="text-ws-glow" />
                <span>Recent Activity</span>
              </div>
              <div style={{position: 'relative'}}>
                <button 
                  type="button"
                  className="bg-transparent border-none text-ws-muted cursor-pointer p-1 rounded hover:text-ws-soft" 
                  onClick={(e) => { e.stopPropagation(); setShowRecentMenu(!showRecentMenu); }}
                  style={{width: 20, height: 20, background: 'none', border: 'none', cursor: 'pointer', color: "#71717a", display: 'flex', alignItems: 'center', justifyContent: 'center'}}
                  onMouseEnter={e => e.currentTarget.style.color = "#10b981"}
                  onMouseLeave={e => e.currentTarget.style.color = "#71717a"}
                >
                  <Settings2 size={12} />
                </button>
                
                {showRecentMenu && (
                  <>
                    <div style={{position: 'fixed', inset: 0, zIndex: 999}} onClick={(e) => { e.stopPropagation(); setShowRecentMenu(false); }} />
                    <div style={{
                      position: 'absolute', right: 0, top: 22, zIndex: 1000,
                      background: "#09090b", border: '1px solid var(--ws-edge)',
                      borderRadius: "6px", padding: 4, minWidth: 120,
                      boxShadow: '0 8px 24px rgba(0,0,0,0.4)',
                    }} onClick={e => e.stopPropagation()}>
                      <div style={{padding: '4px 8px', fontSize: 10, color: "#71717a", textTransform: 'uppercase', letterSpacing: 0.5}}>Group by</div>
                      {['None', 'Date', 'Project'].map(g => (
                         <button
                           key={g}
                           type="button"
                           onClick={() => { setRecentGroupBy(g as any); setShowRecentMenu(false); }}
                           style={{
                             display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%',
                             padding: '6px 10px', background: 'none', border: 'none', borderRadius: "4px",
                             color: "#a1a1aa", fontSize: 12, cursor: 'pointer', textAlign: 'left',
                           }}
                           onMouseEnter={e => (e.currentTarget.style.background = "#27272a")}
                           onMouseLeave={e => (e.currentTarget.style.background = 'none')}
                         >
                           {g}
                           {recentGroupBy === g && <Check size={12} style={{color: "#10b981"}} />}
                         </button>
                      ))}
                    </div>
                  </>
                )}
              </div>
            </div>
            
            {recentGroupBy === 'None' && (
              <div style={{display: 'flex', flexDirection: 'column'}}>
                {recentItems.map(item => renderRecentItem(item))}
              </div>
            )}
            {recentGroupBy === 'Date' && renderGroupedByDate()}
            {recentGroupBy === 'Project' && renderGroupedByProject()}
          </div>
        )}
      </div>

      {/* Context menu */}
      {contextMenu && (
        <>
          <div style={{position: 'fixed', inset: 0, zIndex: 999}} onClick={closeContext} />
          <div style={{
            position: 'fixed', left: contextMenu.x, top: contextMenu.y, zIndex: 1000,
            background: "#09090b", border: '1px solid var(--ws-edge)',
            borderRadius: "6px", padding: 4, minWidth: 140,
            boxShadow: '0 8px 24px rgba(0,0,0,0.4)',
          }}>
            {[
              {icon: Pin, label: domains.find(d => d.id === contextMenu.id)?.pinned ? 'Unpin' : 'Pin', action: () => { onTogglePinDomain(contextMenu.id); closeContext(); }},
              {icon: Archive, label: domains.find(d => d.id === contextMenu.id)?.archived ? 'Unarchive' : 'Archive', action: () => { onToggleArchiveDomain(contextMenu.id); closeContext(); }},
              {icon: Edit2, label: 'Rename', action: () => startRename(contextMenu.id)},
              {icon: Trash2, label: 'Delete', action: () => { onDeleteDomain(contextMenu.id); closeContext(); }, danger: true},
            ].map(item => (
              <button
                key={item.label}
                type="button"
                onClick={item.action}
                style={{
                  display: 'flex', alignItems: 'center', gap: 8, width: '100%',
                  padding: '6px 10px', background: 'none', border: 'none', borderRadius: "4px",
                  color: (item as {danger?: boolean}).danger ? "#ef4444" : "#a1a1aa",
                  fontSize: 12, cursor: 'pointer', textAlign: 'left',
                }}
                onMouseEnter={e => (e.currentTarget.style.background = "#27272a")}
                onMouseLeave={e => (e.currentTarget.style.background = 'none')}
              >
                <item.icon size={12} /> {item.label}
              </button>
            ))}
          </div>
        </>
      )}
    </nav>
  );
}

export default LeftNav;

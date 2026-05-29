import {Brain, AlertTriangle, CheckCircle, X, Plus, Send} from 'lucide-react';
import {useState} from 'react';

type MemoryEvent = { id: string; type: 'blind-spot' | 'mastery' | 'attempt' | 'note'; text: string; time: string; };

const INITIAL_MEMORY: MemoryEvent[] = [
  {id: '1', type: 'blind-spot', text: 'Struggled with degrees of freedom calculation in 3 separate exercises.', time: '2h ago'},
  {id: '2', type: 'mastery', text: 'Mastered C-space topology concepts — consistently correct across 5 exercises.', time: '1d ago'},
  {id: '3', type: 'attempt', text: 'Completed "Exercise 2.1" with 2 hints used. Took 4:32.', time: '1d ago'},
  {id: '4', type: 'mastery', text: 'Forward kinematics product-of-exponentials — solved 3 in a row without hints.', time: '2d ago'},
  {id: '5', type: 'blind-spot', text: 'Consistently confused about SO(3) vs SE(3) distinction.', time: '3d ago'},
];

function MemoryPanel() {
  const [events, setEvents] = useState<MemoryEvent[]>(INITIAL_MEMORY);
  const [noteInput, setNoteInput] = useState('');
  const [showAdd, setShowAdd] = useState(false);

  const handleDismiss = (id: string) => {
    setEvents(prev => prev.filter(e => e.id !== id));
  };

  const handleAddNote = () => {
    if (!noteInput.trim()) return;
    const newEvent: MemoryEvent = {
      id: Date.now().toString(),
      type: 'note',
      text: noteInput.trim(),
      time: 'Just now',
    };
    setEvents(prev => [newEvent, ...prev]);
    setNoteInput('');
    setShowAdd(false);
  };

  return (
    <div className="flex flex-col h-full p-4 gap-4">
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
        <p className="text-ws-muted text-sm m-0">{events.length} learning events tracked</p>
        <button
          type="button"
          onClick={() => setShowAdd(!showAdd)}
          style={{
            background: 'none', border: '1px solid var(--ws-edge-soft)', borderRadius: "4px",
            padding: '3px 8px', cursor: 'pointer', color: "var(--ws-muted)", display: 'flex', alignItems: 'center', gap: 4,
            fontSize: 'var(--ws-type-xs)',
          }}
        >
          <Plus size={10} /> Add Note
        </button>
      </div>

      {showAdd && (
        <div style={{display: 'flex', gap: 6}}>
          <input
            type="text"
            className="flex-1 bg-ws-surface border border-ws-line rounded px-3 py-2 text-ws-ink outline-none focus:border-ws-success transition-colors"
            style={{flex: 1}}
            placeholder="Add a study note..."
            value={noteInput}
            onChange={e => setNoteInput(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter') handleAddNote(); }}
            autoFocus
          />
          <button
            type="button"
            className="bg-transparent border-none text-ws-muted cursor-pointer p-1 rounded hover:text-ws-soft"
            onClick={handleAddNote}
            style={{color: noteInput.trim() ? "var(--ws-accent)" : "var(--ws-muted)"}}
          >
            <Send size={14} />
          </button>
        </div>
      )}
      
      <div className="flex flex-col gap-3 overflow-y-auto flex-1" style={{paddingTop: 4}}>
        {events.map(event => (
          <div key={event.id} className="flex gap-3 pb-4 relative">
            <div className={`w-6 h-6 rounded-full flex items-center justify-center bg-ws-surface border border-ws-line shrink-0 z-10 ${event.type}`}>
              {event.type === 'blind-spot' && <AlertTriangle size={12} />}
              {event.type === 'mastery' && <CheckCircle size={12} />}
              {event.type === 'attempt' && <Brain size={12} />}
              {event.type === 'note' && <Plus size={12} />}
            </div>
            <div className="flex flex-col gap-1 pt-[2px]" style={{flex: 1}}>
              <div className="text-ws-soft leading-[1.4]">{event.text}</div>
              <div className="text-ws-muted text-xs">{event.time}</div>
            </div>
            <button
              type="button"
              onClick={() => handleDismiss(event.id)}
              style={{
                background: 'none', border: 'none', cursor: 'pointer', padding: 2,
                color: "var(--ws-muted)", opacity: 0.5, flexShrink: 0, alignSelf: 'flex-start',
              }}
              title="Dismiss"
            >
              <X size={12} />
            </button>
          </div>
        ))}
        {events.length === 0 && (
          <div style={{color: "var(--ws-muted)", fontSize: '11px', textAlign: 'center', padding: 'var(--ws-sp-6) 0'}}>
            No memory events. Add a note to get started.
          </div>
        )}
      </div>
    </div>
  );
}

export default MemoryPanel;

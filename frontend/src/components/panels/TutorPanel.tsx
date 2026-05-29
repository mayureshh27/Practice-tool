import {Send, Sparkles} from 'lucide-react';
import {useState, useRef, useEffect} from 'react';

type Message = {
  id: string;
  role: 'user' | 'assistant';
  content: string;
};

const INITIAL_MESSAGES: Message[] = [
  {id: '1', role: 'assistant', content: 'Hi! I am your project tutor. What would you like to explore about Modern Robotics?'},
  {id: '2', role: 'user', content: 'Can you explain the difference between C-space and Workspace?'},
  {id: '3', role: 'assistant', content: 'Configuration space (C-space) represents all possible configurations of the robot, while Workspace represents all points the end-effector can reach in physical space. Think of C-space as the "joint space".'}
];

function TutorPanel() {
  const [messages, setMessages] = useState<Message[]>(INITIAL_MESSAGES);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSend = () => {
    if (!input.trim()) return;
    
    const userMsg: Message = {id: Date.now().toString(), role: 'user', content: input.trim()};
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsTyping(true);

    // Simulate AI response
    setTimeout(() => {
      const aiMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `I can certainly help with that. Since this is an interactive mockup, I don't have the real backend yet, but I would normally retrieve chunks from your selected sources and formulate a Socratic response here!`
      };
      setMessages(prev => [...prev, aiMsg]);
      setIsTyping(false);
    }, 1200);
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-4">
        {messages.map(m => (
          <div key={m.id} className={`flex flex-col gap-1 max-w-[90%] ${m.role}`}>
            {m.role === 'assistant' && <Sparkles size={12} className="text-ws-success mb-[2px]" />}
            <div className="px-3 py-2 rounded-lg bg-ws-surface border border-ws-line leading-[1.4]">{m.content}</div>
          </div>
        ))}
        {isTyping && (
          <div className="flex flex-col gap-1 max-w-[90%] self-start">
            <Sparkles size={12} className="text-ws-success mb-[2px]" />
            <div className="px-3 py-2 rounded-lg bg-ws-surface border border-ws-line leading-[1.4]"><span className="text-ws-muted italic">Typing...</span></div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <div className="p-3 border-t border-ws-line flex gap-2 items-center bg-ws-bg">
        <input 
          type="text"
          className="flex-1 bg-ws-surface border border-ws-line rounded px-3 py-2 text-ws-ink outline-none focus:border-ws-success transition-colors"
          placeholder="Ask a question..."
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => {
            if (e.key === 'Enter') {
              e.preventDefault();
              handleSend();
            }
          }}
        />
        <button 
          type="button" 
          className={`bg-transparent border-none text-ws-muted cursor-pointer p-1 rounded hover:text-ws-soft ${input.trim() ? 'active' : ''}`}
          onClick={handleSend}
          title="Send"
        >
          <Send size={14} className={input.trim() ? 'text-ws-glow' : 'text-ws-ink-muted'} />
        </button>
      </div>
    </div>
  );
}

export default TutorPanel;

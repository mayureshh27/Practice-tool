import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown, Check } from 'lucide-react';

interface Option {
  value: string;
  label: string;
}

interface CustomSelectProps {
  value: string;
  onChange: (value: string) => void;
  options: Option[];
  style?: React.CSSProperties;
  className?: string;
  disabled?: boolean;
}

export function CustomSelect({ value, onChange, options, style, className, disabled }: CustomSelectProps) {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  
  const selectedOption = options.find(o => o.value === value);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div 
      ref={containerRef}
      className={className}
      style={{ position: 'relative', display: 'inline-block', opacity: disabled ? 0.5 : 1, ...style }}
    >
      <button
        type="button"
        disabled={disabled}
        onClick={() => setIsOpen(!isOpen)}
        style={{
          width: '100%', height: '100%',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8,
          background: 'transparent',
          border: 'none',
          color: 'inherit',
          fontSize: 'inherit',
          cursor: disabled ? 'not-allowed' : 'pointer',
          outline: 'none',
          whiteSpace: 'nowrap',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          padding: 0,
        }}
      >
        <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', flex: 1, textAlign: 'left' }}>
          {selectedOption ? selectedOption.label : 'Select...'}
        </span>
        <ChevronDown size={14} style={{ flexShrink: 0, color: "#71717a" }} />
      </button>

      {isOpen && !disabled && (
        <div style={{
          position: 'absolute', top: 'calc(100% + 4px)', left: 0, zIndex: 1000,
          minWidth: '100%', width: 'max-content',
          background: "#09090b", border: '1px solid var(--ws-edge)',
          borderRadius: "6px", padding: 4,
          boxShadow: '0 8px 24px rgba(0,0,0,0.4)',
          maxHeight: 300, overflowY: 'auto',
          display: 'flex', flexDirection: 'column', gap: 2
        }}>
          {options.map(opt => (
            <button
              key={opt.value}
              type="button"
              onClick={() => {
                onChange(opt.value);
                setIsOpen(false);
              }}
              style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                width: '100%', padding: '8px 12px',
                background: 'none', border: 'none', borderRadius: "4px",
                color: value === opt.value ? "#10b981" : "#f4f4f5", 
                fontSize: 13, cursor: 'pointer', textAlign: 'left',
                whiteSpace: 'nowrap'
              }}
              onMouseEnter={e => {
                e.currentTarget.style.background = "#27272a";
              }}
              onMouseLeave={e => {
                e.currentTarget.style.background = 'none';
              }}
            >
              {opt.label}
              {value === opt.value && <Check size={14} style={{ color: "#10b981", marginLeft: 12 }} />}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

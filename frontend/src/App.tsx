import {useEffect,useMemo,useState} from 'react';
import Editor from '@monaco-editor/react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {BookOpen, CheckCircle2, FileText, GraduationCap, Play, Search, Send, Upload} from 'lucide-react';
import './index.css';

type Problem={id:string;number:number;title:string;chapter:string;difficulty:string;tags:string[];statement:string;explanation:string;lessonTitle?:string;lesson?:string;approach?:string;pitfalls?:string[];hints:string[];starterCode:string;solutionCode:string;exerciseMode?:string;verifier?:string;examples:{input:string;output:string}[]}
type Store={chapters:{id:string;title:string}[];problems:Problem[]}
type Tab='study'|'problem'|'solution'

const API=import.meta.env.VITE_API_URL||'http://localhost:8080';

function md(text:string){return <ReactMarkdown remarkPlugins={[remarkGfm]}>{text}</ReactMarkdown>}
function chipText(p:Problem){return p.exerciseMode==='judge'?'Judge':'Project'}
function shortTitle(p:Problem){return p.title.replace(/^Exercise \d+\.\d+: /,'')}

function App(){
  const [store,setStore]=useState<Store>({chapters:[],problems:[]});
  const [pid,setPid]=useState('');
  const [query,setQuery]=useState('');
  const [chapter,setChapter]=useState('all');
  const [mode,setMode]=useState('all');
  const [code,setCode]=useState('');
  const [out,setOut]=useState('');
  const [verdict,setVerdict]=useState('');
  const [tab,setTab]=useState<Tab>('study');
  const [uploaded,setUploaded]=useState<{name:string; text:string}[]>([]);
  const [solved,setSolved]=useState<string[]>(()=>JSON.parse(localStorage.getItem('solved')||'[]'));

  useEffect(()=>{fetch(API+'/api/problems').then(r=>r.json()).then(s=>{setStore(s); setPid(s.problems[0]?.id||''); setCode(s.problems[0]?.starterCode||'')})},[]);

  const problem=store.problems.find(p=>p.id===pid);
  const progress=Math.round((solved.length/Math.max(store.problems.length,1))*100);
  const judgeCount=store.problems.filter(p=>p.exerciseMode==='judge').length;
  const needsFiles=!!problem && (problem.tags.includes('file') || /file|stdin|read/i.test(problem.statement));
  const filtered=useMemo(()=>store.problems.filter(p=>(chapter==='all'||p.chapter===chapter)&&(mode==='all'||p.exerciseMode===mode)&&((p.title+p.tags.join(' ')+p.statement+(p.lesson||'')).toLowerCase().includes(query.toLowerCase()))),[store,query,chapter,mode]);

  function select(p:Problem){
    setPid(p.id);
    setCode(localStorage.getItem('draft:'+p.id)||p.starterCode);
    setUploaded(JSON.parse(localStorage.getItem('files:'+p.id)||'[]'));
    setOut('');
    setVerdict('');
    setTab('study');
  }
  function selectById(id:string){
    const next=store.problems.find(p=>p.id===id);
    if(next) select(next);
  }
  function saveDraft(v:string|undefined){
    const c=v||'';
    setCode(c);
    if(problem)localStorage.setItem('draft:'+problem.id,c);
  }
  async function addFiles(list:FileList|null){
    if(!problem||!list) return;
    const files=await Promise.all(Array.from(list).map(async f=>({name:f.name,text:await f.text()})));
    const next=[...uploaded,...files];
    setUploaded(next);
    localStorage.setItem('files:'+problem.id,JSON.stringify(next));
    setOut(`### Uploaded files\n\n${next.map(f=>`- **${f.name}** (${f.text.length} chars)`).join('\n')}\n\nUse these as your sample inputs while solving this file-based exercise.`);
    setVerdict('Files ready');
  }
  function clearFiles(){
    if(!problem) return;
    setUploaded([]);
    localStorage.removeItem('files:'+problem.id);
    setOut('');
    setVerdict('');
  }
  async function run(mode:string){
    setVerdict('Running...');
    setOut('');
    const r=await fetch(API+'/api/run',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({problemId:pid,code,mode})});
    const j=await r.json();
    const body=(j.error?`### Error\n\n\`\`\`text\n${j.error}\n\`\`\`\n\n`:'')+`### Output\n\n\`\`\`text\n${j.output}\n\`\`\`\n\n**Time:** ${j.durationMs}ms`;
    setVerdict(j.verdict);
    setOut(body);
    if(mode==='submit'&&j.verdict==='Accepted'&&problem){
      const ns=[...new Set([...solved,problem.id])];
      setSolved(ns);
      localStorage.setItem('solved',JSON.stringify(ns));
    }
  }

  return <div className="app-shell">
    <header className="topbar">
      <div className="brand-lockup">
        <div className="go-logo-wrap"><img src="/go-logo.svg" alt="Go" /></div>
        <div><h1>PracDaGo</h1><p>book-first Go practice</p></div>
      </div>
      <div className="progress-summary">
        <span>{judgeCount} judgeable</span>
        <span>{solved.length}/{store.problems.length} solved</span>
        <div className="progress-track"><div className="progressbar" style={{width:progress+'%'}}/></div>
        <span>{progress}%</span>
      </div>
    </header>

    <div className="workspace-layout">
      <aside className="problem-nav">
        <div className="nav-tools">
          <label className="search-field"><Search size={15}/><input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search exercises"/></label>
          <select value={chapter} onChange={e=>setChapter(e.target.value)}><option value="all">All chapters</option>{store.chapters.map(c=><option key={c.id} value={c.id}>{c.id.toUpperCase().replace('CH','Ch ')} · {c.title}</option>)}</select>
          <div className="mode-toggle"><button onClick={()=>setMode('all')} className={mode==='all'?'active':''}>All</button><button onClick={()=>setMode('judge')} className={mode==='judge'?'active':''}>Judge</button><button onClick={()=>setMode('project')} className={mode==='project'?'active':''}>Project</button></div>
          <select className="mobile-problem-select" value={pid} onChange={e=>selectById(e.target.value)}>{filtered.map(p=><option key={p.id} value={p.id}>{p.number}. {shortTitle(p)}</option>)}</select>
        </div>
        <div className="side-stats"><div><b>{filtered.length}</b><span>shown</span></div><div><b>{judgeCount}</b><span>judge</span></div><div><b>{store.problems.length-judgeCount}</b><span>projects</span></div></div>
        <div className="problem-list scrollbar">{filtered.map(p=><button key={p.id} onClick={()=>select(p)} className={`problem-row ${p.id===pid?'problem-active':''}`}><div><span className="problem-number">{p.number}.</span> {shortTitle(p)}</div><span>{chipText(p)} · {p.tags.slice(0,2).join(', ')}</span>{solved.includes(p.id)&&<CheckCircle2 size={15}/>}</button>)}</div>
      </aside>

      <main className="workspace-main">{problem&&<>
        <section className="learning-panel">
          <div className="section-header">
            <div className="section-kicker"><BookOpen size={16}/> Exercise workspace</div>
            <h2>{problem.title}</h2>
            <div className="chip-row"><span className="chip">{problem.exerciseMode==='judge'?'Local judge':'Project-style'}</span>{problem.tags.slice(0,4).map(t=><span className="chip" key={t}>{t}</span>)}</div>
            <div className="tab-row"><button className={tab==='study'?'active':''} onClick={()=>setTab('study')}><GraduationCap size={14}/> Study</button><button className={tab==='problem'?'active':''} onClick={()=>setTab('problem')}>Problem</button><button className={tab==='solution'?'active':''} onClick={()=>setTab('solution')}>Explain</button></div>
          </div>
          <div className="content-scroll markdown-body scrollbar">{tab==='study'&&<>{md(`### ${problem.lessonTitle}\n\n${problem.lesson||''}\n\n### How to attack this\n\n${problem.approach||''}\n\n### Common traps\n\n${(problem.pitfalls||[]).map(x=>`- ${x}`).join('\n')}`)}</>}{tab==='problem'&&<>{md(`### Task\n\n${problem.statement}\n\n### Examples\n\n${problem.examples.map(e=>`\`\`\`text\nInput: ${e.input}\nOutput: ${e.output}\n\`\`\``).join('\n\n')}\n\n### Hints\n\n${problem.hints.map(h=>`- ${h}`).join('\n')}`)}</>}{tab==='solution'&&<>{md(`### Detailed explanation\n\n${problem.explanation}\n\n### Reference solution\n\n\`\`\`go\n${problem.solutionCode}\n\`\`\``)}</>}</div>
        </section>

        <section className="work-panel">
          <div className="editor-toolbar">
            <div><b>{needsFiles?'File workspace':'Go editor'}</b><span>{needsFiles?'Upload sample input files for this exercise':'Drafts save locally'}</span></div>
            <div className="run-actions">{needsFiles&&<label className="btn2 cursor-pointer"><Upload size={15}/> Upload<input type="file" multiple className="hidden" onChange={e=>addFiles(e.target.files)}/></label>}<button className="btn2" onClick={()=>run('run')}><Play size={15}/> Run</button><button className="btn" onClick={()=>run('submit')}><Send size={15}/> Submit</button></div>
          </div>
          {needsFiles?<div className="file-workspace scrollbar">
            <div className="drop-card"><Upload size={28}/><h3>Upload input files</h3><p>For file-based book exercises, upload sample files here instead of treating it like a pure LeetCode prompt. Files are saved in browser localStorage for this exercise.</p><label className="btn cursor-pointer mt-3 inline-flex">Choose files<input type="file" multiple className="hidden" onChange={e=>addFiles(e.target.files)}/></label></div>
            {uploaded.length>0&&<div className="uploaded-files"><div className="uploaded-head"><b>{uploaded.length} uploaded</b><button onClick={clearFiles}>Clear</button></div>{uploaded.map((f,i)=><div key={i} className="file-card"><div><FileText size={16}/><b>{f.name}</b><span>{f.text.length} chars</span></div><pre>{f.text.slice(0,2000)}{f.text.length>2000?'\n...':''}</pre></div>)}</div>}
            <div className="optional-editor"><span>Optional Go draft</span><div className="editor-frame compact"><Editor height="100%" defaultLanguage="go" theme="vs-dark" value={code} onChange={saveDraft} options={{fontSize:14,fontFamily:'JetBrains Mono, monospace',minimap:{enabled:false},scrollBeyondLastLine:false,renderLineHighlight:'all',padding:{top:16}}}/></div></div>
          </div>:<div className="editor-frame"><Editor height="100%" defaultLanguage="go" theme="vs-dark" value={code} onChange={saveDraft} options={{fontSize:14,fontFamily:'JetBrains Mono, monospace',minimap:{enabled:false},scrollBeyondLastLine:false,renderLineHighlight:'all',padding:{top:16}}}/></div>}
          <div className="output-panel markdown-body scrollbar"><div className={`verdict ${verdict==='Accepted'?'ok':verdict==='Error'?'bad':''}`}>{verdict||'Output'}</div>{out?md(out):md(needsFiles?"Upload files to preview them here. Use Run for optional Go drafts.":"Run code to see formatted output. Project-style tasks use Run mode plus the study guide's reproducible proof.")}</div>
        </section>
      </>}</main>
    </div>
  </div>
}

export default App

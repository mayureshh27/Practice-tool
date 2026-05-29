import { createFileRoute } from '@tanstack/react-router'
import { useState } from 'react'
import ProblemNav from '../../../../../components/ProblemNav'
import LearningPanel from '../../../../../components/LearningPanel'
import { useWorkspaceStore } from '../../../../../stores/workspaceStore'
import { useQuery } from '@tanstack/react-query'
import { api } from '../../../../../api/workspaceApi'

import WorkPanel from '../../../../../components/WorkPanel'

export const Route = createFileRoute('/topic/$domainId/$subjectId/$chapterId/$topicId')({
  component: TopicRoute,
})

function TopicRoute() {
  const { domainId, subjectId, chapterId, topicId } = Route.useParams()
  const [practiceNavCollapsed, setPracticeNavCollapsed] = useState(false)
  const [tab, setTab] = useState<'problem' | 'solution' | 'notebook' | 'debug'>('problem')

  const { data: topic, isLoading } = useQuery({
    queryKey: ['topic', domainId, subjectId, chapterId, topicId],
    queryFn: () => api.getTopic(domainId, subjectId, chapterId, topicId)
  })

  // Temporary dummy state for practice until Phase 4
  const store = { problems: [] }
  const filtered: any[] = []
  const pid = ''
  
  if (isLoading) {
    return <div style={{ padding: 40, textAlign: 'center', color: "#71717a" }}>Loading topic...</div>
  }

  if (!topic) {
    return <div style={{ padding: 40, textAlign: 'center', color: "#71717a" }}>Topic not found.</div>
  }
  
  const problem = {
    id: topic.id,
    title: topic.name,
    body: `### Welcome to ${topic.name}\n\nStart your learning journey here.`,
    examples: [],
    hints: [],
    type: 'code',
    difficulty: 'easy'
  };
  return (
    <div className="ws-practice">
      <div className={`workspace-layout ${practiceNavCollapsed ? 'collapsed' : ''}`}>
        <ProblemNav
          store={store}
          filtered={filtered}
          pid={pid}
          query=""
          chapter={chapterId}
          mode="all"
          judgeCount={0}
          solved={[]}
          onQuery={() => {}}
          onChapter={() => {}}
          onMode={() => {}}
          onSelect={() => {}}
          onSelectById={() => {}}
          collapsed={practiceNavCollapsed}
          onToggleCollapse={() => setPracticeNavCollapsed(c => !c)}
          onSearchTrigger={() => {}}
        />
        <main className="workspace-main">
          {problem ? (
            <>
              <LearningPanel problem={problem} tab={tab} onTab={setTab} />
              <WorkPanel
                needsFiles={false}
                canSubmitProblem={false}
                code=""
                theme="light"
                runningMode="run"
                uploaded={[]}
                proofReady={false}
                solved={false}
                verdict="None"
                output=""
                comparison={null}
                onSaveDraft={() => {}}
                onResetDraft={() => {}}
                onAddFiles={() => {}}
                onClearFiles={() => {}}
                onRun={async () => {}}
                onMarkComplete={() => {}}
              />
            </>
          ) : (
            <section className="learning-panel">
              <div className="content-scroll markdown-body scrollbar">
                <h3>Loading practice environment</h3>
                <p>Migration to TanStack Query in progress...</p>
              </div>
            </section>
          )}
        </main>
      </div>
    </div>
  )
}

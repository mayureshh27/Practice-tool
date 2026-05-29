import { createFileRoute } from '@tanstack/react-router'
import { useState } from 'react'
import ProblemNav from '../../../../../components/ProblemNav'
import LearningPanel from '../../../../../components/LearningPanel'
import WorkPanel from '../../../../../components/WorkPanel'
import type { FlowTab } from '../../../../../types'
import { useQuery } from '@tanstack/react-query'
import { api } from '../../../../../api/workspaceApi'

import { useEffect } from 'react'
import { useWorkspaceStore } from '../../../../../stores/workspaceStore'

export const Route = createFileRoute('/topic/$domainId/$subjectId/$chapterId/$topicId')({
  component: TopicRoute,
})

function TopicRoute() {
  const { domainId, subjectId, chapterId, topicId } = Route.useParams()
  const [practiceNavCollapsed, setPracticeNavCollapsed] = useState(false)
  const [tab, setTab] = useState<FlowTab>('problem')

  const { data: topic, isLoading } = useQuery({
    queryKey: ['topic', domainId, subjectId, chapterId, topicId],
    queryFn: () => api.getTopic(domainId, subjectId, chapterId, topicId)
  })

  const addToRecents = useWorkspaceStore(s => s.addToRecents)

  useEffect(() => {
    if (topic) {
      addToRecents(topic.name, 'topic', { level: 'topic', domainId, subjectId, chapterId, topicId })
    }
  }, [topic, domainId, subjectId, chapterId, topicId, addToRecents])

  const store = { chapters: [], problems: [] }
  const filtered: any[] = []
  const pid = ''

  if (isLoading) {
    return <div style={{ padding: 40, textAlign: 'center', color: 'var(--ws-muted)' }}>Loading topic...</div>
  }

  if (!topic) {
    return <div style={{ padding: 40, textAlign: 'center', color: 'var(--ws-muted)' }}>Topic not found.</div>
  }

  // Build a stub Problem that satisfies the Problem type for LearningPanel
  const problem = {
    id: topic.id,
    number: 0,
    title: topic.name,
    chapter: chapterId,
    difficulty: 'easy',
    tags: [],
    statement: `## ${topic.name}\n\nStart your learning journey here.`,
    explanation: `## ${topic.name}\n\nStart your learning journey here.`,
    hints: [],
    starterCode: '',
    solutionCode: '',
    examples: [],
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
          <>
            <LearningPanel problem={problem} tab={tab} onTab={setTab} />
            <WorkPanel
              needsFiles={false}
              canSubmitProblem={false}
              code=""
              theme="light"
              runningMode={null as any}
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
        </main>
      </div>
    </div>
  )
}

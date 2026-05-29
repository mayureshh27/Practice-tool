import { createFileRoute } from '@tanstack/react-router'
import ChapterScreen from '../../../../components/ChapterScreen'
import { useQuery } from '@tanstack/react-query'
import { api } from '../../../../api/workspaceApi'
import { useWorkspaceStore } from '../../../../stores/workspaceStore'

import { useEffect } from 'react'

export const Route = createFileRoute(
  '/chapter/$domainId/$subjectId/$chapterId',
)({
  component: ChapterRoute,
})

function ChapterRoute() {
  const { domainId, subjectId, chapterId } = Route.useParams()
  const { data: domain, isLoading } = useQuery({
    queryKey: ['domain', domainId],
    queryFn: () => api.getDomain(domainId)
  })

  const updateChapter = useWorkspaceStore((s) => s.updateChapter)
  const removeResource = useWorkspaceStore((s) => s.removeResource)
  const addToRecents = useWorkspaceStore((s) => s.addToRecents)

  const subject = domain?.subjects.find((s) => s.id === subjectId)
  const chapter = subject?.chapters.find((c) => c.id === chapterId)

  useEffect(() => {
    if (chapter) {
      addToRecents(chapter.name, 'chapter', { level: 'chapter', domainId, subjectId, chapterId })
    }
  }, [chapter, domainId, subjectId, chapterId, addToRecents])

  if (isLoading) {
    return <div style={{ padding: 40, textAlign: 'center', color: "var(--ws-muted)" }}>Loading...</div>
  }

  if (!domain || !subject || !chapter) {
    return (
      <div
        style={{ padding: 40, textAlign: 'center', color: "var(--ws-muted)" }}
      >
        Chapter not found.
      </div>
    )
  }

  return (
    <ChapterScreen
      domain={domain}
      subject={subject}
      chapter={chapter}
      onNavigate={() => {}}
      onUpdateChapter={updateChapter}
      onRemoveResource={removeResource}
    />
  )
}

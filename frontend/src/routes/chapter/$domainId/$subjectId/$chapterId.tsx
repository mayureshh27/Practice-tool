import { createFileRoute } from '@tanstack/react-router'
import ChapterScreen from '../../../../components/ChapterScreen'
import { useQuery } from '@tanstack/react-query'
import { api } from '../../../../api/workspaceApi'
import { useWorkspaceStore } from '../../../../stores/workspaceStore'

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

  if (isLoading) {
    return <div style={{ padding: 40, textAlign: 'center', color: "#71717a" }}>Loading...</div>
  }

  const subject = domain?.subjects.find((s) => s.id === subjectId)
  const chapter = subject?.chapters.find((c) => c.id === chapterId)

  if (!domain || !subject || !chapter) {
    return (
      <div
        style={{ padding: 40, textAlign: 'center', color: "#71717a" }}
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

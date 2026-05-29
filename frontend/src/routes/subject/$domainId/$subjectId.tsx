import { createFileRoute } from '@tanstack/react-router'
import SubjectScreen from '../../../components/SubjectScreen'
import { useQuery } from '@tanstack/react-query'
import { api } from '../../../api/workspaceApi'
import { useWorkspaceStore } from '../../../stores/workspaceStore'

export const Route = createFileRoute('/subject/$domainId/$subjectId')({
  component: SubjectRoute,
})

function SubjectRoute() {
  const { domainId, subjectId } = Route.useParams()
  const { data: domain, isLoading } = useQuery({
    queryKey: ['domain', domainId],
    queryFn: () => api.getDomain(domainId)
  })

  const updateSubject = useWorkspaceStore(s => s.updateSubject)
  const removeResource = useWorkspaceStore(s => s.removeResource)

  if (isLoading) {
    return <div style={{padding: 40, textAlign: 'center', color: "#71717a"}}>Loading...</div>
  }

  const subject = domain?.subjects.find(s => s.id === subjectId)

  if (!domain || !subject) {
    return <div style={{padding: 40, textAlign: 'center', color: "#71717a"}}>Subject not found.</div>
  }

  return (
    <SubjectScreen
      domain={domain}
      subject={subject}
      onNavigate={() => {}}
      onUpdateSubject={updateSubject}
      onRemoveResource={removeResource}
      onOpenCreateModal={() => {}}
    />
  )
}

import { createFileRoute } from '@tanstack/react-router'
import { DomainScreen } from '../../components/ExplorerScreens'
import { useQuery } from '@tanstack/react-query'
import { api } from '../../api/workspaceApi'
import { useWorkspaceStore } from '../../stores/workspaceStore'

export const Route = createFileRoute('/domain/$domainId')({
  component: DomainRoute,
})

function DomainRoute() {
  const { domainId } = Route.useParams()

  const { data: domain, isLoading } = useQuery({
    queryKey: ['domain', domainId],
    queryFn: () => api.getDomain(domainId)
  })

  const renameSubject = useWorkspaceStore(s => s.renameSubject)
  const deleteSubject = useWorkspaceStore(s => s.deleteSubject)

  if (isLoading) {
    return <div style={{padding: 40, textAlign: 'center', color: "#71717a"}}>Loading...</div>
  }

  if (!domain) {
    return <div style={{padding: 40, textAlign: 'center', color: "#71717a"}}>Domain not found.</div>
  }

  return (
    <DomainScreen
      domain={domain}
      onNavigate={() => {}}
      onOpenCreateModal={() => {}}
      onRenameSubject={renameSubject}
      onDeleteSubject={deleteSubject}
    />
  )
}

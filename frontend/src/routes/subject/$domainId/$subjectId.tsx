import { createFileRoute } from '@tanstack/react-router'
import SubjectScreen from '../../../components/SubjectScreen'
import { useQuery } from '@tanstack/react-query'
import { api } from '../../../api/workspaceApi'
import { useWorkspaceStore } from '../../../stores/workspaceStore'

import { useEffect } from 'react'
import { useUIStore } from '../../../stores/uiStore'

export const Route = createFileRoute('/subject/$domainId/$subjectId')({
  component: SubjectRoute,
})

function SubjectRoute() {
  const { domainId, subjectId } = Route.useParams()
  const setCreationModal = useUIStore(s => s.setCreationModal)
  const { data: domain, isLoading } = useQuery({
    queryKey: ['domain', domainId],
    queryFn: () => api.getDomain(domainId)
  })

  const updateSubject = useWorkspaceStore(s => s.updateSubject)
  const removeResource = useWorkspaceStore(s => s.removeResource)
  const addToRecents = useWorkspaceStore(s => s.addToRecents)

  const subject = domain?.subjects.find(s => s.id === subjectId)

  useEffect(() => {
    if (subject) {
      addToRecents(subject.name, 'subject', { level: 'subject', domainId, subjectId })
    }
  }, [subject, domainId, subjectId, addToRecents])

  if (isLoading) {
    return <div style={{padding: 40, textAlign: 'center', color: "var(--ws-muted)"}}>Loading...</div>
  }

  if (!domain || !subject) {
    return <div style={{padding: 40, textAlign: 'center', color: "var(--ws-muted)"}}>Subject not found.</div>
  }

  return (
    <SubjectScreen
      domain={domain}
      subject={subject}
      onNavigate={() => {}}
      onUpdateSubject={updateSubject}
      onRemoveResource={removeResource}
      onOpenCreateModal={(type, dId, sId) => setCreationModal({ open: true, type: type as any, domainId: dId, subjectId: sId })}
    />
  )
}

import { createFileRoute, useNavigate } from '@tanstack/react-router'
import SourceNotebookScreen from '../../../components/SourceNotebookScreen'
import { useWorkspaceStore } from '../../../stores/workspaceStore'

export const Route = createFileRoute('/notebook/$domainId/$subjectId')({
  component: NotebookRoute,
})

function NotebookRoute() {
  const { domainId, subjectId } = Route.useParams()
  const domains = useWorkspaceStore(s => s.domains)
  const notebooks = useWorkspaceStore(s => s.notebooks)
  const createNotebook = useWorkspaceStore(s => s.createNotebook)
  const deleteNotebook = useWorkspaceStore(s => s.deleteNotebook)
  const navigate = useNavigate()

  const domain = domains.find(d => d.id === domainId)
  const subject = domain?.subjects.find(s => s.id === subjectId)

  if (!domain || !subject) {
    return <div style={{padding: 40, textAlign: 'center', color: "#71717a"}}>Notebook target not found.</div>
  }

  return (
    <SourceNotebookScreen
      domain={domain}
      subject={subject}
      notebooks={notebooks}
      onNavigate={(loc: any) => {
        if (loc.level === 'subject') navigate({ to: `/subject/${loc.domainId}/${loc.subjectId}` })
      }}
      onCreateNotebook={createNotebook}
      onDeleteNotebook={deleteNotebook}
    />
  )
}

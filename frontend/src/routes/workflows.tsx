import { createFileRoute } from '@tanstack/react-router'
import WorkflowManagerScreen from '../components/WorkflowManagerScreen'
import { useWorkspaceStore } from '../stores/workspaceStore'

export const Route = createFileRoute('/workflows')({
  component: WorkflowsRoute,
})

function WorkflowsRoute() {
  const workflows = useWorkspaceStore(s => s.workflows)
  const deleteWorkflow = useWorkspaceStore(s => s.deleteWorkflow)
  const duplicateWorkflow = useWorkspaceStore(s => s.duplicateWorkflow)

  return (
    <WorkflowManagerScreen
      workflows={workflows}
      onNavigate={() => {}}
      onDelete={deleteWorkflow}
      onDuplicate={duplicateWorkflow}
    />
  )
}

import { createFileRoute } from '@tanstack/react-router'
import WorkflowEditorScreen from '../components/WorkflowEditorScreen'
import { useWorkspaceStore } from '../stores/workspaceStore'

export const Route = createFileRoute('/workflow-editor')({
  component: WorkflowEditorRoute,
})

function WorkflowEditorRoute() {
  const workflows = useWorkspaceStore(s => s.workflows)
  const updateWorkflow = useWorkspaceStore(s => s.updateWorkflow)

  return (
    <WorkflowEditorScreen
      workflows={workflows}
      onNavigate={() => {}}
      onSaveWorkflow={updateWorkflow}
    />
  )
}

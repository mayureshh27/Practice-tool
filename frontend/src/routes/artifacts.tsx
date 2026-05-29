import { createFileRoute } from '@tanstack/react-router'
import ArtifactViewerScreen from '../components/ArtifactViewerScreen'
import { useWorkspaceStore } from '../stores/workspaceStore'

export const Route = createFileRoute('/artifacts')({
  component: ArtifactsRoute,
})

function ArtifactsRoute() {
  const artifacts = useWorkspaceStore(s => s.artifacts)
  const domains = useWorkspaceStore(s => s.domains)
  const deleteArtifact = useWorkspaceStore(s => s.deleteArtifact)

  return (
    <ArtifactViewerScreen
      artifacts={artifacts}
      domains={domains}
      onDelete={deleteArtifact}
    />
  )
}

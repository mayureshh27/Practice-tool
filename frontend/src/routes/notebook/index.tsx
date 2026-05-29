import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/notebook/')({
  component: NotebookIndexRoute,
})

function NotebookIndexRoute() {
  return (
    <div style={{padding: '32px 24px', maxWidth: 1000, margin: '0 auto', height: '100%', overflowY: 'auto'}}>
      <div style={{marginBottom: 28}}>
        <h1 style={{fontSize: 24, fontWeight: 800, color: "var(--ws-ink)", margin: '0 0 6px', letterSpacing: '-0.02em'}}>
          Reference Source Notebooks
        </h1>
        <p style={{fontSize: 13, color: "var(--ws-soft)", margin: 0}}>
          Please select a Subject from the Left Navigation to access its source notebook.
        </p>
      </div>
    </div>
  )
}

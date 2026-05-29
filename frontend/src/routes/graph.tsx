import { createFileRoute } from '@tanstack/react-router'
import GraphScreen from '../components/GraphScreen'

export const Route = createFileRoute('/graph')({
  component: GraphRoute,
})

function GraphRoute() {
  return <GraphScreen />
}

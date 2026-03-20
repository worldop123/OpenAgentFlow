import React, { createContext, useContext, useState, ReactNode } from 'react'
import { Edge, Node } from 'reactflow'

export type WorkflowNode = Node & {
  type: 'agent' | 'condition' | 'action' | 'input' | 'output'
  agentId?: string
  config?: Record<string, any>
}

export type WorkflowEdge = Edge

export interface Workflow {
  id: string
  name: string
  description: string
  nodes: WorkflowNode[]
  edges: WorkflowEdge[]
  createdAt: Date
  updatedAt: Date
}

interface WorkflowContextType {
  workflows: Workflow[]
  activeWorkflow: Workflow | null
  selectedNode: WorkflowNode | null
  selectedEdge: WorkflowEdge | null
  isDirty: boolean
  addWorkflow: (workflow: Omit<Workflow, 'id' | 'createdAt' | 'updatedAt'>) => void
  updateWorkflow: (id: string, updates: Partial<Workflow>) => void
  deleteWorkflow: (id: string) => void
  setActiveWorkflow: (workflow: Workflow | null) => void
  updateActiveWorkflow: (nodes: WorkflowNode[], edges: WorkflowEdge[]) => void
  setSelectedNode: (node: WorkflowNode | null) => void
  setSelectedEdge: (edge: WorkflowEdge | null) => void
  markAsDirty: (dirty: boolean) => void
}

const WorkflowContext = createContext<WorkflowContextType | undefined>(undefined)

export const useWorkflow = () => {
  const context = useContext(WorkflowContext)
  if (!context) {
    throw new Error('useWorkflow must be used within a WorkflowProvider')
  }
  return context
}

interface WorkflowProviderProps {
  children: ReactNode
}

export const WorkflowProvider: React.FC<WorkflowProviderProps> = ({ children }) => {
  const [workflows, setWorkflows] = useState<Workflow[]>([
    {
      id: '1',
      name: 'Customer Support Automation',
      description: 'Automated customer inquiry handling workflow',
      nodes: [
        {
          id: 'node-1',
          type: 'input',
          position: { x: 100, y: 100 },
          data: { label: 'Customer Inquiry' },
        },
        {
          id: 'node-2',
          type: 'agent',
          position: { x: 300, y: 100 },
          data: { label: 'AI Support Agent' },
          agentId: 'support-agent',
        },
        {
          id: 'node-3',
          type: 'condition',
          position: { x: 500, y: 100 },
          data: { label: 'Needs Human?' },
        },
      ],
      edges: [
        { id: 'edge-1', source: 'node-1', target: 'node-2' },
        { id: 'edge-2', source: 'node-2', target: 'node-3' },
      ],
      createdAt: new Date(),
      updatedAt: new Date(),
    },
  ])

  const [activeWorkflow, setActiveWorkflow] = useState<Workflow | null>(null)
  const [selectedNode, setSelectedNode] = useState<WorkflowNode | null>(null)
  const [selectedEdge, setSelectedEdge] = useState<WorkflowEdge | null>(null)
  const [isDirty, setIsDirty] = useState(false)

  const addWorkflow = (workflow: Omit<Workflow, 'id' | 'createdAt' | 'updatedAt'>) => {
    const newWorkflow: Workflow = {
      ...workflow,
      id: `wf-${Date.now()}`,
      createdAt: new Date(),
      updatedAt: new Date(),
    }
    setWorkflows((prev) => [...prev, newWorkflow])
    setActiveWorkflow(newWorkflow)
    setIsDirty(true)
  }

  const updateWorkflow = (id: string, updates: Partial<Workflow>) => {
    setWorkflows((prev) =>
      prev.map((workflow) =>
        workflow.id === id
          ? {
              ...workflow,
              ...updates,
              updatedAt: new Date(),
            }
          : workflow
      )
    )
    if (activeWorkflow?.id === id) {
      setActiveWorkflow((prev) =>
        prev ? { ...prev, ...updates, updatedAt: new Date() } : null
      )
    }
    setIsDirty(true)
  }

  const deleteWorkflow = (id: string) => {
    setWorkflows((prev) => prev.filter((workflow) => workflow.id !== id))
    if (activeWorkflow?.id === id) {
      setActiveWorkflow(null)
      setSelectedNode(null)
      setSelectedEdge(null)
    }
  }

  const updateActiveWorkflow = (nodes: WorkflowNode[], edges: WorkflowEdge[]) => {
    if (activeWorkflow) {
      const updatedWorkflow = {
        ...activeWorkflow,
        nodes,
        edges,
        updatedAt: new Date(),
      }
      setActiveWorkflow(updatedWorkflow)
      setWorkflows((prev) =>
        prev.map((w) => (w.id === activeWorkflow.id ? updatedWorkflow : w))
      )
      setIsDirty(true)
    }
  }

  const markAsDirty = (dirty: boolean) => {
    setIsDirty(dirty)
  }

  const value: WorkflowContextType = {
    workflows,
    activeWorkflow,
    selectedNode,
    selectedEdge,
    isDirty,
    addWorkflow,
    updateWorkflow,
    deleteWorkflow,
    setActiveWorkflow,
    updateActiveWorkflow,
    setSelectedNode,
    setSelectedEdge,
    markAsDirty,
  }

  return <WorkflowContext.Provider value={value}>{children}</WorkflowContext.Provider>
}
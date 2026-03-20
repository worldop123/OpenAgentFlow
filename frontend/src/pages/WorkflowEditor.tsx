import React, { useState, useCallback } from 'react'
import ReactFlow, {
  Node,
  Edge,
  Connection,
  addEdge,
  applyNodeChanges,
  applyEdgeChanges,
  NodeChange,
  EdgeChange,
  Controls,
  Background,
  MiniMap,
  Panel,
} from 'reactflow'
import 'reactflow/dist/style.css'
import { useWorkflow } from '../contexts/WorkflowContext'
import AgentNode from '../components/Nodes/AgentNode'
import ConditionNode from '../components/Nodes/ConditionNode'
import ActionNode from '../components/Nodes/ActionNode'
import { Plus, Save, Play, Download, Upload } from 'lucide-react'
import toast from 'react-hot-toast'

// Register custom node types
const nodeTypes = {
  agent: AgentNode,
  condition: ConditionNode,
  action: ActionNode,
}

const WorkflowEditor: React.FC = () => {
  const { 
    activeWorkflow, 
    updateActiveWorkflow, 
    selectedNode, 
    setSelectedNode,
    markAsDirty 
  } = useWorkflow()
  
  const [nodeName, setNodeName] = useState('')
  const [nodeType, setNodeType] = useState<'agent' | 'condition' | 'action'>('agent')
  
  const onNodesChange = useCallback(
    (changes: NodeChange[]) => {
      if (activeWorkflow) {
        const updatedNodes = applyNodeChanges(changes, activeWorkflow.nodes)
        updateActiveWorkflow(updatedNodes, activeWorkflow.edges)
      }
    },
    [activeWorkflow, updateActiveWorkflow]
  )
  
  const onEdgesChange = useCallback(
    (changes: EdgeChange[]) => {
      if (activeWorkflow) {
        const updatedEdges = applyEdgeChanges(changes, activeWorkflow.edges)
        updateActiveWorkflow(activeWorkflow.nodes, updatedEdges)
      }
    },
    [activeWorkflow, updateActiveWorkflow]
  )
  
  const onConnect = useCallback(
    (connection: Connection) => {
      if (activeWorkflow) {
        const edge = { ...connection, id: `edge-${Date.now()}` }
        const updatedEdges = addEdge(edge, activeWorkflow.edges)
        updateActiveWorkflow(activeWorkflow.nodes, updatedEdges)
      }
    },
    [activeWorkflow, updateActiveWorkflow]
  )
  
  const addNewNode = () => {
    if (!nodeName.trim()) {
      toast.error('Please enter a node name')
      return
    }
    
    if (activeWorkflow) {
      const newNode: Node = {
        id: `node-${Date.now()}`,
        type: nodeType,
        position: {
          x: Math.random() * 400,
          y: Math.random() * 400,
        },
        data: {
          label: nodeName,
          type: nodeType,
        },
      }
      
      const updatedNodes = [...activeWorkflow.nodes, newNode]
      updateActiveWorkflow(updatedNodes, activeWorkflow.edges)
      setNodeName('')
      markAsDirty(true)
      toast.success(`Added ${nodeType} node: ${nodeName}`)
    }
  }
  
  const saveWorkflow = () => {
    if (activeWorkflow) {
      // In real implementation, this would call API
      toast.success('Workflow saved successfully!')
      markAsDirty(false)
    }
  }
  
  const executeWorkflow = () => {
    if (activeWorkflow) {
      toast.loading('Executing workflow...')
      // In real implementation, this would call API
      setTimeout(() => {
        toast.dismiss()
        toast.success('Workflow executed successfully!')
      }, 2000)
    }
  }
  
  if (!activeWorkflow) {
    return (
      <div className="flex flex-col items-center justify-center h-full">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-secondary-300 mb-4">No Workflow Selected</h2>
          <p className="text-secondary-500 mb-6">Create a new workflow or select an existing one</p>
          <button className="btn btn-primary">
            <Plus className="w-4 h-4 mr-2" />
            Create New Workflow
          </button>
        </div>
      </div>
    )
  }
  
  return (
    <div className="flex flex-col h-full">
      {/* Toolbar */}
      <div className="glass border-b border-secondary-800 p-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">{activeWorkflow.name}</h1>
            <p className="text-secondary-500">{activeWorkflow.description}</p>
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={saveWorkflow}
              className="btn btn-secondary"
              disabled={!selectedNode}
            >
              <Save className="w-4 h-4 mr-2" />
              Save Workflow
            </button>
            <button
              onClick={executeWorkflow}
              className="btn btn-primary"
            >
              <Play className="w-4 h-4 mr-2" />
              Execute
            </button>
          </div>
        </div>
      </div>
      
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <div className="w-64 glass border-r border-secondary-800 p-4">
          <div className="mb-6">
            <h3 className="font-semibold mb-3">Add New Node</h3>
            <div className="space-y-3">
              <input
                type="text"
                value={nodeName}
                onChange={(e) => setNodeName(e.target.value)}
                placeholder="Node name"
                className="input input-bordered w-full"
              />
              <select
                value={nodeType}
                onChange={(e) => setNodeType(e.target.value as any)}
                className="select select-bordered w-full"
              >
                <option value="agent">AI Agent</option>
                <option value="condition">Condition</option>
                <option value="action">Action</option>
              </select>
              <button
                onClick={addNewNode}
                className="btn btn-primary w-full"
              >
                <Plus className="w-4 h-4 mr-2" />
                Add Node
              </button>
            </div>
          </div>
          
          <div className="mb-6">
            <h3 className="font-semibold mb-3">Nodes Palette</h3>
            <div className="space-y-2">
              <div className="p-3 bg-secondary-800 rounded-lg cursor-grab">
                <div className="font-medium">AI Agent</div>
                <div className="text-sm text-secondary-500">LLM-powered agent</div>
              </div>
              <div className="p-3 bg-secondary-800 rounded-lg cursor-grab">
                <div className="font-medium">Condition</div>
                <div className="text-sm text-secondary-500">Branching logic</div>
              </div>
              <div className="p-3 bg-secondary-800 rounded-lg cursor-grab">
                <div className="font-medium">Action</div>
                <div className="text-sm text-secondary-500">Execute task</div>
              </div>
            </div>
          </div>
          
          {selectedNode && (
            <div className="border-t border-secondary-800 pt-4">
              <h3 className="font-semibold mb-3">Node Properties</h3>
              <div className="space-y-3">
                <div>
                  <label className="label">Name</label>
                  <input
                    type="text"
                    value={selectedNode.data.label}
                    onChange={(e) => {
                      // Update node label
                    }}
                    className="input input-bordered w-full"
                  />
                </div>
                <div>
                  <label className="label">Type</label>
                  <div className="badge badge-primary">
                    {selectedNode.type}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
        
        {/* Main Editor */}
        <div className="flex-1 relative">
          <ReactFlow
            nodes={activeWorkflow.nodes}
            edges={activeWorkflow.edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={(_, node) => setSelectedNode(node)}
            nodeTypes={nodeTypes}
            fitView
          >
            <Background />
            <Controls />
            <MiniMap />
            <Panel position="top-right" className="space-x-2">
              <button className="btn btn-sm btn-secondary">
                <Download className="w-4 h-4" />
              </button>
              <button className="btn btn-sm btn-secondary">
                <Upload className="w-4 h-4" />
              </button>
            </Panel>
          </ReactFlow>
        </div>
      </div>
    </div>
  )
}

export default WorkflowEditor
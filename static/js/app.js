// OpenAgentFlow 前端JavaScript

// API基础URL
const API_BASE_URL = window.location.origin;

// 全局状态
let currentSection = 'dashboard';
let agents = [];
let workflows = [];
let executions = [];
let selectedNode = null;

// DOM加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    // 初始化导航
    initNavigation();
    
    // 加载仪表板数据
    loadDashboardData();
    
    // 初始化工作流设计器
    initWorkflowDesigner();
    
    // 设置表单提交
    setupForms();
    
    // 显示欢迎消息
    showMessage('欢迎使用 OpenAgentFlow！', 'info');
});

// 初始化导航
function initNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const sectionId = this.getAttribute('href').substring(1);
            showSection(sectionId);
        });
    });
}

// 显示指定部分
function showSection(sectionId) {
    // 更新导航
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${sectionId}`) {
            link.classList.add('active');
        }
    });
    
    // 隐藏所有部分
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    
    // 显示目标部分
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.classList.add('active');
        currentSection = sectionId;
        
        // 加载对应部分的数据
        switch(sectionId) {
            case 'dashboard':
                loadDashboardData();
                break;
            case 'agents':
                loadAgents();
                break;
            case 'workflows':
                loadWorkflows();
                break;
            case 'tools':
                loadTools();
                break;
        }
    }
}

// 加载仪表板数据
async function loadDashboardData() {
    try {
        // 加载Agent数量
        const agentsResponse = await fetch(`${API_BASE_URL}/api/v1/agents?limit=1`);
        if (agentsResponse.ok) {
            const agentsData = await agentsResponse.json();
            document.getElementById('agent-count').textContent = '...';
            // 实际应该获取总数，这里用列表长度模拟
        }
        
        // 加载工作流数量
        const workflowsResponse = await fetch(`${API_BASE_URL}/api/v1/workflows?limit=1`);
        if (workflowsResponse.ok) {
            const workflowsData = await workflowsResponse.json();
            document.getElementById('workflow-count').textContent = '...';
        }
        
        // 加载最近活动
        loadRecentActivity();
        
    } catch (error) {
        console.error('加载仪表板数据失败:', error);
        showMessage('加载数据失败，请检查网络连接', 'error');
    }
}

// 加载最近活动
async function loadRecentActivity() {
    const activityList = document.getElementById('activity-list');
    if (!activityList) return;
    
    activityList.innerHTML = `
        <div class="activity-item">
            <i class="fas fa-sync-alt loading"></i>
            <span>加载中...</span>
        </div>
    `;
    
    try {
        // 模拟活动数据
        setTimeout(() => {
            activityList.innerHTML = `
                <div class="activity-item">
                    <i class="fas fa-check-circle" style="color: #10b981;"></i>
                    <span>系统启动成功</span>
                    <span class="activity-time">刚刚</span>
                </div>
                <div class="activity-item">
                    <i class="fas fa-user-robot" style="color: #2563eb;"></i>
                    <span>创建了新的AI Agent</span>
                    <span class="activity-time">5分钟前</span>
                </div>
                <div class="activity-item">
                    <i class="fas fa-project-diagram" style="color: #8b5cf6;"></i>
                    <span>工作流执行完成</span>
                    <span class="activity-time">1小时前</span>
                </div>
                <div class="activity-item">
                    <i class="fas fa-tools" style="color: #f59e0b;"></i>
                    <span>飞书工具已连接</span>
                    <span class="activity-time">2小时前</span>
                </div>
            `;
        }, 1000);
    } catch (error) {
        activityList.innerHTML = `
            <div class="activity-item">
                <i class="fas fa-exclamation-triangle" style="color: #ef4444;"></i>
                <span>加载活动失败</span>
            </div>
        `;
    }
}

// 加载Agent列表
async function loadAgents() {
    const agentList = document.getElementById('agent-list');
    if (!agentList) return;
    
    agentList.innerHTML = `
        <div class="agent-card" style="text-align: center; padding: 40px;">
            <i class="fas fa-sync-alt loading" style="font-size: 2rem;"></i>
            <p>加载中...</p>
        </div>
    `;
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/agents`);
        if (response.ok) {
            agents = await response.json();
            renderAgents(agents);
        } else {
            throw new Error(`HTTP ${response.status}`);
        }
    } catch (error) {
        console.error('加载Agent失败:', error);
        agentList.innerHTML = `
            <div class="agent-card" style="text-align: center; padding: 40px; color: #ef4444;">
                <i class="fas fa-exclamation-triangle" style="font-size: 2rem;"></i>
                <p>加载失败: ${error.message}</p>
                <button class="btn btn-outline" onclick="loadAgents()">
                    <i class="fas fa-redo"></i> 重试
                </button>
            </div>
        `;
    }
}

// 渲染Agent列表
function renderAgents(agents) {
    const agentList = document.getElementById('agent-list');
    if (!agentList) return;
    
    if (agents.length === 0) {
        agentList.innerHTML = `
            <div class="agent-card" style="text-align: center; padding: 40px;">
                <i class="fas fa-user-robot" style="font-size: 3rem; color: #cbd5e1;"></i>
                <h3>暂无 Agent</h3>
                <p>创建您的第一个AI Agent开始工作</p>
                <button class="btn btn-primary" onclick="createNewAgent()">
                    <i class="fas fa-plus"></i> 创建 Agent
                </button>
            </div>
        `;
        return;
    }
    
    agentList.innerHTML = agents.map(agent => `
        <div class="agent-card">
            <div class="agent-header">
                <h3>${agent.name}</h3>
                <span class="agent-type ${agent.agent_type}">${getAgentTypeLabel(agent.agent_type)}</span>
            </div>
            ${agent.description ? `<p class="agent-description">${agent.description}</p>` : ''}
            <div class="agent-details">
                <p><small>创建时间: ${formatDate(agent.created_at)}</small></p>
                <p><small>状态: ${agent.is_active ? '<span style="color: #10b981;">活跃</span>' : '<span style="color: #ef4444;">禁用</span>'}</small></p>
            </div>
            <div class="agent-actions">
                <button class="btn btn-outline btn-sm" onclick="testAgent(${agent.id})">
                    <i class="fas fa-vial"></i> 测试
                </button>
                <button class="btn btn-outline btn-sm" onclick="editAgent(${agent.id})">
                    <i class="fas fa-edit"></i> 编辑
                </button>
                <button class="btn btn-outline btn-sm" onclick="deleteAgent(${agent.id})">
                    <i class="fas fa-trash"></i> 删除
                </button>
            </div>
        </div>
    `).join('');
}

// 获取Agent类型标签
function getAgentTypeLabel(type) {
    const labels = {
        'llm': 'LLM Agent',
        'tool': '工具 Agent',
        'condition': '条件 Agent'
    };
    return labels[type] || type;
}

// 创建新Agent
function createNewAgent() {
    const agentForm = document.getElementById('agent-form');
    const agentList = document.getElementById('agent-list');
    
    if (agentForm && agentList) {
        agentList.style.display = 'none';
        agentForm.style.display = 'block';
    }
}

// 取消创建Agent
function cancelAgentForm() {
    const agentForm = document.getElementById('agent-form');
    const agentList = document.getElementById('agent-list');
    
    if (agentForm && agentList) {
        agentForm.style.display = 'none';
        agentList.style.display = 'grid';
    }
}

// 设置表单提交
function setupForms() {
    const agentForm = document.getElementById('agent-create-form');
    if (agentForm) {
        agentForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = {
                name: document.getElementById('agent-name').value,
                description: document.getElementById('agent-description').value,
                agent_type: document.getElementById('agent-type').value,
                config: JSON.parse(document.getElementById('agent-config').value)
            };
            
            try {
                const response = await fetch(`${API_BASE_URL}/api/v1/agents`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });
                
                if (response.ok) {
                    showMessage('Agent 创建成功！', 'success');
                    cancelAgentForm();
                    loadAgents();
                    loadDashboardData();
                } else {
                    const error = await response.json();
                    throw new Error(error.detail || '创建失败');
                }
            } catch (error) {
                showMessage(`创建失败: ${error.message}`, 'error');
            }
        });
    }
}

// 加载工作流
async function loadWorkflows() {
    const workflowItems = document.getElementById('workflow-items');
    if (!workflowItems) return;
    
    workflowItems.innerHTML = `
        <div class="activity-item" style="text-align: center; padding: 20px;">
            <i class="fas fa-sync-alt loading"></i>
            <span>加载中...</span>
        </div>
    `;
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/workflows`);
        if (response.ok) {
            workflows = await response.json();
            renderWorkflows(workflows);
        } else {
            throw new Error(`HTTP ${response.status}`);
        }
    } catch (error) {
        console.error('加载工作流失败:', error);
        workflowItems.innerHTML = `
            <div class="activity-item" style="text-align: center; padding: 20px; color: #ef4444;">
                <i class="fas fa-exclamation-triangle"></i>
                <span>加载失败: ${error.message}</span>
            </div>
        `;
    }
}

// 渲染工作流列表
function renderWorkflows(workflows) {
    const workflowItems = document.getElementById('workflow-items');
    if (!workflowItems) return;
    
    if (workflows.length === 0) {
        workflowItems.innerHTML = `
            <div class="activity-item" style="text-align: center; padding: 40px;">
                <i class="fas fa-project-diagram" style="font-size: 2rem; color: #cbd5e1;"></i>
                <p>暂无工作流</p>
                <button class="btn btn-primary" onclick="createNewWorkflow()">
                    <i class="fas fa-plus"></i> 创建工作流
                </button>
            </div>
        `;
        return;
    }
    
    workflowItems.innerHTML = workflows.map(workflow => `
        <div class="activity-item" style="cursor: pointer;" onclick="loadWorkflow(${workflow.id})">
            <i class="fas fa-project-diagram" style="color: #8b5cf6;"></i>
            <div style="flex: 1;">
                <strong>${workflow.name}</strong>
                ${workflow.description ? `<p style="margin: 5px 0 0 0; font-size: 0.9em; color: #64748b;">${workflow.description}</p>` : ''}
                <div style="display: flex; gap: 10px; margin-top: 5px; font-size: 0.8em;">
                    <span>节点: ${workflow.nodes ? workflow.nodes.length : 0}</span>
                    <span>边: ${workflow.edges ? workflow.edges.length : 0}</span>
                    <span style="color: ${getStatusColor(workflow.status)}">● ${workflow.status}</span>
                </div>
            </div>
            <div class="workflow-actions" style="display: flex; gap: 5px;">
                <button class="btn btn-outline btn-sm" onclick="executeWorkflow(${workflow.id}, event)">
                    <i class="fas fa-play"></i>
                </button>
                <button class="btn btn-outline btn-sm" onclick="editWorkflow(${workflow.id}, event)">
                    <i class="fas fa-edit"></i>
                </button>
            </div>
        </div>
    `).join('');
}

// 获取状态颜色
function getStatusColor(status) {
    const colors = {
        'draft': '#64748b',
        'active': '#10b981',
        'paused': '#f59e0b',
        'archived': '#ef4444'
    };
    return colors[status] || '#64748b';
}

// 创建工作流
function createNewWorkflow() {
    showSection('workflows');
    // 清空画布
    const canvas = document.getElementById('workflow-canvas');
    if (canvas) {
        canvas.innerHTML = `
            <div class="canvas-placeholder">
                <i class="fas fa-mouse-pointer"></i>
                <p>从左侧拖拽节点到此处开始设计工作流</p>
            </div>
        `;
    }
}

// 初始化工作流设计器
function initWorkflowDesigner() {
    // 节点拖拽
    const nodeItems = document.querySelectorAll('.node-item');
    const canvas = document.getElementById('workflow-canvas');
    
    nodeItems.forEach(item => {
        item.addEventListener('dragstart', function(e) {
            e.dataTransfer.setData('text/plain', this.getAttribute('data-type'));
        });
    });
    
    if (canvas) {
        canvas.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.style.backgroundColor = '#e2e8f0';
        });
        
        canvas.addEventListener('dragleave', function(e) {
            this.style.backgroundColor = '';
        });
        
        canvas.addEventListener('drop', function(e) {
            e.preventDefault();
            this.style.backgroundColor = '';
            
            const nodeType = e.dataTransfer.getData('text/plain');
            if (!nodeType) return;
            
            // 移除占位符
            const placeholder = this.querySelector('.canvas-placeholder');
            if (placeholder) {
                placeholder.remove();
            }
            
            // 创建新节点
            const node = createWorkflowNode(nodeType, e.offsetX, e.offsetY);
            this.appendChild(node);
        });
    }
}

// 创建工作流节点
function createWorkflowNode(type, x, y) {
    const nodeTypes = {
        'start': { icon: 'fa-play-circle', color: '#10b981', label: '开始' },
        'llm': { icon: 'fa-brain', color: '#2563eb', label: 'AI Agent' },
        'tool': { icon: 'fa-tools', color: '#f59e0b', label: '工具' },
        'condition': { icon: 'fa-code-branch', color: '#8b5cf6', label: '条件' },
        'end': { icon: 'fa-stop-circle', color: '#ef4444', label: '结束' }
    };
    
    const nodeInfo = nodeTypes[type] || { icon: 'fa-circle', color: '#64748b', label: '节点' };
    
    const nodeId = `node_${Date.now()}`;
    const node = document.createElement('div');
    node.className = 'workflow-node';
    node.id = nodeId;
    node.style.position = 'absolute';
    node.style.left = `${x - 50}px`;
    node.style.top = `${y - 50}px`;
    node.style.width = '100px';
    node.style.height = '100px';
    node.style.backgroundColor = 'white';
    node.style.borderRadius = '8px';
    node.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
    node.style.border = `2px solid ${nodeInfo.color}`;
    node.style.display = 'flex';
    node.style.flexDirection = 'column';
    node.style.alignItems = 'center';
    node.style.justifyContent = 'center';
    node.style.cursor = 'move';
    node.style.zIndex = '1000';
    node.draggable = true;
    
    node.innerHTML = `
        <div style="color: ${nodeInfo.color}; font-size: 1.5rem;">
            <i class="fas ${nodeInfo.icon}"></i>
        </div>
        <div style="margin-top: 5px; font-size: 0.8rem; font-weight: 500;">
            ${nodeInfo.label}
        </div>
    `;
    
    // 添加拖拽功能
    makeDraggable(node);
    
    // 点击选择节点
    node.addEventListener('click', function(e) {
        e.stopPropagation();
        selectNode(node);
    });
    
    return node;
}

// 使元素可拖拽
function makeDraggable(element) {
    let isDragging = false;
    let offsetX, offsetY;
    
    element.addEventListener('mousedown', function(e) {
        isDragging = true;
        const rect = element.getBoundingClientRect();
        offsetX = e.clientX - rect.left;
        offsetY = e.clientY - rect.top;
        element.style.zIndex = '1001';
    });
    
    document.addEventListener('mousemove', function(e) {
        if (!isDragging) return;
        
        const canvas = document.getElementById('workflow-canvas');
        if (!canvas) return;
        
        const canvasRect = canvas.getBoundingClientRect();
        const x = e.clientX - canvasRect.left - offsetX;
        const y = e.clientY - canvasRect.top - offsetY;
        
        // 限制在画布内
        const maxX = canvasRect.width - element.offsetWidth;
        const maxY = canvasRect.height - element.offsetHeight;
        
        element.style.left = `${Math.max(0, Math.min(x, maxX))}px`;
        element.style.top = `${Math.max(0, Math.min(y, maxY))}px`;
    });
    
    document.addEventListener('mouseup', function() {
        isDragging = false;
        element.style.zIndex = '1000';
    });
}

// 选择节点
function selectNode(node) {
    // 移除之前选择的节点样式
    document.querySelectorAll('.workflow-node').forEach(n => {
        n.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
    });
    
    // 添加选中样式
    node.style.boxShadow = '0 0 0 3px rgba(37, 99, 235, 0.3)';
    selectedNode = node;
    
    // 更新属性面板
    updateNodeProperties(node);
}

// 更新节点属性
function updateNodeProperties(node) {
    const propertiesPanel = document.getElementById('node-properties');
    if (!propertiesPanel) return;
    
    const nodeId = node.id;
    const nodeType = node.getAttribute('data-type') || 'unknown';
    
    propertiesPanel.innerHTML = `
        <div class="form-group">
            <label>节点ID</label>
            <input type="text" value="${nodeId}" readonly>
        </div>
        <div class="form-group">
            <label>节点类型</label>
            <input type="text" value="${nodeType}" readonly>
        </div>
        <div class="form-group">
            <label>位置</label>
            <div style="display: flex; gap: 10px;">
                <input type="number" value="${parseInt(node.style.left)}" placeholder="X" style="flex: 1;">
                <input type="number" value="${parseInt(node.style.top)}" placeholder="Y" style="flex: 1;">
            </div>
        </div>
        <div class="form-actions">
            <button class="btn btn-secondary btn-sm" onclick="deleteSelectedNode()">
                <i class="fas fa-trash"></i> 删除节点
            </button>
        </div>
    `;
}

// 删除选中的节点
function deleteSelectedNode() {
    if (selectedNode) {
        selectedNode.remove();
        selectedNode = null;
        
        const propertiesPanel = document.getElementById('node-properties');
        if (propertiesPanel) {
            propertiesPanel.innerHTML = '<p class="placeholder">选择一个节点进行配置</p>';
        }
        
        // 如果画布为空，显示占位符
        const canvas = document.getElementById('workflow-canvas');
        if (canvas && canvas.children.length === 0) {
            canvas.innerHTML = `
                <div class="canvas-placeholder">
                    <i class="fas fa-mouse-pointer"></i>
                    <p>从左侧拖拽节点到此处开始设计工作流</p>
                </div>
            `;
        }
    }
}

// 保存工作流
async function saveWorkflow() {
    const canvas = document.getElementById('workflow-canvas');
    if (!canvas) return;
    
    const nodes = [];
    const edges = [];
    
    // 收集节点
    document.querySelectorAll('.workflow-node').forEach(node => {
        const rect = node.getBoundingClientRect();
        const canvasRect = canvas.getBoundingClientRect();
        
        nodes.push({
            id: node.id,
            type: node.getAttribute('data-type') || 'custom',
            position: {
                x: parseInt(node.style.left),
                y: parseInt(node.style.top)
            },
            data: {
                label: node.querySelector('div:nth-child(2)')?.textContent || '节点'
            }
        });
    });
    
    if (nodes.length === 0) {
        showMessage('请先添加节点到工作流', 'warning');
        return;
    }
    
    const workflowName = prompt('请输入工作流名称:', `工作流_${new Date().toLocaleDateString()}`);
    if (!workflowName) return;
    
    const workflowData = {
        name: workflowName,
        description: prompt('请输入工作流描述:', ''),
        nodes: nodes,
        edges: edges, // 这里需要实现边的创建逻辑
        status: 'draft'
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/workflows`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(workflowData)
        });
        
        if (response.ok) {
            showMessage('工作流保存成功！', 'success');
            loadWorkflows();
        } else {
            const error = await response.json();
            throw new Error(error.detail || '保存失败');
        }
    } catch (error) {
        showMessage(`保存失败: ${error.message}`, 'error');
    }
}

// 加载示例工作流
function loadSampleWorkflow() {
    const canvas = document.getElementById('workflow-canvas');
    if (!canvas) return;
    
    // 清空画布
    canvas.innerHTML = '';
    
    // 创建示例节点
    const nodes = [
        { type: 'start', x: 100, y: 200 },
        { type: 'llm', x: 300, y: 200 },
        { type: 'tool', x: 500, y: 200 },
        { type: 'end', x: 700, y: 200 }
    ];
    
    nodes.forEach(nodeInfo => {
        const node = createWorkflowNode(nodeInfo.type, nodeInfo.x, nodeInfo.y);
        canvas.appendChild(node);
    });
    
    showMessage('示例工作流已加载', 'success');
}

// 测试API连接
async function testAPI() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            const data = await response.json();
            showMessage(`API连接正常: ${data.status}`, 'success');
        } else {
            throw new Error(`HTTP ${response.status}`);
        }
    } catch (error) {
        showMessage(`API连接失败: ${error.message}`, 'error');
    }
}

// 显示消息
function showMessage(text, type = 'info') {
    // 移除现有消息
    const existingMessage = document.querySelector('.message');
    if (existingMessage) {
        existingMessage.remove();
    }
    
    // 创建新消息
    const message = document.createElement('div');
    message.className = `message ${type}`;
    message.innerHTML = `
        <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i>
        <span>${text}</span>
    `;
    
    document.body.appendChild(message);
    
    // 3秒后自动移除
    setTimeout(() => {
        if (message.parentNode) {
            message.remove();
        }
    }, 3000);
}

// 工具函数
function formatDate(dateString) {
    if (!dateString) return '未知';
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// 打开文档
function openDocs() {
    showSection('docs');
}

// 打开API文档
function openAPIDocs() {
    window.open(`${API_BASE_URL}/docs`, '_blank');
}

// 快速开始
function openQuickStart() {
    showMessage('快速开始文档开发中...', 'info');
}

// 视频教程
function openVideoTutorials() {
    showMessage('视频教程开发中...', 'info');
}

// 常见问题
function openFAQ() {
    showMessage('常见问题开发中...', 'info');
}

// 配置工具
function configureFeishu() {
    showMessage('飞书配置功能开发中...', 'info');
}

function configureDingtalk() {
    showMessage('钉钉配置功能开发中...', 'info');
}

function configureWecom() {
    showMessage('企业微信配置功能开发中...', 'info');
}

function createCustomTool() {
    showMessage('自定义工具功能开发中...', 'info');
}

// 导出全局函数
window.showSection = showSection;
window.createNewAgent = createNewAgent;
window.cancelAgentForm = cancelAgentForm;
window.createNewWorkflow = createNewWorkflow;
window.loadSampleWorkflow = loadSampleWorkflow;
window.saveWorkflow = saveWorkflow;
window.testAPI = testAPI;
window.openDocs = openDocs;
window.openAPIDocs = openAPIDocs;
window.configureFeishu = configureFeishu;
window.configureDingtalk = configureDingtalk;
window.configureWecom = configureWecom;
window.createCustomTool = createCustomTool;
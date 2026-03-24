import asyncio
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class TaskPriority(Enum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    CRITICAL = 3

@dataclass
class Task:
    id: str
    priority: TaskPriority
    compute_units: float
    data: dict
    assigned_node: Optional[str] = None
    status: str = 'pending'

class SwarmCoordinator:
    def __init__(self):
        self.nodes: Dict[str, dict] = {}
        self.tasks: Dict[str, Task] = {}
        self.load_threshold = 0.8

    async def register_node(self, node_id: str, capabilities: dict):
        self.nodes[node_id] = {
            'capabilities': capabilities,
            'current_load': 0.0,
            'tasks': []
        }

    async def remove_node(self, node_id: str):
        if node_id in self.nodes:
            # Reassign tasks from failing node
            tasks_to_reassign = self.nodes[node_id]['tasks']
            del self.nodes[node_id]
            for task_id in tasks_to_reassign:
                await self.reassign_task(task_id)

    async def submit_task(self, task: Task) -> str:
        self.tasks[task.id] = task
        await self.assign_task(task)
        return task.id

    async def assign_task(self, task: Task):
        best_node = await self._find_optimal_node(task)
        if best_node:
            task.assigned_node = best_node
            self.nodes[best_node]['tasks'].append(task.id)
            self.nodes[best_node]['current_load'] += task.compute_units

    async def _find_optimal_node(self, task: Task) -> Optional[str]:
        available_nodes = []
        for node_id, node in self.nodes.items():
            if node['current_load'] + task.compute_units <= self.load_threshold:
                available_nodes.append((node_id, node))

        if not available_nodes:
            return None

        # Sort by current load and capabilities match
        sorted_nodes = sorted(available_nodes, 
                             key=lambda x: (x[1]['current_load'], 
                                          -self._calculate_capability_score(x[1], task)))
        return sorted_nodes[0][0] if sorted_nodes else None

    def _calculate_capability_score(self, node: dict, task: Task) -> float:
        # Calculate how well node capabilities match task requirements
        # This is a simplified scoring - enhance based on specific requirements
        base_score = 1.0
        if task.priority == TaskPriority.CRITICAL:
            if node['capabilities'].get('high_reliability', False):
                base_score *= 1.5
        return base_score

    async def reassign_task(self, task_id: str):
        task = self.tasks[task_id]
        task.status = 'reassigning'
        await self.assign_task(task)

    async def monitor_load(self):
        while True:
            await self._balance_load()
            await asyncio.sleep(30)  # Check every 30 seconds

    async def _balance_load(self):
        overloaded = [node_id for node_id, node in self.nodes.items() 
                      if node['current_load'] > self.load_threshold]

        for node_id in overloaded:
            tasks = sorted(self.nodes[node_id]['tasks'],
                         key=lambda t: self.tasks[t].priority.value)
            for task_id in tasks:
                await self.reassign_task(task_id)
                if self.nodes[node_id]['current_load'] <= self.load_threshold:
                    break

    async def get_system_status(self) -> dict:
        return {
            'total_nodes': len(self.nodes),
            'total_tasks': len(self.tasks),
            'load_distribution': {
                node_id: node['current_load']
                for node_id, node in self.nodes.items()
            },
            'task_priorities': {
                priority: len([t for t in self.tasks.values() 
                             if t.priority == priority])
                for priority in TaskPriority
            }
        }
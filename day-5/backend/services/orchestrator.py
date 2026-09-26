"""Multi-Agent Orchestration System."""

from typing import Optional, Dict, List
from enum import Enum
from dataclasses import dataclass
from datetime import datetime


class AgentRole(str, Enum):
    """Agent roles in the orchestration."""
    FRONTEND = "frontend"
    BACKEND = "backend"
    RAG = "rag"
    TRIAGE = "triage"


class TaskPriority(str, Enum):
    """Task priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Task:
    """Orchestration task."""
    id: str
    description: str
    assigned_agent: AgentRole
    priority: TaskPriority
    dependencies: List[str]
    created_at: datetime
    status: str = "pending"
    result: Optional[str] = None


class Orchestrator:
    """Multi-agent orchestration and coordination."""

    def __init__(self):
        """Initialize orchestrator."""
        self.tasks: Dict[str, Task] = {}
        self.agent_status: Dict[AgentRole, str] = {
            role: "idle" for role in AgentRole
        }
        self.execution_history: List[Dict] = []

    def create_task(
        self,
        description: str,
        agent: AgentRole,
        priority: TaskPriority = TaskPriority.MEDIUM,
        dependencies: Optional[List[str]] = None
    ) -> str:
        """Create and register a new task."""
        task_id = f"task_{len(self.tasks) + 1}"

        task = Task(
            id=task_id,
            description=description,
            assigned_agent=agent,
            priority=priority,
            dependencies=dependencies or [],
            created_at=datetime.now()
        )

        self.tasks[task_id] = task
        return task_id

    def execute_task(self, task_id: str) -> Dict:
        """Execute a single task."""
        if task_id not in self.tasks:
            return {"error": "Task not found"}

        task = self.tasks[task_id]

        # Check dependencies
        if not self._check_dependencies(task):
            return {"error": "Dependencies not met"}

        # Mark agent as busy
        self.agent_status[task.assigned_agent] = "busy"
        task.status = "running"

        try:
            # Execute based on agent type
            result = self._dispatch_to_agent(task)
            task.status = "completed"
            task.result = result
            return {"status": "success", "result": result}
        except Exception as e:
            task.status = "failed"
            return {"error": str(e)}
        finally:
            # Mark agent as idle
            self.agent_status[task.assigned_agent] = "idle"

    def execute_workflow(self, task_ids: List[str]) -> Dict:
        """Execute multiple tasks as a workflow."""
        results = {}
        failed_tasks = []

        for task_id in task_ids:
            result = self.execute_task(task_id)
            results[task_id] = result

            if "error" in result:
                failed_tasks.append(task_id)

        return {
            "workflow_status": "failed" if failed_tasks else "success",
            "total_tasks": len(task_ids),
            "completed_tasks": len(task_ids) - len(failed_tasks),
            "failed_tasks": failed_tasks,
            "results": results
        }

    def _check_dependencies(self, task: Task) -> bool:
        """Check if all task dependencies are satisfied."""
        for dep_id in task.dependencies:
            if dep_id not in self.tasks:
                return False
            if self.tasks[dep_id].status != "completed":
                return False
        return True

    def _dispatch_to_agent(self, task: Task) -> str:
        """Dispatch task to appropriate agent."""
        if task.assigned_agent == AgentRole.FRONTEND:
            return self._execute_frontend_task(task)
        elif task.assigned_agent == AgentRole.BACKEND:
            return self._execute_backend_task(task)
        elif task.assigned_agent == AgentRole.RAG:
            return self._execute_rag_task(task)
        elif task.assigned_agent == AgentRole.TRIAGE:
            return self._execute_triage_task(task)
        else:
            raise ValueError(f"Unknown agent role: {task.assigned_agent}")

    def _execute_frontend_task(self, task: Task) -> str:
        """Execute frontend agent task."""
        # Frontend tasks: component creation, UI optimization
        return f"Frontend: {task.description} - Completed"

    def _execute_backend_task(self, task: Task) -> str:
        """Execute backend agent task."""
        # Backend tasks: API development, Claude integration
        return f"Backend: {task.description} - Completed"

    def _execute_rag_task(self, task: Task) -> str:
        """Execute RAG agent task."""
        # RAG tasks: knowledge retrieval, document processing
        return f"RAG: {task.description} - Completed"

    def _execute_triage_task(self, task: Task) -> str:
        """Execute P3-Triage agent task."""
        # Triage tasks: code review, quality assessment
        return f"Triage: {task.description} - Completed"

    def get_agent_status(self) -> Dict:
        """Get current status of all agents."""
        return {
            "agents": self.agent_status,
            "timestamp": datetime.now().isoformat()
        }

    def get_task_status(self, task_id: str) -> Dict:
        """Get status of a specific task."""
        if task_id not in self.tasks:
            return {"error": "Task not found"}

        task = self.tasks[task_id]
        return {
            "id": task.id,
            "description": task.description,
            "agent": task.assigned_agent.value,
            "priority": task.priority.value,
            "status": task.status,
            "result": task.result,
            "created_at": task.created_at.isoformat()
        }

    def get_statistics(self) -> Dict:
        """Get orchestration statistics."""
        total_tasks = len(self.tasks)
        completed = sum(1 for t in self.tasks.values() if t.status == "completed")
        failed = sum(1 for t in self.tasks.values() if t.status == "failed")
        pending = sum(1 for t in self.tasks.values() if t.status == "pending")

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed,
            "failed_tasks": failed,
            "pending_tasks": pending,
            "agent_status": self.agent_status,
            "success_rate": (completed / total_tasks * 100) if total_tasks > 0 else 0
        }


class TaskScheduler:
    """Schedule and prioritize tasks."""

    def __init__(self, orchestrator: Orchestrator):
        """Initialize task scheduler."""
        self.orchestrator = orchestrator
        self.queue: List[str] = []

    def enqueue_task(self, task_id: str) -> None:
        """Add task to queue."""
        self.queue.append(task_id)
        self._reorder_by_priority()

    def _reorder_by_priority(self) -> None:
        """Reorder queue by task priority."""
        priority_order = {
            TaskPriority.CRITICAL: 0,
            TaskPriority.HIGH: 1,
            TaskPriority.MEDIUM: 2,
            TaskPriority.LOW: 3
        }

        self.queue.sort(
            key=lambda tid: priority_order.get(
                self.orchestrator.tasks[tid].priority,
                999
            )
        )

    def execute_queue(self) -> Dict:
        """Execute all tasks in queue."""
        results = {}
        while self.queue:
            task_id = self.queue.pop(0)
            result = self.orchestrator.execute_task(task_id)
            results[task_id] = result
        return results

    def get_queue_status(self) -> List[Dict]:
        """Get current queue status."""
        status = []
        for task_id in self.queue:
            task = self.orchestrator.tasks[task_id]
            status.append({
                "task_id": task_id,
                "description": task.description,
                "priority": task.priority.value
            })
        return status

import asyncio
import random
import uuid

class SwarmerNode:
    def __init__(self, node_id, connection_pool):
        self.node_id = node_id
        self.connection_pool = connection_pool
        self.tasks = []

    async def coordinate_swarm(self):
        while True:
            await self.process_tasks()
            await asyncio.sleep(random.uniform(1, 5))

    async def process_tasks(self):
        for task in self.tasks:
            await self.execute_task(task)
        self.tasks = []

    async def execute_task(self, task):
        print(f'Swarmer node {self.node_id} executing task: {task}')
        # Implement task execution logic here
        await asyncio.sleep(random.uniform(1, 3))

    def add_task(self, task):
        self.tasks.append(task)

class SwarmCoordinator:
    def __init__(self, node_count=3):
        self.node_count = node_count
        self.connection_pool = []
        self.swarmers = []
        self.setup_swarm()

    def setup_swarm(self):
        for _ in range(self.node_count):
            node_id = str(uuid.uuid4())
            swarm_node = SwarmerNode(node_id, self.connection_pool)
            self.swarmers.append(swarm_node)
            asyncio.create_task(swarm_node.coordinate_swarm())

    async def coordinate_tasks(self, tasks):
        for task in tasks:
            await self.assign_task(task)

    async def assign_task(self, task):
        selected_node = random.choice(self.swarmers)
        selected_node.add_task(task)

# Example usage
coordinator = SwarmCoordinator()
tasks = ['Curate visual diary', 'Organize media assets', 'Generate weekly summary']
asyncio.create_task(coordinator.coordinate_tasks(tasks))

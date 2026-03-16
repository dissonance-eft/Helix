from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
import numpy as np

class HelixAgent(Agent):
    """An agent with fixed initial unique_id."""
    def __init__(self, unique_id, model, params=None):
        super().__init__(unique_id, model)
        self.params = params or {}
        self.state = {}

    def step(self):
        # To be implemented by specific experiments
        pass

class MesaAdapter(Model):
    """
    A thin wrapper for Mesa simulation within Helix.
    """
    def __init__(self, n_agents, width=10, height=10, agent_class=HelixAgent, **agent_params):
        super().__init__()
        self.num_agents = n_agents
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        
        # Create agents
        for i in range(self.num_agents):
            a = agent_class(i, self, agent_params)
            self.schedule.add(a)
            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

    def step(self):
        self.schedule.step()

    def run_simulation(self, steps):
        for _ in range(steps):
            self.step()
        return self.get_agent_states()

    def get_agent_states(self):
        states = []
        for agent in self.schedule.agents:
            states.append({
                "id": agent.unique_id,
                "pos": agent.pos,
                "state": agent.state
            })
        return states

"""
Async workflow runner for LangGraph with WebSocket broadcasting support.
"""

import asyncio
import importlib
from typing import Dict, Any, List
from config.config_loader import ConfigLoader
from agent_state import AgentState
from websocketServer import manager


class AsyncWorkflowRunner:
    """Custom async workflow runner that executes nodes sequentially with WebSocket broadcasts."""
    
    def __init__(self):
        """Initialize the async workflow runner."""
        self.config_loader = ConfigLoader()
        self.graph_config = self.config_loader.get("AGENT_WORKFLOW_GRAPH")
        
    def resolve_tool(self, tool_path: str):
        """
        Dynamically import a tool function based on its import path.
        
        Args:
            tool_path (str): The full import path of the tool (e.g., "agent_tools.get_data_from_csv_tool").
            
        Returns:
            function: The imported tool function.
        """
        module_name, function_name = tool_path.rsplit(".", 1)
        module = importlib.import_module(module_name)
        return getattr(module, function_name)
    
    def build_execution_order(self) -> List[str]:
        """
        Build the execution order of nodes based on the graph edges.
        
        Returns:
            List[str]: Ordered list of node IDs to execute.
        """
        # Create a simple linear execution order based on the edges
        # Starting from entry_point and following the edges
        execution_order = []
        current_node = self.graph_config["entry_point"]
        
        # Build a mapping of node -> next_node
        edge_map = {}
        for edge in self.graph_config["edges"]:
            if edge["to"] != "END":
                edge_map[edge["from"]] = edge["to"]
        
        # Follow the chain
        while current_node and current_node in edge_map:
            execution_order.append(current_node)
            current_node = edge_map.get(current_node)
        
        # Add the last node if it exists
        if current_node and current_node != "END":
            execution_order.append(current_node)
            
        return execution_order

    async def ainvoke(self, initial_state: Dict[str, Any], config: Dict[str, Any] = None, thread_id: str = None, **kwargs) -> Dict[str, Any]:
        """
        Asynchronously execute the workflow with WebSocket broadcasting.
        
        Args:
            initial_state (Dict[str, Any]): Initial state for the workflow.
            config (Dict[str, Any], optional): Configuration for the workflow.
            thread_id (str, optional): Thread ID for WebSocket messaging.
            **kwargs: Additional keyword arguments (like query_reported) that will be ignored.
            
        Returns:
            Dict[str, Any]: Final state after workflow execution.
        """
        state = initial_state.copy()
        execution_order = self.build_execution_order()
        total_steps = len(execution_order)
        
        # Broadcast workflow start
        await manager.send_to_thread(f"Starting workflow with {total_steps} steps...", thread_id=thread_id)

        # Create node tools mapping
        node_tools = {}
        for node in self.graph_config["nodes"]:
            tool_function = self.resolve_tool(node["tool"])
            node_tools[node["id"]] = tool_function
        
        # Execute nodes in order
        for i, node_id in enumerate(execution_order, 1):
            try:
                # Broadcast step start
                
                if node_id in node_tools:
                    tool_function = node_tools[node_id]
                    # Execute the tool function
                    result = await tool_function(state)
                    
                    # Update state with result
                    if isinstance(result, dict):
                        state.update(result)
                    
                    # Broadcast step completion
                else:
                    await manager.send_to_thread(f"Node {node_id} not found in tools", thread_id=thread_id)

            except Exception as e:
                await manager.send_to_thread(f"Error in step {i}/{total_steps} ({node_id}): {str(e)}", thread_id=thread_id)
                raise e
        
        # Broadcast workflow completion
        await manager.send_to_thread(f"All {total_steps} steps completed successfully!", thread_id=thread_id)
        return state


async def create_async_workflow():
    """
    Create an async workflow runner instance.
    
    Returns:
        AsyncWorkflowRunner: Configured async workflow runner.
    """
    return AsyncWorkflowRunner()

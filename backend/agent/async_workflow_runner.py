"""
Async workflow runner for LangGraph with WebSocket broadcasting support.
"""

import asyncio
import importlib
from typing import Dict, Any, List
from config.config_loader import ConfigLoader
from agent_state import AgentState
from websocketServer import manager

from langgraph.graph import StateGraph, END

import logging
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AsyncWorkflowRunner:
    """LangGraph-based async workflow runner with WebSocket broadcasting support."""
    
    def __init__(self, checkpointer=None):
        """Initialize the async workflow runner with LangGraph."""
        self.config_loader = ConfigLoader()
        self.graph_config = self.config_loader.get("AGENT_WORKFLOW_GRAPH")
        self.checkpointer = checkpointer
        self.langgraph_checkpointer = None
        
        # Initialize LangGraph checkpointer if provided
        if checkpointer:
            self.langgraph_checkpointer = self.checkpointer
            if self.langgraph_checkpointer:
                logger.info("LangGraph MongoDB checkpointer initialized successfully")
            else:
                logger.warning("Failed to initialize LangGraph MongoDB checkpointer")
        
        # Build the LangGraph workflow
        self.workflow_graph = self._build_langgraph_workflow(checkpointer=checkpointer)
        
    def resolve_tool(self, tool_path):
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
        
    def _build_langgraph_workflow(self, checkpointer=None):
        """
        Create the LangGraph StateGraph for the agent workflow based on the JSON config file.

        Args:
            checkpointer (AgentCheckpointer, optional): AgentCheckpointer instance. Default is None.

        Returns:
            StateGraph: LangGraph StateGraph for the agent workflow
        """
        # Load configuration
        config_loader = ConfigLoader()
        graph_config = config_loader.get("AGENT_WORKFLOW_GRAPH")

        graph = StateGraph(AgentState)

        # Add nodes
        for node in graph_config["nodes"]:
            logger.info(f"Adding node: {node['id']} with tool: {node['tool']}")
            tool_function = self.resolve_tool(node["tool"])
            graph.add_node(node["id"], tool_function)

        # Add edges
        for edge in graph_config["edges"]:
            from_node = edge["from"]
            to_node = edge["to"]
            if to_node == "END":
                graph.add_edge(from_node, END)
            else:
                graph.add_edge(from_node, to_node)

        # Set entry point
        graph.set_entry_point(graph_config["entry_point"])

        # Compile the graph
        if checkpointer:
            print("===ASYNC WORKFLOW RUNNER===\nCompiling graph WITH checkpointer")
            logger.info(f"Checkpointer type: {type(checkpointer)}")
            logger.info(f"Checkpointer methods: {[method for method in dir(checkpointer) if not method.startswith('_')]}")

            compiled_graph = graph.compile(checkpointer=checkpointer)

            # Verify the checkpointer was actually attached
            logger.info(f"Compiled graph type: {type(compiled_graph)}")
            logger.info(f"Compiled graph has checkpointer: {hasattr(compiled_graph, 'checkpointer')}")
            if hasattr(compiled_graph, 'checkpointer'):
                logger.info(f"Compiled graph checkpointer: {compiled_graph.checkpointer}")
                logger.info(f"Checkpointer is same object: {compiled_graph.checkpointer is checkpointer}")
            return compiled_graph
        else:
            print("===ASYNC WORKFLOW RUNNER===\nCompiling graph WITHOUT checkpointer")
            return graph.compile()

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
        # Use LangGraph's built-in execution with automatic checkpointing

        has_checkpointer = hasattr(self.workflow_graph, 'checkpointer') and self.workflow_graph.checkpointer is not None
        logger.info(f"Workflow has checkpointer: {has_checkpointer}")
        logger.info(f"Config provided: {config is not None}")

        if has_checkpointer and config:
            logger.info(f"Invoking LangGraph workflow with checkpointer for thread_id: {thread_id}")

            try: 
                # Directly invoke the workflow and get the final state
                logger.info("Invoking workflow with checkpointer...")
                final_state = await self.workflow_graph.ainvoke(initial_state, config=config)
                logger.info(f"Workflow completed successfully with final state: {final_state}")
                await manager.send_to_thread(f"Workflow completed.", thread_id=thread_id)
                return final_state
            except Exception as e:
                # Log the specific error to help debug
                logger.error(f"LangGraph workflow error: {type(e).__name__}: {str(e)}")
        
        # Fallback to manual execution if no checkpointer
        logger.info("Invoking workflow without checkpointer (manual execution).")
        state = initial_state.copy()
        edge_map = {}
        for edge in self.graph_config["edges"]:
            edge_map.setdefault(edge["from"], []).append(edge["to"])
        node_tools = {node["id"]: self.resolve_tool(node["tool"]) for node in self.graph_config["nodes"]}
        current_node = self.graph_config["entry_point"]
        steps = 0

        while current_node and current_node != "END":
            steps += 1
            if current_node not in node_tools:
                await manager.send_to_thread(f"Node {current_node} not found in tools", thread_id=thread_id)
                break
            tool_function = node_tools[current_node]
            result = await tool_function(state)
            if isinstance(result, dict):
                state.update(result)
            
            # Check for dynamic jump
            next_step = state.get("next_step")
            if next_step and next_step != current_node:
                current_node = next_step
                state["next_step"] = None  # Optionally clear after use
            else:
                # Default: follow the first outgoing edge
                next_nodes = edge_map.get(current_node, [])
                current_node = next_nodes[0] if next_nodes else "END"
        
        await manager.send_to_thread(f"Workflow completed after {steps} steps.", thread_id=thread_id)
        return state



async def create_async_workflow(checkpointer=None) -> AsyncWorkflowRunner:
    """
    Create an async workflow runner instance.
    
    Returns:
        AsyncWorkflowRunner: Configured async workflow runner.
    """
    return AsyncWorkflowRunner(checkpointer=checkpointer)

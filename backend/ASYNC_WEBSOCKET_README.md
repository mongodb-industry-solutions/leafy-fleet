# Async Agent Workflow with WebSocket Broadcasting

This project has been updated to support real-time WebSocket broadcasting during agent workflow execution. Now you can monitor the progress of each agent tool execution in real-time through WebSocket connections.

## How It Works

### 1. **Workflow Execution Flow**

The `/run-agent` endpoint now works as follows:

1. **HTTP Request**: Client calls `/run-agent?query_reported=your_query`
2. **Workflow Creation**: Creates an `AsyncWorkflowRunner` instance
3. **Sequential Execution**: Executes each tool in the LangGraph sequentially:
   - `reasoning_node` (generate_chain_of_thought_tool)
   - `data_from_csv` (get_data_from_csv_tool)  
   - `process_data` (process_data_tool)
   - `embedding_node` (get_query_embedding_tool)
   - `vector_search` (vector_search_tool)
   - `process_vector_search` (process_vector_search_tool)
   - `persistence_node` (persist_data_tool)
   - `recommendation_node` (get_llm_recommendation_tool)

4. **Real-time Updates**: Each step broadcasts progress via WebSocket
5. **Final Response**: Returns the complete agent state


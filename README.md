# Agentic Framework

This repository hosts `leafy-fleet`, designed as an assistant RAG Agent capable of understanding a user's query, searching trough timeseries data and generating an aswer with an insight that satisfies the original question

## Goal

The primary goal of Leafy Fleet is to showcase the capabilities of MongoDB being used as a memory provider for LangGraph, enabling the creation of intelligent agents that can process and analyze timeseries data, generate embeddings, perform vector searches, and provide actionable recommendations.

The current workflow is intentionally simple, showcasing the core capabilities of the demo. This simplicity allows users to quickly understand its structure and functionality while encouraging customization. This demo is to be taken as a starting point for building intelligent agents tailored to specific use cases.

## High Level Logical Architecture

![High Level Logical Architecture](architecture/logical.png)

## Features

- **Multi-Step Diagnostic Workflow:**  
  The agent processes a query by:
  1. **Understanding the Query:** The agent adds an embedding to the query using the VoyageAI model Voyage-3.5 to search similar questions via embedding Vectors.
  2. **Tool Selecting:** Selects from a set of predefined tools based on the query context.
  3. **Atlas Vector Search:** Searches for similar queries in MongoDB Atlas using the generated embedding.
  4. **Data Persistence:** Saves timeseries data, session logs, and recommendations in MongoDB Atlas.
  5. **Final Recommendation:** Uses Anthropic Claude 3 Haiku model to generate a final recommendation.
  
- **Agent Profile Management:**  
  Automatically retrieves (or creates if missing) a default agent profile from MongoDB that contains instructions, rules, and goals.

- **Session & Run Document Tracking:**  
  Each diagnostic run is assigned a unique thread ID and logged. Specific run documents from various collections (eg. agent_profiles, historical_recommendations, logs, queries, checkpoints, timeseries_data, etc) can be retrieved for detailed analysis.

- **User-Friendly Frontend:**  
  A dashboard displays the agent’s real-time workflow updates (chain-of-thought, final recommendation, update messages) and the corresponding MongoDB run documents.

## Why MongoDB?

### Flexible Data Model

MongoDB’s document-oriented architecture allows you to store varied data (such as timeseries logs, agent profiles, and recommendation outputs) in a single unified format. This flexibility means you don’t have to redesign your database schema every time your data requirements evolve.

### Scalability and Performance

MongoDB is designed to scale horizontally, making it capable of handling large volumes of real-time data. This is essential when multiple data sources send timeseries data simultaneously, ensuring high performance under heavy load.

### Real-Time Analytics

With powerful aggregation frameworks and change streams, MongoDB supports real-time data analysis and anomaly detection. This enables the system to process incoming timeseries data on the fly and quickly surface critical insights.

### Seamless Integration

MongoDB is seamlessly integrated with LangGraph, making it a powerful memory provider.

### Vector Search

MongoDB Atlas supports native vector search, enabling fast and efficient similarity searches on embedding vectors. This is critical for matching current queries with historical data, thereby enhancing diagnostic accuracy and providing more relevant recommendations.

### Geospatial Queries

MongoDB’s geospatial capabilities allow for advanced location-based queries, which can be useful in scenarios where timeseries data is tied to specific geographic locations.

## Tech Stack

### Backend 

- [MongoDB Atlas](https://www.mongodb.com/atlas/database) for the database.
- [FastAPI](https://fastapi.tiangolo.com/) for building the API.
- [LangGraph](https://www.langchain.com/langgraph) for designing the agent workflows.
- [LangChain](https://www.langchain.com/) to interact and build with LLMs.
- [Uvicorn](https://www.uvicorn.org/) for ASGI server.
- [Docker](https://www.docker.com/) for containerization.

### Frontend

- **Web Framework**:  
  - [Next.js](https://nextjs.org/)

- **Styling**:  
  - [CSS Modules](https://github.com/css-modules/css-modules)  
  - [LeafyGreen Design System](https://www.mongodb.design/)

- **UI Components**:  
  - [Leafygreen UI](https://github.com/mongodb/leafygreen-ui) for customizable components.

- **Core React and Next.js**:  
  - `next`, `react`, `react-dom`

## Prerequisites

Before you begin, ensure you have met the following requirements:

- **MongoDB Atlas** account - [Register Here](https://account.mongodb.com/account/register)
- **Python >=3.10,<3.11** - If you are Mac user, you can install Python 3.10.11 using this [link](https://www.python.org/ftp/python/3.10.11/python-3.10.11-macos11.pkg).
- **Docker** installed
- **Node.js** installed
- **VoyageAI** account
- **AWS Account** with access to Bedrock service

## Getting Started

### Cloning the Repository

1. Navigate to the repository on GitHub and obtain the repository URL.
2. Open your terminal and run the following command to clone the repository:

```bash
git clone <REPOSITORY_URL>
```

### GitHub Desktop Setup

1. Install GitHub Desktop if you haven't already. You can download it from [GitHub Desktop's official website](https://desktop.github.com/).
2. Open GitHub Desktop and sign in to your GitHub account.
3. Click on "File" in the menu bar and select "Clone repository."
4. In the "Clone a repository" window, select the "URL" tab.
5. Paste the repository URL you copied earlier into the "Repository URL" field.
6. Choose the local path where you want to clone the repository by clicking on "Choose..."
7. Click the "Clone" button to start cloning the repository to your local machine.

## Setup Instructions

This demo consists of a backend with multiple microservices. Each microservice has its own `Dockerfile` and can be run independently. The backend services are defined in the `docker-compose.yml` file located in the root directory.

### Step 1: Set Up MongoDB Database and Collections

1. Log in to **MongoDB Atlas** and obtain your **MongoDB connection string URI**. Follow [this guide](https://www.mongodb.com/resources/products/fundamentals/mongodb-connection-string) if you need help obtaining a connection string.

### Step 2: Obtain access to LLMs

1. Set up an account with **AWS** and ensure you have a role which you can access on the computer where you will run the backend service. The role must have access to **AWS Bedrock** service.
2. Ensure that you have access to the **Anthropic Claude 3 Haiku** for chat completions.

### Step 3: Obtain the VoyageAI API Key
1. Sign up for a **VoyageAI** account if you don't have one already.
2. Navigate to the API section of your VoyageAI account to generate an API key.
3. Copy the generated API key and keep it secure, as you will need it to configure the backend service.

This API key will be used to access the Voyage-3.5 model for generating embeddings.

### Step 4: Configure the `.env` files

You will need to have 2 sets of environment variables, one for the backend and one for the frontend.

#### Backend Configuration - `.env`

Thi is the .env that goes into the `/backend` directory.

```bash
MONGODB_URI="mongodb+srv://<USERNAME>:<PASSWORD>@<CLUSTER>"
APP_NAME="leafy_fleet"
AWS_REGION=<THE_AWS_REGION_YOU_SET_UP_YOUR_ACCOUNT_IN>
AWS_PROFILE=<YOUR_AWS_PROFILE_NAME>
ORIGINS=http://localhost:3000 # your local dev server
VOYAGE_API_KEY=<YOUR_VOYAGE_API_KEY>
STATIC_SERVICE_ENDPOINT=http://static-vehicle-service
TIMESERIES_POST_ENDPOINT=http://timeseries-post-service
GEOFENCES_SERVICE_ENDPOINT=http://geofence-get-service
```

Only replace the values in `<>` with your actual values.

You'll need to copy this file into multiple directories for different services in the backend:
- `/backend`
- `/backend/agent`
- `/backend/geofenceGET/app`
- `/backend/sessions/app`
- `/backend/simulation/app`
- `/backend/static_service/app`
- `/backend/timeSeriesGET/app`
- `/backend/timeSeriesPOST/app`

> **IMPORTANT NOTES**: Make sure you create a docker network the first time you run the services by executing:
```bash
docker network create -d bridge simulation-network
```

Once you made sure the network is created, the `.env` files are in place, and your computer has access to the AWS profile you can run the backend services with the following command from the `/backend` directory:
```bash
docker compose up -d
```
docker should build the containers and start the services.




> **_IMPORTANT NOTES_**: For better understanding of the JSON `config.json` file inside agent, this is the main configuration file for the Agent.

Attributes in config.json
1. `CSV_DATA`:
   * Path to the CSV file containing the data for your use case.
   * Example: `data/csv/macro_indicators_data.csv`

2. `MDB_DATABASE_NAME`:
   * Name of the MongoDB database where all collections and data are stored.
   * Example: `agentic_macro_indicators`

3. `MDB_TIMESERIES_COLLECTION`:
    * Name of the MongoDB collection used to store timeseries data.
    * Example: `macro_indicators_timeseries`

4. `DEFAULT_TIMESERIES_DATA`:
    * Default timeseries data to be used when no data is available in the database.
    * Example:

    ```json
    {
        "timestamp": "2025-02-19T13:00:00Z",
        "gdp": 2.5,
        "interest_rate": 1.75,
        "unemployment_rate": 3.8,
        "vix": 15
    }
    ```
    
5. `CRITICAL_CONDITIONS`:
    * Defines thresholds and conditions for critical metrics in your use case.
    * Example:
    ```json
    {
        "gdp": {"threshold": 2.5, "condition": "<", "message": "GDP growth slowing: {value}%"},
        "interest_rate": {"threshold": 2.0, "condition": ">", "message": "Interest rates rising: {value}%"},
        "unemployment_rate": {"threshold": 4.0, "condition": ">", "message": "Unemployment rate increasing: {value}%"},
        "vix": {"threshold": 20, "condition": ">", "message": "High market volatility (VIX): {value}"}
    }
    ```
    * Each condition includes:
        - `threshold`: TThe value to compare against.
        - `condition`: The comparison operator (`<`, `>`, etc.).
        - `message`: The message to display when the condition is met.

6. `MDB_TIMESERIES_TIMEFIELD`:
    * Name of the field in the timeseries data that represents the timestamp.
    * Example: `timestamp`

7. `MDB_TIMESERIES_GRANULARITY`:
    * Granularity of the timeseries data (e.g. `minutes`, `hours`, `days`).
    * Example: `minutes`

8. `MDB_EMBEDDINGS_COLLECTION`:
    * Name of the MongoDB collection used to store query embeddings.
    * Example: `queries`

9. `MDB_EMBEDDINGS_COLLECTION_VS_FIELD`:
    * Name of the field in the embeddings collection that stores the embeddings.
    * Example: `query_embedding`

10. `MDB_VS_INDEX`:
    * Name of the MongoDB index used for vector search.
    * Example: `agentic_macro_indicators_queries_vs_idx`

11. `MDB_HISTORICAL_RECOMMENDATIONS_COLLECTION`:
    * Name of the MongoDB collection used to store historical recommendations.
    * Example: `historical_recommendations`

12. `SIMILAR_QUERIES`:
    * Default queries and recommendations used for vector search when no match is found in the database.
    * Example:
    ```json
    [
        {"query": "GDP growth slowing", "recommendation": "Consider increasing bond assets to mitigate risks from potential economic slowdown."},
        {"query": "Interest rates rising", "recommendation": "Shift focus to bond assets as higher rates may impact borrowing-sensitive sectors."}
    ]
    ```

13. `MDB_CHAT_HISTORY_COLLECTION`:
    * Name of the MongoDB collection used to store chat history.
    * Example: `chat_history`

14. `MDB_CHECKPOINTER_COLLECTION`:
    * Name of the MongoDB collection used to store checkpoints.
    * Example: `checkpoints`

15. `MDB_LOGS_COLLECTION`:
    * Name of the MongoDB collection used to store logs.
    * Example: `logs`

16. `MDB_AGENT_PROFILES_COLLECTION`:
    * Name of the MongoDB collection used to store agent profiles. e.g.: `agent_profiles`
    * You can add your custom agent profiles to this collection by importing a JSON file to the collection.
    * Example for a Finance Agent Profile:
    ```json
    {
      "_id": {
        "$oid": "67d2bffdf3fe062c9a3dbe3d"
      },
      "agent_id": "FINANCE_AG01",
      "profile": "Finance Agent Profile",
      "role": "Portfolio Advisor",
      "kind_of_data": "Macroeconomic Indicators",
      "motive": "Analyze macroeconomic data and provide portfolio adjustment recommendations.",
      "instructions": "Follow economic trends and portfolio management principles.",
      "rules": "Document all steps; ensure compliance with financial regulations; validate data accuracy.",
      "goals": "Optimize portfolio allocation based on macroeconomic conditions and provide actionable insights."
    }
    ```
    * The `AGENT_PROFILE_CHOSEN_ID` will determine which agent profile to use in the agent workflow.

17. `MDB_AGENT_SESSIONS_COLLECTION`:
    * Name of the MongoDB collection used to store agent sessions.
    * Example: `agent_sessions`

18. `AGENT_PROFILE_CHOSEN_ID`:
    * ID of the agent profile to be used in the agent workflow.
    * Example: `FINANCE_AG01`

19. `DEFAULT_AGENT_PROFILE`:
    * Default agent profile used in the agent workflow.
    * Example:
    ```json
    {
        "agent_id": "DEFAULT",
        "profile": "Default Agent Profile",
        "role": "Expert Advisor",
        "kind_of_data": "Specific Data",
        "motive": "diagnose the query and provide recommendations",
        "instructions": "Follow procedures meticulously.",
        "rules": "Document all steps.",
        "goals": "Provide actionable recommendations."
    }
    ```

20. `EMBEDDINGS_MODEL_NAME`:
    * Name of the embeddings model used for creating the chain of thought.
    * Example: `Cohere Embed English V3 Model (within AWS Bedrock)`

21. `EMBEDDINGS_MODEL_ID`:
    * Model ID of the embeddings model.
    * Example: `cohere.embed-english-v3`

22. `CHATCOMPLETIONS_MODEL_NAME`:
    * Name of the chat completions model used for generating responses.
    * Example: `Anthropic Claude 3 Haiku (within AWS Bedrock)`

23. `CHATCOMPLETIONS_MODEL_ID`:
    * Model ID of the chat completions model.
    * Example: `anthropic.claude-3-haiku-20240307-v1:0`

24. `AGENT_WORKFLOW_GRAPH`:
    * Agent workflow graph that defines the sequence of tools used in the agent workflow.
    * Example:
    ```json
    {
        "nodes": [
            {"id": "reasoning_node", "tool": "agent_tools.generate_chain_of_thought_tool"},
            {"id": "data_from_csv", "tool": "agent_tools.get_data_from_csv_tool"},
            {"id": "process_data", "tool": "agent_tools.process_data_tool"},
            {"id": "embedding_node", "tool": "agent_tools.get_query_embedding_tool"},
            {"id": "vector_search", "tool": "agent_tools.vector_search_tool"},
            {"id": "process_vector_search", "tool": "agent_tools.process_vector_search_tool"},
            {"id": "persistence_node", "tool": "agent_tools.persist_data_tool"},
            {"id": "recommendation_node", "tool": "agent_tools.get_llm_recommendation_tool"}
        ],
        "edges": [
            {"from": "reasoning_node", "to": "data_from_csv"},
            {"from": "data_from_csv", "to": "process_data"},
            {"from": "process_data", "to": "embedding_node"},
            {"from": "embedding_node", "to": "vector_search"},
            {"from": "vector_search", "to": "process_vector_search"},
            {"from": "process_vector_search", "to": "persistence_node"},
            {"from": "persistence_node", "to": "recommendation_node"},
            {"from": "recommendation_node", "to": "END"}
        ],
        "entry_point": "reasoning_node"
    }
    ```
    * Components:
        - `nodes`: Defines the tools used in the workflow.
        - `edges`: Defines the connections between nodes.
        - `entry_point`: Starting point of the agent workflow.

### Step 5: Configure Environment Variables

#### Backend

1. Create a `.env` file in the `/backend` directory with the following content:

```bash
MONGODB_URI="mongodb+srv://<USERNAME>:<PASSWORD>@<CLUSTER>"
APP_NAME="<YOUR_APP_NAME>"
AWS_REGION="<YOUR_AWS_REGION>"
ORIGINS=http://localhost:3000
```

#### Frontend

2. Create a `.env` file in the `/frontend` directory with the following content:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_INITIAL_QUERY="<YOUR_INITIAL_QUERY>"
```
E.g. for **macro indicators** use case:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_INITIAL_QUERY="What adjustments should I make to my portfolio given the current macro economic conditions?"
```

### Step 6: Create Embeddings for the queries

1. Run [embedder.py](/backend/embedder.py) to create and store embeddings in MongoDB.

### Step 7: Create Vector Search Index in MongoDB

1. Run [mdb_vector_search_idx_creator.py](/backend/mdb_vector_search_idx_creator.py) to create a vector search index in MongoDB.

### Step 8: Customize your Frontend

1. Ensure to customize your frontend by updating [page.jsx](/frontend/app/page.jsx) according to your use case.

## Run it Locally

### Backend

1. (Optional) Set your project description and author information in the `pyproject.toml` file:
   ```toml
   description = "Your Description"
   authors = ["Your Name <you@example.com>"]
2. Open the project in your preferred IDE (the standard for the team is Visual Studio Code).
3. Open the Terminal within Visual Studio Code.
4. Ensure you are in the root project directory where the `makefile` is located.
5. Execute the following commands:
  - Poetry start
    ````bash
    make poetry_start
    ````
  - Poetry install
    ````bash
    make poetry_install
    ````
6. Verify that the `.venv` folder has been generated within the `/backend` directory.
7. To start the backend service, run:

```bash
poetry run uvicorn main:app --host 0.0.0.0 --port 8000
```

> Default port is `8000`, modify the `--port` flag if needed.

### Frontend

1. Navigate to the `/frontend` folder.
2. Install dependencies by running:
```bash
npm install
```
3. Start the frontend development server with:
````bash
npm run dev
````
4. The frontend will now be accessible at http://localhost:3000 by default, providing a user interface.


## Run with Docker

Make sure to run this on the root directory.

1. To run with Docker use the following command:
```
make build
```
2. To delete the container and image run:
```
make clean
```

## Common errors

- Check that you've created the necessary  `.env` files within the `/backend` and `/frontend` directories.
- Ensure that the MongoDB URI is correct and that the user has the necessary permissions.
- Verify that the MongoDB collections and data are correctly set up.
- Check that the `config.json` file is correctly configured following the guidelines provided.
- Ensure that the CSV data and queries are correctly formatted and stored in the `/backend/data/csv` directory.
- Verify that the embeddings have been created and stored in the MongoDB collection.
- Check that the vector search index has been created in MongoDB.
- Verify that the backend and frontend services are running on the correct ports.

## Demo Presentation & Talk Track

### Overview

The Agentic Framework serves as a versatile AI-driven recommendation assistant capable of comprehending your data, performing a multi-step diagnostic workflow using LangGraph, and generating actionable recommendations. The framework integrates several key technologies. It reads timeseries data from a CSV file or MongoDB (simulating various data inputs), generates text embeddings using the Cohere English V3 model, performs vector searches to identify similar past queries from MongoDB, persists session and run data, and finally generates a diagnostic recommendation. MongoDB stores agent profiles, historical recommendations, timeseries data, session logs, and more. This persistent storage not only logs every step of the diagnostic process for traceability but also enables efficient querying and reusability of past data.
  
- **Backend:**  
  Implements a multi-step diagnostic workflow using LangGraph. The backend reads timeseries data from a CSV file, generates text embeddings using Cohere English V3 model, performs vector searches to identify similar past queries, persists session and run data, and finally generates a diagnostic recommendation.

- **MongoDB:**  
  The flexible document model database stores agent profiles, historical recommendations, timeseries data, session logs, and more. This persistent storage not only logs every step of the diagnostic process for traceability but also enables efficient querying and reusability of past data.

- **Next.js Frontend:**  
  Provides a two-column view:
  - **Left Column:** Displays the real-time agent workflow updates such as the chain-of-thought reasoning, update messages, and final recommendations.
  - **Right Column:** Shows the documents inserted into MongoDB during the agent run, including session details, logs, historical recommendations, agent profiles and sample past issues.


**System Architecture:**  
   - **Backend Workflow:**  
     - The agent receives a user’s query report (e.g., "What adjustments should I make to my portfolio given the current macro economic conditions?").
     - It first retrieves timeseries data (simulated here via a CSV file) and logs the update.
     - Next, it generates an embedding for the complaint using Cohere English V3 model.
     - The system then performs a vector search against historical queries in MongoDB to find similar cases.
     - All data (timeseries, embeddings, session logs) are persisted in MongoDB for traceability.
     - Finally, the agent uses Anthropic Claude 3 Haiku model to generate a final recommendation.
   - **MongoDB Role:**  
     - MongoDB stores everything: the agent profile, session logs, timeseries data, historical recommendations, and even checkpoints. This makes the system highly traceable and scalable.
   - **Frontend Interface:**  
     - The two-column UI shows both the real-time workflow and the relevant MongoDB documents that validate each step.


### Demo Presentation Flow

3. **Live Demonstration (takes about 5-7 minutes):**  
   - **Starting a New Diagnosis:**  
     - Open the frontend and choose “New Diagnosis.”
     - Enter a query in the text box (e.g. "What adjustments should I make to my portfolio given the current macro economic conditions?").
     - Example prompts
        - "What adjustments should I make to my portfolio given the current macro economic conditions?"
        - "What should I do with my investments given the current economic climate?"
        - "How should I adjust my portfolio based on the current economic indicators?"
        - "What changes should I make to my investments based on the current economic data?"
     - Click the “Run Agent” button and **wait** for a few mins as the agent finishes its run 
   - **Viewing Workflow:**  
     - The workflow , chain-of-thought output, and the final recommendation is shown in the left column.
     - The workflow is being generated in real time, giving transparency into the agent's decision-making process.

   - **Reviewing MongoDB Documents:**  
     - In the right column, the documents shown are the records inserted during the current agent run.
       - **agent_sessions:** Contains session metadata and the thread ID.
       - **historical_recommendations:** Stores the final recommendations and related diagnostics.
       - **timeseries_data:** Holds the timeseries data used in the diagnostic process.
       - **logs:** Contains log entries for the diagnostic process.
       - **agent_profiles:** Shows the agent's profile that was used during diagnosis.
       - **past_issues:** (If available) Displays a sample of historical issues.
       - **checkpoints:** (From the checkpointing database) Shows the last saved state for potential recovery.
   - **Resume Functionality:**  
     - Optionally, we can demonstrate the "Resume Diagnosis" feature by entering a thread ID and showing how the system retrieves the corresponding session.

## Future tasks

- [ ] Add tests

## Feedback or Suggestions

* Contact the MongoDB Industry Solutions team.

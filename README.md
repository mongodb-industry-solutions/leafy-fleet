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

### Step 1: Retreieve your MongoDB connection string

1. Log in to **MongoDB Atlas** and obtain your **MongoDB connection string URI**. Follow [this guide](https://www.mongodb.com/resources/products/fundamentals/mongodb-connection-string) if you need help obtaining a connection string.

###  Step 2. Populate your database
Next, populate your database with the required data and metadata required for the demo. In the application code locate the dump/leafy_popup_store directory. Inside it, there are several .gz files which contain the data and metadata of the collections: users, products, orders, locations and carts.

Use the [mongorestore](https://www.mongodb.com/docs/database-tools/mongorestore/) command to load the data from the database dump into a new database within your Cluster.

You will need a way of interacting with your MongoDB Atlas cluster. The easiest way is to use the [MongoDB Shell](https://www.mongodb.com/docs/mongodb-shell/install/)

Let's go back to your terminal, navigate to the directory /leafy-fleet (the root level of the application code), and run the following command:

```bash
mongorestore --uri "mongodb+srv://<user>:<password>@<cluster-url>" ./dmp/leafy_fleet
```

This command will create the database and collections and log its progress. Upon completion, you should see a log like this:

```bash
X document(s) restored successfully. 0 document(s) failed to restore.
```

Perfect! You now have your application code with environment variables, all the dependencies installed and the database created with the required data loaded.


Curious about how the database dump was generated? Check out  the documentation for the mongodump command. 



### Step 3: Obtain access to LLMs

1. Set up an account with **AWS** and ensure you have a role which you can access on the computer where you will run the backend service. The role must have access to **AWS Bedrock** service.
2. Ensure that you have access to the **Anthropic Claude 3 Haiku** for chat completions.

### Step 4: Obtain the VoyageAI API Key
1. Sign up for a **VoyageAI** account if you don't have one already.
2. Navigate to the API section of your VoyageAI account to generate an API key.
3. Copy the generated API key and keep it secure, as you will need it to configure the backend service.

This API key will be used to access the Voyage-3.5 model for generating embeddings.

### Step 5: Configure the `.env` files

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
- `/`
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



#### Frontend

2. Create a `.env` file in the `/frontend` directory with the following content:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
LOCAL_API_URL=http://localhost:3000
NEXT_PUBLIC_AGENT_SERVICE_URL=localhost:9000
NEXT_PUBLIC_TIMESERIES_GET_SERVICE_URL=localhost:9001
NEXT_PUBLIC_SESSIONS_SERVICE_URL=localhost:9003
NEXT_PUBLIC_GEOSPATIAL_SERVICE_URL=localhost:9004
NEXT_PUBLIC_SIMULATION_SERVICE_URL=localhost:9006
NEXT_PUBLIC_GEOFENCES_SERVICE_URL=localhost:9005
```

## Run it Locally

Once you made sure the network is created, the `.env` files are in place, and your computer has access to the AWS profile you can run the backend services with the following command from the root `/` directory:
```bash
docker compose up -d
```
Docker should build the containers and start the services.

Once the services are up and running you can start the frontend by going into your browser and navigating to `http://localhost:3000`. This will load the frontend application, which connects to the backend services running on the specified ports.

You can go to `http://localhost:3000/chat` to access the chat interface.



## Application flow

The flow of the application's AI Agent backend is as follows:

1. **Frontend**: Once the user loads the `/chat` on the frontend, the client connects to a websocket server to receive real-time updates from the AI Agent (shown as its chain-of-thought).
2. **Backend**: When the user sends a query, a REST request is received in `/agent/app/main.py`, which starts the agent workflow.
3. `main.py` parses environment variables, sets up the agent workflow, and invokes the LangGraph graph builder via `/backend/agent/async_workflow_runner.py` (see https://langchain-ai.github.io/langgraph/how-tos/graph-api/#async).
4. The async workflow builder loads nodes and their order from `/backend/agent/config/config.json`, beginning with the embedding node implemented in `/backend/agent/agent_tools.py` as `get_query_embedding_tool`.
5. The graph contains conditional edges — at runtime the agent chooses different paths (for example, routing to a vector search tool when similar results exist, otherwise routing to the reasoning node). Routing logic is implemented inside the corresponding tool functions (see `vector_search_tool` in `/backend/agent/agent_tools.py`).


## Important notes

- The JSON file `config.json` inside `/backend/agent/config/` is the primary configuration for the agent. Review it to understand the workflow graph and other settings.

### Key attributes in `config.json`

1. `MDB_DATABASE_NAME`:
   - Name of the MongoDB database where collections and data are stored.

2. `MDB_TIMESERIES_COLLECTION`:
   - Name of the MongoDB collection used for timeseries data (e.g. `timeseries_data`).

3. `MDB_TIMESERIES_TIMEFIELD`:
   - Field name representing the timestamp (e.g. `timestamp`).

4. `MDB_TIMESERIES_GRANULARITY`:
   - Granularity of the timeseries data (e.g. `minutes`, `hours`, `days`).

5. `MDB_EMBEDDINGS_COLLECTION`:
   - Collection for storing query embeddings (e.g. `historical_recommendations`).

6. `MDB_EMBEDDINGS_COLLECTION_VS_FIELD`:
   - Field in the embeddings collection that stores the embedding vector (e.g. `query_embedding`).

7. `MDB_VS_INDEX`:
   - Name of the MongoDB vector-search index (e.g. `agentic_historical_recommendations_queries_idx`).

8. `MDB_HISTORICAL_RECOMMENDATIONS_COLLECTION`:
   - Collection for historical recommendations (e.g. `historical_recommendations`).

9. `MDB_CHECKPOINTER_COLLECTION`:
   - Collection for storing checkpoints (e.g. `checkpoints`).

10. `MDB_AGENT_PROFILES_COLLECTION`:
   - Collection for agent profiles (e.g. `agent_profiles`). You can add custom profiles by importing JSON documents.

11. `MDB_AGENT_SESSIONS_COLLECTION`:
   - Collection for agent sessions (e.g. `agent_sessions`).

12. `DEFAULT_AGENT_PROFILE`:
   - Default profile used by the agent. Example:

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

13. `CHATCOMPLETIONS_MODEL_NAME`:
   - Name of the chat model used for generating responses (e.g. Anthropic Claude 3 Haiku via Bedrock).

14. `CHATCOMPLETIONS_MODEL_ID`:
   - Model ID used for chat completions (example format provided in the file).

15. `AGENT_WORKFLOW_GRAPH`:
   - Defines nodes, edges, conditional_edges, and entry_point for the LangGraph workflow. Example structure is included in the repository README below.



## Common Errors & Troubleshooting

- If you are deploying on a local machine, ensure that the .aws folder is present in the directory of the agent microservice. This folder should contain your AWS credentials and configuration files, if not, configure a secret in your AWS Secrets Manager and update the `AWS_PROFILE` in the `.env` file accordingly.
- There should be an env in every folder in the project, since the project is designed for every service to run independently.
- If you are using Docker, ensure that the Docker network is created before running the services.
- If experiencing build issues with peer dependencies, try installing with `npm install --legacy-peer-deps`


## Suggestions for improvement

- Allow the chatbot to answer user's questions about how the demo works


## Authors & Contributors


- **Humza Akhtar** — Senior Principal — humza.akhtar@mongodb.com
- **Raphael Schor** — Principal — raphael.schor@mongodb.com
- **Kirill Makienko** — Developer — https://github.com/Kicho-Fops
- **Fernando Morán** — Developer — https://github.com/fermofou
- **Romina Carranza** — Maintainer — romina.carranza@mongodb.com
- **Rami Pinto** — Maintainer — rami.pinto@mongodb.com

## License

© 2025 MongoDB. All rights reserved.

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

This repository is intended solely for demonstration and educational purposes.  
No support or warranty is provided. Use at your own risk.

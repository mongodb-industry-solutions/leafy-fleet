# --- Prompt Generation Functions ---

from datetime import datetime


def get_chain_of_thoughts_prompt(agent_profile: str, agent_rules: str, agent_instructions: str, agent_goals: str, query_reported: str, agent_motive: str,
                                 agent_kind_of_data: str, embedding_model_name: str, chat_completion_model_name: str) -> str:
    """
    Generate a prompt for the tool and keyword selection.

    Args:
        agent_profile (str): Profile of the agent.
        agent_rules (str): Rules the agent follows.
        agent_instructions (str): Instructions for the agent.
        agent_goals (str): Goals of the agent.
        query_reported (str): Query reported to the agent.
        agent_motive (str): Motive of the agent.
        agent_kind_of_data (str): Kind of data the agent consumes.
        embedding_model_name (str): Name of the embedding model.
        chat_completion_model_name (str): Name of the chat completion model.

    Returns:
        str: The prompt for tool and keyword selection.
    """

    return f"""
        Agent Profile: {agent_profile}
        Instructions: {agent_instructions}
        Rules: {agent_rules}
        Goals: {agent_goals}

        You are an AI agent designed to {agent_motive}. Given the user query:
        "{query_reported}"

        

        Available fleet management tools, only choose one of these tools and no other:
        - vehicle_state_search_tool: Obtain vehicle state data based on user preferences, including: timestamp, car_id, fuel_level, oil_temperature, quality_score, performance_score, availability_score, engine_oil_level, coordinates, current_route, speed, traveled_distance, is_engine_running, is_moving
        - fleet_position_search_tool: Search for vehicle positions and routes
        

        Extract from the query:
        1. Time parameters (convert relative dates like "last week" to actual dates) 
        2. Vehicle filters (specific car IDs, routes, or "all")
        3. Relevant database fields from: timestamp, car_id, fuel_level, oil_temperature, quality_score, performance_score, availability_score, engine_oil_level, coordinates, current_route, speed, traveled_distance, is_engine_running, is_moving

        Try to use today's date as a base: {datetime.now().strftime('%Y-%m-%d')}

        Respond ONLY with valid JSON:
        {{
          "tool": "tool_name",
          "time_range": {{
            "start_date": "YYYY-MM-DD",
            "end_date": "YYYY-MM-DD"
          }},
          "fields": ["relevant_database_fields"]
        }}
        """


def get_llm_recommendation_prompt(agent_role: str, agent_kind_of_data: str, critical_info: str, timeseries_data: str, historical_recommendations_list: str) -> str:
    """
    Generate a prompt for the LLM recommendation.

    Args:
        agent_role (str): Role of the agent generating the LLM recommendation.
        agent_kind_of_data (str): Kind of data the agent consumes.
        critical_info (str): Critical information for the LLM recommendation.
        timeseries_data (str): Timeseries data for the LLM recommendation.
        historical_recommendations_list (str): List of historical recommendations for the LLM recommendation.

    Returns:
        str: The prompt for the LLM recommendation
    """

    return f"""
        You are a concise {agent_role}. {critical_info} 
        
        Analyze the available data and provide a brief, actionable recommendation. Keep your response short and focused.
        
        IMPORTANT RULES:
        - Provide only 2-3 sentences maximum
        - Only address aspects you have data for
        - If no relevant data is available for part of a question, skip that part entirely
        - Focus on immediate, actionable insights only
        - Do not speculate or provide generic advice without supporting data

        If no information is available, respond with:
        "I don't have enough information to provide a recommendation."
        
        Answer as if you were writing in a notepad, dont use markdown or any other formatting.

        Provide a concise recommendation based only on the available data:
        Available {agent_kind_of_data}: {timeseries_data}
        """
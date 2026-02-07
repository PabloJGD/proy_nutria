import os
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from src.tools.vision import analyze_image_for_ingredients
from src.tools.nutrition import find_recipes_by_ingredients, get_recipe_details
from src.prompts.chef_prompt import get_chat_prompt
from src.models.schemas import AgentInput

# Load tools
tools = [analyze_image_for_ingredients, find_recipes_by_ingredients, get_recipe_details]

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0.7)

# Create Agent
prompt = get_chat_prompt()
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

def process_request(request: AgentInput):
    """
    Main entry point for the agent. 
    Constructs the prompt inputs from the pydantic model.
    """
    # Format restrictions and profile for the prompt
    profile_str = f"Age: {request.user_profile.age}, Goals: {request.user_profile.health_goals}"
    restrictions_str = ", ".join(request.user_profile.dietary_restrictions) + ", " + ", ".join(request.user_profile.allergies)
    
    # Construct input text
    user_input = ""
    if request.text_description:
        user_input += f"Ingredients available: {request.text_description}.\n"
    if request.image_data:
        # Pass the image path/url to the tool via the prompt text instruction implicitly? 
        # Actually, the agent needs to know there is an image. 
        # The tool `analyze_image_for_ingredients` takes a path. 
        # We need to tell the agent to use the tool on this path.
        user_input += f"I have an image of ingredients at: {request.image_data}. Please analyze it."
    
    result = agent_executor.invoke({
        "input": user_input,
        "user_profile": profile_str,
        "restrictions": restrictions_str
    })
    
    return result["output"]

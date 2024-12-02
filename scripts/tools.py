from langchain_openai import AzureChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
import os

def SQLQueryChecker(SQL_query: str) -> str:
    """
    Use an LLM to check if an SQL query is correct.

    Args:
        SQL_query (str): The SQL query to validate.

    Returns:
        str: A message indicating whether the query is valid, and if not, what might be wrong.
    """
    try:
        # Initialize the Azure OpenAI instance
        llm = AzureChatOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_deployment=os.getenv("DEPLOYMENT_NAME"),
            openai_api_version=os.getenv("OPENAI_API_VERSION"),
        )
        print("LLM successfully initialized!")

        # Create the system and user messages
        system_message = SystemMessage(
            content=(
                """You are a SQL query expert. Your task is to analyze SQL queries and determine if they are syntaxically correct. 
                If the query is correct, return the query, however if it's not correct it and return the corrected query. 
                Assume a standard SQL dialect."""
            )
        )
        user_message = HumanMessage(content=f"Here is the SQL query: {SQL_query}\nPlease validate this query and provide feedback.")

        # Use the LLM to evaluate the query
        response = llm.invoke([system_message, user_message])

        # Extract and return the content of the LLM's response
        return response.content

    except Exception as e:
        return f"An error occurred while checking the SQL query: {e}"

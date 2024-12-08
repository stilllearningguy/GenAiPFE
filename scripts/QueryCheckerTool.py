from langchain_openai import AzureChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
import os

def SQLQueryChecker(SQL_query: str) -> str:
    """
    Use an LLM to check if an SQL query is correct.

    Args:
        SQL_query (str): The SQL query to validate.

    Returns:
        str: The validated or corrected SQL query.
    """
    try:
        # Initialize the Azure OpenAI instance
        llm = AzureChatOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_deployment=os.getenv("DEPLOYMENT_NAME"),
            openai_api_version=os.getenv("OPENAI_API_VERSION"),
            temperature=0,
        )
        print("LLM successfully initialized!")

        # Create the system and user messages
        system_message = SystemMessage(
            content=(
                """You are a SQL query expert. Your task is to analyze SQL queries and determine if they are syntactically correct.
                If the query is correct, return the query exactly as is. If it is incorrect, return only the corrected SQL query.
                Assume a standard SQL dialect.
                -Your response should be only an sql query and nothing else."""
            )
        )
        user_message = HumanMessage(content=f"Here is the SQL query: {SQL_query}")

        # Use the LLM to evaluate the query
        response = llm.invoke([system_message, user_message])

        # Extract and return the content of the LLM's response (assumes response is a single SQL query string)
        return response.content.strip()

    except Exception as e:
        return f"An error occurred while checking the SQL query: {e}"


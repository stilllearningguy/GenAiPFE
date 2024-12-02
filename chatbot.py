import os
from dotenv import load_dotenv
import getpass
from langchain_openai import AzureChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from scripts.tools import SQLQueryChecker 

load_dotenv()

if not os.getenv("AZURE_OPENAI_API_KEY"):
    os.environ["AZURE_OPENAI_API_KEY"] = getpass.getpass("Enter AZURE_OPENAI_API_KEY: ")

# check environment variables
required_env_vars = ["AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT", "DEPLOYMENT_NAME", "OPENAI_API_VERSION"]
for var in required_env_vars:
    value = os.getenv(var)
    if not value:
        raise ValueError(f"Environment variable {var} is missing or empty!")
    print(f"{var}: {value}")

# AzureChatOpenAI
try:
    llm = AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment=os.getenv("DEPLOYMENT_NAME"),
        openai_api_version=os.getenv("OPENAI_API_VERSION"),
    )
    print("LLM successfully initialized!")
except Exception as e:
    raise RuntimeError(f"Failed to initialize AzureChatOpenAI: {e}")

# database
db = SQLDatabase.from_uri("sqlite:///D:/GenAiPFE/Chinook.db")

# check database connection
try:
    print("Database Dialect:", db.dialect)
    print("Usable Tables:", db.get_usable_table_names())
    print("Sample Query Result:", db.run("SELECT * FROM Artist LIMIT 10;"))
except Exception as e:
    raise RuntimeError(f"Database connection failed: {e}")

# Create SQL query chain
try:
    chain = create_sql_query_chain(llm, db)
    print("SQL Query Chain successfully created!")
except Exception as e:
    raise RuntimeError(f"Failed to create SQL Query Chain: {e}")

# Ask a question and generate a SQL query
try:
    question = "How many employees are there?"
    response = chain.invoke({"question": question})
    print("Generated SQL Query:", response)
except Exception as e:
    raise RuntimeError(f"Failed to generate SQL query: {e}")

# check il sql bel tool jdida 
try:
    result = SQLQueryChecker(response) 
    print("LLM Feedback on query:\n", result)
except Exception as e:
    raise RuntimeError(f"Failed to check the generated query: {e}")

# Execute the generated SQL query
try:
    query_result = db.run(response)
    print("Query Result:", query_result)
except Exception as e:
    raise RuntimeError(f"Failed to execute the generated query: {e}")


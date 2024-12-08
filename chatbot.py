import os
from dotenv import load_dotenv
import getpass
from langchain_openai import AzureChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from scripts.QueryCheckerTool import SQLQueryChecker 
from scripts.SchemaTool import get_database_schema
from langchain.prompts import PromptTemplate

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
schema = get_database_schema("sqlite:///D:/GenAiPFE/Chinook.db")

# prompting 
initial_prompt = PromptTemplate(
    input_variables=["input", "table_info", "top_k"],
    template=(
        """You are an intelligent assistant designed to interact with a relational SQL database. Your primary task is to generate syntactically correct SQL queries based on user questions, adhering to the schema provided below. 

Schema:
{table_info}

Instructions:
- Analyze the input question and generate a valid SQL query that directly answers the question.
- Always limit the number of results to {top_k} rows unless the user specifies otherwise, using the appropriate SQL syntax for the database dialect.
- Select only the relevant columns necessary to answer the question; do not query all columns from a table.
- If the question is unclear or does not relate to the database, respond with "I don't know."
- Review and validate your SQL query for correctness and alignment with the schema before finalizing it. If the query might generate an error or seems incorrect, revise it before execution.
- Avoid performing any data modification operations like INSERT, UPDATE, DELETE, or DROP.
- Use the information from the database schema to ensure your queries align with the database structure and relationships between tables.

Follow these guidelines strictly to provide accurate and meaningful SQL queries for the user question provided below.

User question:
{input}."""
    )
)

# Create SQL query chain
try:
    chain = create_sql_query_chain(llm, db, prompt=initial_prompt)
    print("SQL Query Chain successfully created!")
except Exception as e:
    raise RuntimeError(f"Failed to create SQL Query Chain: {e}")

try:
    question = "give me the top albums based on the number of tracks in each album"
    response = chain.invoke({"question": question,
                             "table_info": schema,
                             "top_k": 10})
    print("Generated SQL Query:", response)
    
    try:
        query_result = db.run(response)
        print("Query Result:", query_result)
    except Exception as db_error:
        print(f"Database Error: {db_error}")
        
        try:
            result = SQLQueryChecker(response)
            print("LLM Feedback on query: \n", result)
            #lena we use ReAct prompting strategy 
            # lena 9aad bich naamel faza il initial prompt chenzidha il feedback mtaa il checker tool bich yaamel iteration okhra kinda 
        except Exception as Checker_error:
            raise RuntimeError(f"Failed to Check the sql query: {Checker_error}")
    
except Exception as chain_error:
    raise RuntimeError(f"Failed to generate SQL query: {chain_error}")




# check il sql bel tool jdida 
try:
    result = SQLQueryChecker(response) 
    print("LLM Feedback on query:\n", result)
except Exception as e:
    raise RuntimeError(f"Failed to check the generated query: {e}")



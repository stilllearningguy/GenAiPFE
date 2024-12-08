from sqlalchemy import create_engine, inspect

def get_database_schema(database_url: str) -> str:
    """
    Retrieve the schema of the database, including relationships between tables.

    Args:
        database_url (str): The connection string for the database.

    Returns:
        str: The database schema as a formatted string.
    """
    try:
        # Create a database engine
        engine = create_engine(database_url)
        inspector = inspect(engine)

        schema_output = []

        # Iterate over all tables
        for table_name in inspector.get_table_names():
            schema_output.append(f"Table: {table_name}")
            schema_output.append("=" * 40)

            # Get columns for each table
            columns = inspector.get_columns(table_name)
            for column in columns:
                column_name = column["name"]
                column_type = str(column["type"])
                nullable = "NULL" if column["nullable"] else "NOT NULL"
                schema_output.append(f"- {column_name} ({column_type}) {nullable}")

            # Get foreign key constraints
            foreign_keys = inspector.get_foreign_keys(table_name)
            if foreign_keys:
                schema_output.append("  Foreign Keys:")
                for fk in foreign_keys:
                    fk_column = ", ".join(fk["constrained_columns"])
                    referenced_table = fk["referred_table"]
                    referenced_columns = ", ".join(fk["referred_columns"])
                    schema_output.append(f"    - {fk_column} references {referenced_table}({referenced_columns})")

            schema_output.append("\n")  # Add a newline for separation

        return "\n".join(schema_output)

    except Exception as e:
        return f"An error occurred while retrieving the schema: {e}"


# Example Usage
if __name__ == "__main__":
    db_url = "sqlite:///D:/GenAiPFE/Chinook.db"  # Replace with your DB connection string
    schema = get_database_schema(db_url)
    print(schema)
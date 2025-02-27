from agno.agent import Agent
from agno.storage.agent.postgres import PostgresAgentStorage

db_url = "postgresql+psycopg2://aiagent:qwer1234@localhost:5532/aiagent"

# Create a storage backend using the Postgres database
storage = PostgresAgentStorage(
    # store sessions in the ai.sessions table
    table_name="agent_sessions",
    # db_url: Postgres database URL
    db_url=db_url,
)

# Add storage to the Agent
agent = Agent(storage=storage)
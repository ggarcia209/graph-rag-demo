from falkordb import FalkorDB
from src.config import settings

def get_graph_client():
    """
    Initializes and returns a FalkorDB client.
    """
    client = FalkorDB(
        host=settings.falkordb_host,
        port=settings.falkordb_port,
        password=settings.falkordb_password
    )
    # The Knowledge Graph Schema specified "GDELT Events × Equity Markets"
    # We will name our graph 'gdelt_markets'
    return client.select_graph("gdelt_markets")

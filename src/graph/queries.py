# Cypher queries for the FalkorDB schema
# As per knowledge_graph_schema.md

# Find an organization by name
FIND_ORG_QUERY = """
MATCH (o:Organization)
WHERE o.name = $org_name OR $org_name IN o.aliases
RETURN o
"""

# Extract subgraph of events affecting an organization and related markets
EVENT_IMPACT_SUBGRAPH_QUERY = """
MATCH (e:Event)-[r1:DISRUPTS_SUPPLY]->(c:Commodity)-[r2:PRICED_BY]->(m1:Market)
MATCH (c)<-[r3:CONSUMES|PRODUCES]-(o:Organization)-[r4:LISTED_AS]->(m2:Market)
WHERE e.id = $event_id AND o.id = $org_id
RETURN e, r1, c, r2, m1, r3, o, r4, m2
"""

# Find events near a certain geographic location
FIND_EVENTS_BY_REGION_QUERY = """
MATCH (e:Event)-[:OCCURRED_IN|AFFECTS_REGION]->(r:Region)
WHERE r.name = $region_name
RETURN e
"""

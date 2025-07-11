import datetime

def log_crm_heartbeat():
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{timestamp} CRM is alive\n"
    with open("/tmp/crm_heartbeat_log.txt", "a") as log_file:
        log_file.write(message)

    # Optional: Check GraphQL hello field
    try:
        from gql import gql, Client
        from gql.transport.requests import RequestsHTTPTransport
        transport = RequestsHTTPTransport(url="http://localhost:8000/graphql", verify=False)
        client = Client(transport=transport, fetch_schema_from_transport=True)
        query = gql("query { hello }")
        result = client.execute(query)
        if "hello" in result:
            with open("/tmp/crm_heartbeat_log.txt", "a") as log_file:
                log_file.write(f"{timestamp} GraphQL hello: {result['hello']}\n")
    except Exception as e:
        with open("/tmp/crm_heartbeat_log.txt", "a") as log_file:
            log_file.write(f"{timestamp} GraphQL hello check failed: {e}\n")

def update_low_stock():
    from gql import gql, Client
    from gql.transport.requests import RequestsHTTPTransport

    GRAPHQL_ENDPOINT = "http://localhost:8000/graphql"
    transport = RequestsHTTPTransport(url=GRAPHQL_ENDPOINT, verify=False)
    client = Client(transport=transport, fetch_schema_from_transport=True)

    mutation = gql("""
    mutation {
      updateLowStockProducts {
        updatedProducts {
          name
          stock
        }
        message
      }
    }
    """)

    result = client.execute(mutation)
    products = result.get("updateLowStockProducts", {}).get("updatedProducts", [])
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    with open("/tmp/low_stock_updates_log.txt", "a") as log_file:
        for prod in products:
            log_file.write(f"{timestamp} Restocked: {prod['name']} (Stock: {prod['stock']})\n")
        message = result.get("updateLowStockProducts", {}).get("message", "No message")
        log_file.write(f"{timestamp} Update message: {message}\n")
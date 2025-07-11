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
            log_file.write(f"{timestamp} GraphQL hello check
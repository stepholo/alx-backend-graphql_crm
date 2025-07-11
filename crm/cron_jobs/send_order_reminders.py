import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

GRAPHQL_ENDPOINT = "http://localhost:8000/graphql"

# Calculate date range for last 7 days
now = datetime.datetime.now()
seven_days_ago = now - datetime.timedelta(days=7)
date_from = seven_days_ago.strftime("%Y-%m-%dT%H:%M:%S")
date_to = now.strftime("%Y-%m-%dT%H:%M:%S")

query = gql("""
query GetRecentOrders($date_from: DateTime!, $date_to: DateTime!) {
  allOrders(orderDate_Gte: $date_from, orderDate_Lte: $date_to) {
    edges {
      node {
        id
        orderDate
        customer {
          email
        }
      }
    }
  }
}
""")

transport = RequestsHTTPTransport(url=GRAPHQL_ENDPOINT, verify=False)
client = Client(transport=transport, fetch_schema_from_transport=True)

params = {"date_from": date_from, "date_to": date_to}
result = client.execute(query, variable_values=params)

orders = result.get("allOrders", {}).get("edges", [])

with open("/tmp/order_reminders_log.txt", "a") as log_file:
    for edge in orders:
        node = edge["node"]
        order_id = node["id"]
        customer_email = node["customer"]["email"]
        timestamp = datetime.datetime.now().isoformat()
        log_file.write(f"{timestamp}: Reminder for Order {order_id} to {customer_email}\n")

print("Order reminders processed!")
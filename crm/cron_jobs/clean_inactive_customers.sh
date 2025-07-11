#!/bin/bash

# Get the current working directory
cwd="$(pwd)"

# Change to the script's directory
cd "$(dirname "${BASH_SOURCE[0]}")"

# Check if manage.py exists in the expected location
if [ ! -f "$cwd/../../manage.py" ]; then
    echo "manage.py not found in $cwd/../../"
    exit 1
else
    # Use Django’s manage.py shell to execute a Python command that deletes customers with no orders since a year ago.
    # Log the number of deleted customers to a /tmp/customer_cleanup_log.txt with a timestamp.
    python3 "$cwd/../../manage.py" shell <<EOF
from django.utils import timezone
from crm.models import Customer, Order
from datetime import timedelta

one_year_ago = timezone.now() - timedelta(days=365)
inactive_customers = Customer.objects.exclude(order__order_date__gte=one_year_ago)
count = inactive_customers.count()
inactive_customers.delete()

with open('/tmp/customer_cleanup_log.txt', 'a') as log_file:
    log_file.write(f"{timezone.now()}: Deleted {count} inactive customers\n")
EOF
fi
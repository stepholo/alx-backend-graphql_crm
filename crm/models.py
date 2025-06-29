from django.db import models


class Customer(models.Model):
    """Model representing a customer in the CRM system."""
    customer_id = models.AutoField(primary_key=True, editable=False)
    name = models.CharField(max_length=200, blank=False)
    email = models.EmailField(max_length=254, blank=False, unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=False)

    def __str__(self):
        """String representation of the Customer model."""
        return f"{self.name} {self.email}"


class Product(models.Model):
    """Model representing a product in the CRM system."""
    product_id = models.AutoField(primary_key=True, editable=False)
    name = models.CharField(max_length=254, blank=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=False)
    stock = models.PositiveIntegerField(default=0, blank=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=False)

    def __str__(self):
        """String representation of the Product model."""
        return f"{self.name} = ${self.price} {self.stock} in stock"""


class Order(models.Model):
    """Model representing an order in the CRM system."""
    order_id = models.AutoField(primary_key=True, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    products = models.ManyToManyField(Product, related_name='orders')
    totalAmount = models.DecimalField(max_digits=10, decimal_places=2, blank=False)
    order_date = models.DateTimeField(auto_now_add=True, blank=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=False)
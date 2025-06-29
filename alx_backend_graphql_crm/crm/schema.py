import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter
from django.utils import timezone
from graphql import GraphQLError
import re

# =====================
# Types
# =====================


class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("customer_id", "name", "email", "phone", "created_at")


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("product_id", "name", "price", "stock", "created_at")


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("order_id", "customer", "products", "totalAmount", "order_date")

# =====================
# Input Types
# =====================


class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()
    created_at = graphene.DateTime(required=False, default_value=timezone.now)


class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int(required=False, default_value=0)
    created_at = graphene.DateTime(required=False, default_value=timezone.now)


class OrderInput(graphene.InputObjectType):
    customer_id = graphene.Int(required=True)
    product_ids = graphene.List(graphene.Int, required=True)
    order_date = graphene.DateTime(required=False)

# =====================
# Mutations
# =====================


class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, input):
        if Customer.objects.filter(email=input.email).exists():
            raise GraphQLError("Email already exists.")

        if input.phone and not re.match(r'^\+?1?\d{9,15}$', input.phone):
            raise GraphQLError("Phone number must be in valid format.")

        customer = Customer.objects.create(
            name=input.name,
            email=input.email,
            phone=input.phone,
            created_at=input.created_at or timezone.now()
        )
        return CreateCustomer(customer=customer, message="Customer created successfully.")


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, root, info, input):
        created = []
        errors = []

        for idx, data in enumerate(input):
            if not data.name:
                errors.append(f"Entry {idx}: Name is required.")
                continue
            if not data.email:
                errors.append(f"Entry {idx}: Email is required.")
                continue
            if Customer.objects.filter(email=data.email).exists():
                errors.append(f"Entry {idx}: Email '{data.email}' already exists.")
                continue
            if data.phone and not re.match(r'^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$', data.phone):
                errors.append(f"Entry {idx}: Invalid phone format.")
                continue

            customer = Customer.objects.create(
                name=data.name,
                email=data.email,
                phone=data.phone,
                created_at=data.created_at or timezone.now()
            )
            created.append(customer)

        return BulkCreateCustomers(customers=created, errors=errors)


class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)

    @classmethod
    def mutate(cls, root, info, input):
        if input.price <= 0:
            raise GraphQLError("Price must be a positive number.")
        if input.stock is not None and input.stock < 0:
            raise GraphQLError("Stock cannot be negative.")

        product = Product.objects.create(
            name=input.name,
            price=input.price,
            stock=input.stock or 0,
            created_at=input.created_at or timezone.now()
        )
        return CreateProduct(product=product)


class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)

    @classmethod
    def mutate(cls, root, info, input):
        try:
            customer = Customer.objects.get(pk=input.customer_id)
        except Customer.DoesNotExist:
            raise GraphQLError("Invalid customer ID.")

        products = Product.objects.filter(pk__in=input.product_ids)
        if products.count() != len(input.product_ids):
            raise GraphQLError("One or more product IDs are invalid.")

        total = sum([p.price for p in products])
        order_date = input.order_date or timezone.now()

        order = Order.objects.create(
            customer=customer,
            totalAmount=total,
            order_date=order_date
        )
        order.product.set(products)

        return CreateOrder(order=order)

# =====================
# Query with Filtering and Ordering
# =====================

class CustomerNode(DjangoObjectType):
    class Meta:
        model = Customer
        filterset_class = CustomerFilter
        interfaces = (graphene.relay.Node,)

class ProductNode(DjangoObjectType):
    class Meta:
        model = Product
        filterset_class = ProductFilter
        interfaces = (graphene.relay.Node,)

class OrderNode(DjangoObjectType):
    class Meta:
        model = Order
        filterset_class = OrderFilter
        interfaces = (graphene.relay.Node,)

class Query(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType)

    # Relay-style filtered connections
    all_customers = DjangoFilterConnectionField(
        CustomerNode,
        order_by=graphene.List(graphene.String, description="Order by fields, e.g. ['name', '-created_at']")
    )
    all_products = DjangoFilterConnectionField(
        ProductNode,
        order_by=graphene.List(graphene.String, description="Order by fields, e.g. ['price', '-stock']")
    )
    all_orders = DjangoFilterConnectionField(
        OrderNode,
        order_by=graphene.List(graphene.String, description="Order by fields, e.g. ['-order_date']")
    )

    def resolve_customers(self, info):
        return Customer.objects.all()

    def resolve_products(self, info):
        return Product.objects.all()

    def resolve_orders(self, info):
        return Order.objects.all()

    def resolve_all_customers(self, info, order_by=None, **kwargs):
        qs = Customer.objects.all()
        if order_by:
            qs = qs.order_by(*order_by)
        return qs

    def resolve_all_products(self, info, order_by=None, **kwargs):
        qs = Product.objects.all()
        if order_by:
            qs = qs.order_by(*order_by)
        return qs

    def resolve_all_orders(self, info, order_by=None, **kwargs):
        qs = Order.objects.all()
        if order_by:
            qs = qs.order_by(*order_by)
        return qs


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)

import django_filters as filters
from .models import Customer, Product, Order


class CustomerFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")
    email = filters.CharFilter(field_name="email", lookup_expr="icontains")
    created_at__gte = filters.DateFilter(field_name="created_at", lookup_expr="gte")
    created_at__lte = filters.DateFilter(field_name="created_at", lookup_expr="lte")
    phone_pattern = filters.CharFilter(method="filter_phone_pattern")

    def filter_phone_pattern(self, queryset, name, value):
        # Example: value = "+1" will match phone numbers starting with +1
        return queryset.filter(phone__startswith=value)

    class Meta:
        model = Customer
        fields = ["name", "email", "phone_pattern"]


class ProductFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")
    price__gte = filters.NumberFilter(field_name="price", lookup_expr="gte")
    price__lte = filters.NumberFilter(field_name="price", lookup_expr="lte")
    stock = filters.NumberFilter(field_name="stock", lookup_expr="exact")
    stock__gte = filters.NumberFilter(field_name="stock", lookup_expr="gte")
    stock__lte = filters.NumberFilter(field_name="stock", lookup_expr="lte")
    stock__lt = filters.NumberFilter(field_name="stock", lookup_expr="lt")  # For low stock

    class Meta:
        model = Product
        fields = [
            "name",
            "price__gte", "price__lte",
            "stock", "stock__gte", "stock__lte", "stock__lt"
        ]


class OrderFilter(filters.FilterSet):
    total_amount__gte = filters.NumberFilter(field_name="totalAmount", lookup_expr="gte")
    total_amount__lte = filters.NumberFilter(field_name="totalAmount", lookup_expr="lte")
    order_date__gte = filters.DateFilter(field_name="order_date", lookup_expr="gte")
    order_date__lte = filters.DateFilter(field_name="order_date", lookup_expr="lte")
    customer_name = filters.CharFilter(field_name="customer__name", lookup_expr="icontains")
    product_name = filters.CharFilter(field_name="products__name", lookup_expr="icontains")
    product_id = filters.NumberFilter(method="filter_product_id")

    def filter_product_id(self, queryset, name, value):
        # Filters orders that include a specific product ID
        return queryset.filter(products__product_id=value)

    class Meta:
        model = Order
        fields = [
            "total_amount__gte", "total_amount__lte",
            "order_date__gte", "order_date__lte",
            "customer_name", "product_name", "product_id"
        ]

from django.http import JsonResponse
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, filters, status
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Product, OrderItem
from .serializers import CategorySerializer, ProductSerializer
from .utils import search_products


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(
            {
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "count": self.page.paginator.count,
                "total_pages": self.page.paginator.num_pages,
                "results": data,
            }
        )


class ProductListByCategory(generics.ListAPIView):
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["category"]
    search_fields = ["name", "description"]
    pagination_class = CustomPagination

    def get_queryset(self):
        category_id = self.kwargs["category_id"]
        return Product.objects.filter(category_id=category_id)


class CategoryList(generics.ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()


class ProductList(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "description"]

    def get_queryset(self):
        search_query = self.request.query_params.get("search", None)

        if search_query:
            return Product.objects.filter(
                Q(name__icontains=search_query) | Q(description__icontains=search_query)
            )

        return Product.objects.all()


def product_search(request):
    query = request.GET.get("query", "")
    results = search_products(query)
    serialized_results = [
        {"name": product.name, "description": product.description}
        for product in results
    ]

    return JsonResponse({"results": serialized_results})


class ShoppingCartView(APIView):
    def get_cart(self, request):
        cart = request.session.get("cart", [])

        cart_details = []
        total_price = 0

        for item in cart:
            product = get_object_or_404(Product, pk=item["product_id"])
            quantity = item["quantity"]
            item_total = product.price * quantity
            total_price += item_total

            cart_details.append(
                {
                    "product": ProductSerializer(product).data,
                    "quantity": quantity,
                    "item_total": item_total,
                }
            )

        return cart_details, total_price

    def get(self, request):
        cart_details, total_price = self.get_cart(request)
        return Response({"cart_items": cart_details, "total_price": total_price})

    def post(self, request):
        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))

        product = get_object_or_404(Product, pk=product_id)

        cart = request.session.get("cart", [])

        for item in cart:
            if item["product_id"] == product_id:
                item["quantity"] += quantity
                request.session.modified = True
                cart_details, total_price = self.get_cart(request)
                return Response(
                    {"cart_items": cart_details, "total_price": total_price}
                )

        cart.append({"product_id": product_id, "quantity": quantity})
        request.session["cart"] = cart
        request.session.modified = True

        cart_details, total_price = self.get_cart(request)
        return Response({"cart_items": cart_details, "total_price": total_price})

    def delete(self, request):
        product_id = request.data.get("product_id")

        cart = request.session.get("cart", [])

        for item in cart:
            if item["product_id"] == product_id:
                cart.remove(item)
                request.session.modified = True
                cart_details, total_price = self.get_cart(request)
                return Response(
                    {"cart_items": cart_details, "total_price": total_price}
                )

        return Response(status=status.HTTP_404_NOT_FOUND)

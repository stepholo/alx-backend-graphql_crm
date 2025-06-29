import graphene
from crm.schema import Query as CRMQuery, Mutation as CRMmutation


class Query(CRMQuery, graphene.ObjectType):
    """Root query for the GraphQL schema."

    hello = graphene.String(description="A simple hello world query.")

    def resolve_hello(self, info):
        "Resolve the hello query to return a greeting."
        return "Hello, GraphQL!"""
    pass


class Mutation(CRMmutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)

from rest_framework.authentication import TokenAuthentication


# The subclass.
class BearerAuthentication(TokenAuthentication):
    # Ste the keyword as "bearer".
    keyword = 'Bearer'

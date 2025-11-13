from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'auth': {
            'login': reverse('token_obtain_pair', request=request, format=format),
            'refresh': reverse('token_refresh', request=request, format=format),
            'verify': reverse('token_verify', request=request, format=format),
            'user': reverse('user-detail', request=request, format=format, kwargs={'pk': 'me'}),
        },
        'docs': {
            'swagger': reverse('schema-swagger-ui', request=request, format=format),
            'redoc': reverse('schema-redoc', request=request, format=format),
        },
        # Add more endpoints here as you implement them
    })

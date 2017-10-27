import os
import datetime
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from rest_framework.generics import CreateAPIView
from rest_framework.serializers import ModelSerializer
from img.models import Token


class TokenSerializer(ModelSerializer):
    class Meta:
        model = Token
        fields = []

    @property
    def data(self):
        super_data = super(TokenSerializer, self).data
        super_data['token'] = getattr(self.instance, 'token', None)
        return super_data


class CreateToken(CreateAPIView):
    serializer_class = TokenSerializer


@csrf_exempt
def image_upload(request, token):
    img = request.FILES.get('image')
    if not img:
        return JsonResponse({'success': False,
                             'detail': 'Image not provided'})
    timestamp = str(datetime.datetime.now()).\
        replace(' ', '_').replace(':', '_').replace('.', '_') + '__'
    path = os.path.join(settings.MEDIA_ROOT, token, timestamp+img._name)
    try:
        os.makedirs(os.path.join(settings.MEDIA_ROOT, token))
    except OSError:
        pass
    with open(path, 'wb+') as destination:
        destination.write(img.file.read())
    return JsonResponse({'success': True, 'url': '/'.join([
        '/media', token, timestamp+img._name])})


def get_images(request, token):
    path = os.path.join(settings.MEDIA_ROOT, token)
    try:
        Token.objects.get(token=token)
    except Token.DoesNotExist:
        return JsonResponse({
            'success': False,
            'details': 'Token %s does not exist' % token
        })
    if not os.path.isdir(path):
        return JsonResponse({'images': [], 'success': True})
    files = os.walk(path).next()[2]
    return JsonResponse({'success': True, 'images': [
        '/media/%s/%s' % (token, i) for i in files
    ]})

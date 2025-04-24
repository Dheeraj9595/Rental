from rest_framework import serializers
from user.models import Cloth

class ClothSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cloth
        fields = '__all__'
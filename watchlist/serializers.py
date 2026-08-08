from rest_framework import serializers
from .models import WatchlistItem


class WatchlistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = WatchlistItem
        fields = '__all__'
        read_only_fields = ('user', 'added_at', 'updated_at')

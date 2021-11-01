from rest_framework import serializers

from tickets.models import Ticket


class TicketSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True, source='author.username')

    class Meta:
        model = Ticket
        fields = '__all__'

from rest_framework import serializers

from tickets.models import Ticket


class TicketSerializer(serializers.HyperlinkedModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True,
                                                source='author.username')

    class Meta:
        model = Ticket
        fields = '__all__'

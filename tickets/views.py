from typing import Union

from rest_framework import viewsets, status
from rest_framework.response import Response

from tickets.models import Ticket
from tickets.serializers import TicketSerializer

EDITABLE_FOR_STAFF = ('is_completed', 'is_frozen')
EDITABLE_FOR_CLIENT = ('body',)
NOT_ALLOWED_FIELD_MESSAGE = f'you don\'t have permission to change fields'


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    def get_queryset(self):
        """Return all tickets to the staff and
        only his tickets to the user"""

        user = self.request.user
        queryset = super().get_queryset()
        if user.is_staff:
            return queryset
        return queryset.filter(author=user)

    def perform_create(self, serializer):
        """Set author automatically"""

        serializer.save(author=self.request.user)

    def update(self, request, *args, **kwargs):
        user = self.request.user
        instance = self.get_object()

        if user.is_staff:
            response = _check_allowed_fields(request,
                                             EDITABLE_FOR_STAFF)
            if response is not None:
                return response
            data = _get_data_for_staff(request, instance)

        else:
            response = _check_allowed_fields(request,
                                             EDITABLE_FOR_CLIENT)
            if response is not None:
                return response
            data = _get_data_for_client(request, instance)

        serializer = self._update_ticket(instance, data)
        return Response(serializer.data)

    def _update_ticket(self, instance, data):
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return serializer


def _check_allowed_fields(request, allowed_fields):
    """Checks that no fields were passed that cannot be
    changed by user."""

    not_allowed_fields = list(set(request.data.keys() -
                                  set(allowed_fields)))

    if not_allowed_fields:
        message = NOT_ALLOWED_FIELD_MESSAGE + str(not_allowed_fields)
        return Response({'error': message},
                        status=status.HTTP_400_BAD_REQUEST)


def _get_data_for_staff(request, instance):
    """Return data for update ticket by staff."""
    data = {}
    for item in EDITABLE_FOR_STAFF:
        data[item] = request.data.get(item, instance.__dict__[item])

    return data


def _get_data_for_client(request, instance):
    """Return data for update ticket by owner."""
    data = {}
    for item in EDITABLE_FOR_CLIENT:
        data[item] = request.data.get(item, instance.__dict__[item])
    return data

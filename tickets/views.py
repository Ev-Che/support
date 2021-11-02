from typing import Union

from rest_framework import viewsets, status
from rest_framework.response import Response

from tickets.models import Ticket
from tickets.serializers import TicketSerializer

EDITABLE_FOR_STAFF = ('is_completed', 'is_frozen')
EDITABLE_FOR_CLIENT = ('body',)
NOT_ALLOWED_FIELD_MESSAGE = 'you don\'t have permission to change field(s)'


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    def get_queryset(self) -> queryset:
        """Return all tickets to the staff and
        only his tickets to the user"""
        user = self.request.user
        queryset = super().get_queryset()
        if user.is_staff:
            return queryset
        return queryset.filter(author=user)

    def perform_create(self, serializer: serializer_class) -> None:
        """Set author automatically"""
        serializer.save(author=self.request.user)

    def update(self, request, *args, **kwargs) -> Union[None, Response]:
        instance = self.get_object()
        data = self._get_data(request, instance)

        if data is None:
            message = NOT_ALLOWED_FIELD_MESSAGE
            return Response({'error': message},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self._update_ticket(instance, data)
        return Response(serializer.data)

    def _get_data(self, request, instance) -> Union[None, dict]:
        """Returns dict with field to be edited or
        None if user has not permission to change some
        field."""
        user = self.request.user
        data = None

        if user.is_staff:
            if self._all_fields_allowed(request, EDITABLE_FOR_STAFF):
                data = self._get_data_for_staff(request, instance)
        else:
            if self._all_fields_allowed(request, EDITABLE_FOR_CLIENT):
                data = self._get_data_for_client(request, instance)
        return data

    def _update_ticket(self, instance, data) -> serializer_class:
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return serializer

    def _all_fields_allowed(self, request, allowed_fields: tuple) -> bool:
        """Checks that no fields were passed that cannot be
        changed by user."""
        return not bool(set(request.data.keys() - set(allowed_fields)))

    def _get_data_for_staff(self, request, instance) -> dict:
        """Return data for update ticket by staff."""
        data = {}
        for item in EDITABLE_FOR_STAFF:
            data[item] = request.data.get(item, instance.__dict__[item])

        return data

    def _get_data_for_client(self, request, instance) -> dict:
        """Return data for update ticket by owner."""
        data = {}
        for item in EDITABLE_FOR_CLIENT:
            data[item] = request.data.get(item, instance.__dict__[item])
        return data

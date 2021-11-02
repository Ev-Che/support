import json

import pytest
from django.contrib.auth.models import User
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIRequestFactory, force_authenticate

from tickets.models import Ticket
from tickets.views import TicketViewSet, NOT_ALLOWED_FIELD_MESSAGE


@pytest.mark.django_db
class TestUpdateTicket:

    def test_client_updates_his_ticket_updated(self):
        user = self._get_user('test')
        ticket = self._get_ticket()
        new_body = "updated body"
        data = {'body': new_body}
        factory = APIRequestFactory()
        ticket_update = TicketViewSet.as_view(actions={"put": "update"})

        request = factory.put(f'/tickets/{ticket.id}/',
                              data=json.dumps(data),
                              content_type="application/json")
        force_authenticate(request, user=user)
        ticket_update(request, pk=ticket.pk)

        assert new_body == self._get_ticket().body

    def test_client_tries_to_update_not_his_ticket_not_found(self):
        user = self._get_user('test2')
        ticket = self._get_ticket()
        old_body = ticket.body
        new_body = "updated body"
        data = {'body': new_body}
        factory = APIRequestFactory()
        ticket_update = TicketViewSet.as_view(actions={"put": "update"})

        request = factory.put(f'/tickets/{ticket.id}/',
                              data=json.dumps(data),
                              content_type="application/json")
        force_authenticate(request, user=user)
        response = ticket_update(request, pk=ticket.pk)

        assert isinstance(response.data['detail'], ErrorDetail)
        assert response.data['detail'].code == 'not_found'
        assert old_body == self._get_ticket().body

    def test_client_tries_to_update_not_allowed_field_error_message(self):
        user = self._get_user('test')
        ticket = self._get_ticket()
        new_is_completed = True
        old_is_completed = ticket.is_completed
        data = {'is_completed': new_is_completed}
        factory = APIRequestFactory()
        ticket_update = TicketViewSet.as_view(actions={"put": "update"})

        request = factory.put(f'/tickets/{ticket.id}/',
                              data=json.dumps(data),
                              content_type="application/json")
        force_authenticate(request, user=user)
        response = ticket_update(request, pk=ticket.pk)

        assert response.data['error'] == NOT_ALLOWED_FIELD_MESSAGE
        assert old_is_completed == self._get_ticket().is_completed

    def test_staff_update_field_updated(self):
        user = self._get_user('staff')
        ticket = self._get_ticket()
        new_is_completed = True
        data = {'is_completed': new_is_completed}
        factory = APIRequestFactory()
        ticket_update = TicketViewSet.as_view(actions={"put": "update"})

        request = factory.put(f'/tickets/{ticket.id}/',
                              data=json.dumps(data),
                              content_type="application/json")
        force_authenticate(request, user=user)
        ticket_update(request, pk=ticket.pk)

        assert new_is_completed == self._get_ticket().is_completed

    def test_staff_tries_to_update_not_allowed_field_error_message(self):
        user = self._get_user('staff')
        ticket = self._get_ticket()
        old_body = ticket.body
        new_body = "updated body"
        data = {'body': new_body}
        factory = APIRequestFactory()
        ticket_update = TicketViewSet.as_view(actions={"put": "update"})

        request = factory.put(f'/tickets/{ticket.id}/',
                              data=json.dumps(data),
                              content_type="application/json")
        force_authenticate(request, user=user)
        response = ticket_update(request, pk=ticket.pk)

        assert response.data['error'] == NOT_ALLOWED_FIELD_MESSAGE
        assert old_body == self._get_ticket().body

    @staticmethod
    def _get_user(username):
        return User.objects.get(username=username)

    @staticmethod
    def _get_ticket():
        return Ticket.objects.first()

    @pytest.fixture(autouse=True)
    def populate_db(self):
        user1 = self._create_user('test', 'test', False)
        user2 = self._create_user('test2', 'test2', False)
        staff = self._create_user('staff', 'staff', True)
        ticket = self._create_ticket('test ticket', user1)
        yield
        user1.delete()
        user2.delete()
        staff.delete()
        ticket.delete()

    @staticmethod
    def _create_user(username, password, is_staff):
        return User.objects.create(username=username, password=password,
                                   is_staff=is_staff)

    @staticmethod
    def _create_ticket(body, user):
        return Ticket.objects.create(body=body, author=user)

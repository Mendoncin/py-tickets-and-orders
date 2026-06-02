from datetime import datetime

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import QuerySet
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from db.models import MovieSession, Order, Ticket


User = get_user_model()


def _prepare_date(date: str | datetime) -> datetime:
    if isinstance(date, datetime):
        parsed_date = date
    else:
        parsed_date = parse_datetime(date)

        if parsed_date is None:
            parsed_date = datetime.strptime(date, "%Y-%m-%d %H:%M")

    if timezone.is_naive(parsed_date):
        parsed_date = timezone.make_aware(parsed_date)

    return parsed_date


@transaction.atomic
def create_order(
    tickets: list[dict],
    username: str,
    date: str | datetime = None,
) -> Order:
    user = User.objects.get(username=username)

    order = Order.objects.create(user=user)

    if date is not None:
        order.created_at = _prepare_date(date)
        order.save(update_fields=["created_at"])

    for ticket_data in tickets:
        movie_session = MovieSession.objects.get(
            id=ticket_data["movie_session"]
        )

        Ticket.objects.create(
            row=ticket_data["row"],
            seat=ticket_data["seat"],
            movie_session=movie_session,
            order=order,
        )

    return order


def get_orders(username: str = None) -> QuerySet:
    queryset = Order.objects.all()

    if username is not None:
        queryset = queryset.filter(user__username=username)

    return queryset
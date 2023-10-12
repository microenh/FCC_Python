"define event data"
from enum import Enum, auto


class TicketType(Enum):
    "type of event"
    STATUS = auto()
    PROGRESS = auto()
    DONE = auto()
    RESULT = auto()


class Ticket():
    "class of event data"

    def __init__(self, ticket_type, value):
        self.ticket_type = ticket_type
        self.value = value

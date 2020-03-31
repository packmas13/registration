from django import template
from django.template.defaultfilters import stringfilter

from ..models.participant import Participant

register = template.Library()


@register.filter
@stringfilter
def section_color(value):
    if value == Participant.SECTION_BEAVER:
        return "gray-600"
    elif value == Participant.SECTION_CUB:
        return "orange-600"
    elif value == Participant.SECTION_SCOUT:
        return "blue-600"
    elif value == Participant.SECTION_VENTURER:
        return "green-600"
    elif value == Participant.SECTION_ROVER:
        return "red-600"
    return "purple-600"


@register.filter
@stringfilter
def section_color_hex(value):
    if value == Participant.SECTION_BEAVER:
        return "#718096"
    elif value == Participant.SECTION_CUB:
        return "#dd6b20"
    elif value == Participant.SECTION_SCOUT:
        return "#3182ce"
    elif value == Participant.SECTION_VENTURER:
        return "#38a169"
    elif value == Participant.SECTION_ROVER:
        return "#e53e3e"
    return "#805ad5"

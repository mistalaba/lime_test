from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from scheduler.utils import show_available_slots


@api_view()
@permission_classes((permissions.AllowAny,))
def available_timeslots(request):
    """
    Required query params:
    participant (for example: ?participant=id1&participant=id2), start (as ISO), end (as ISO),
    Optional query params (with defaults):
    tz='UTC', duration=30 (in minutes), office_hours=[8, 17]
    """
    # Check that mandatory query params are here
    mandatory_keys = ['participant', 'start', 'end']
    optional_keys = ['tz', 'duration', 'office_hours']
    if all (key in request.query_params for key in mandatory_keys):
        participant_list = request.query_params['participant']
        earliest_datetime = request.query_params['start']
        latest_datetime = request.query_params['end']
    else:
        return Response({"status": "not found."}, status=status.HTTP_404_NOT_FOUND)

    timeslots = show_available_slots(participant_list, earliest_datetime, latest_datetime)

import csv
import logging
from dateutil import parser
import pytz
from datetime import datetime, timedelta

from .models import Participant, Schedule

logger = logging.getLogger(__name__)



def str_to_datetime(input):
    try:
        # Make string to datetime object
        dt = parser.parse(input)
        # Make aware
        dt = pytz.utc.localize(dt)
        return dt
    except:
        raise


def overlapping_dateranges(range1, range2):
    """
    Returns True if ranges overlap.
    Taken from http://wiki.c2.com/?TestIfDateRangesOverlap
    Exception: You can apparently go from one meeting to another in 0 minutes
    """
    # return (range1[0] <= range2[1] and range2[0] <= range1[1])
    return (range1[0] < range2[1] and range2[0] < range1[1])


def csv_import(file_obj):
    with open(file_obj, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')

        # Get participants
        for row in reader:
            # Participant with id is always len(row) == 2
            if len(row) == 2:
                # Add participant to database
                participant_id = row[0]
                val = row[1]
                particiant, created = Participant.objects.get_or_create(participant_id=participant_id, defaults={'name': val})
                if not created:
                    logger.debug("Participant '{}' not created, '{}' found on row {}.".format(val, particiant, reader.line_num))


        # Get data
        csvfile.seek(0)
        participant = None
        for row in reader:
            if len(row) > 2:
                try:
                    participant_id = str(row[0])
                    # Locate participant
                    participant = Participant.objects.filter(participant_id=participant_id).first()
                    # logger.debug("{}: {}".format(participant_id, participant))
                    if participant is None:
                        logger.warning("{} on line {} could not be found.".format(participant_id, reader.line_num))
                        raise Exception
                except IndexError:
                    # Skip conversion
                    continue
                # Add meeting
                try:
                    meeting_start = str_to_datetime(row[1])
                    meeting_end = str_to_datetime(row[2])
                    meeting, created = Schedule.objects.get_or_create(
                        meeting_notes=row[3], defaults={'participant': participant, 'start': meeting_start, 'end': meeting_end}
                    )
                    if created:
                        # logger.debug("Meeting {} for {} created.".format(meeting, particiant))
                        pass
                    else:
                        # logger.debug("Meeting {} exist.".format(row[3][:20]))
                        pass
                except IndexError:
                    raise


def duplicates(file_obj):
    """
    Sanity check to see if there's any duplicate meetings
    """
    with open(file_obj, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        meetings = []
        for row in reader:
            if len(row) > 2:
                # logger.debug("Meeting: {}".format(row[3]))
                # It's a meeting
                # Find meeting, otherwise add it
                idx = next((i for (i, res) in enumerate(meetings) if res['meeting'] == row[3]), None)
                if idx:
                    meetings[idx]['times'] += 1
                else:
                    meetings.append({'meeting': row[3], 'times': 1})
    for meeting in meetings:
        if meeting['times'] > 1:
            print(meeting)


def merge_dateranges(range1, range2):
    if overlapping_dateranges(range1, range2):
        return (min(range1[0], range2[0]), max(range1[1], range2[1]))


# tmp_range = [
#     (datetime(2015, 2, 5, 9, 0), datetime(2015, 2, 5, 12, 0)),
#     (datetime(2015, 2, 5, 12, 30), datetime(2015, 2, 5, 14, 0)),
#     (datetime(2015, 2, 5, 14, 30), datetime(2015, 2, 5, 16, 0)),
# ]
def merge_unavailable_ranges(rng):
    """
    Takes the list of unavailable ranges and merges them. This is used if there's
    multiple participants with overlapping meetings.
    """
    for i, r in enumerate(rng):
        try:
            if overlapping_dateranges(r, rng[i+1]):
                rng[i] = merge_dateranges(r, rng[i+1])
                rng.pop(i+1)
                try:
                    merge_unavailable_ranges(rng)
                except IndexError:
                    pass
        except IndexError:
            pass
    return rng


def show_available_slots(participant_list, earliest_datetime, latest_datetime, tz='UTC', duration=30, office_hours=[8, 17]):
    """
    participants_list: ['id1', 'id2', 'id3']
    earliest_datetime = '2015-01-01 08:00'
    latest_datetime = '2015-01-01 17:00'
    tz: xxx
    duration=30 (minutes)
    office_hours=[8, 17] (start/end hour of office hours)

    Return time slots between earliest and latest where all participants can attend the meeting, half hour intervals.
    """
    from_dt = str_to_datetime(earliest_datetime)
    to_dt = str_to_datetime(latest_datetime)
    duration_td = timedelta(minutes=duration)

    time_slots = []
    slot_start = from_dt

    # Get range between earliest_datetime, latest_datetime
    available_range = [from_dt, to_dt - duration_td]

    # Remove unavailable ranges
    meetings = Schedule.objects.filter(participant__participant_id__in=participant_list).filter(end__gte=available_range[0], start__lte=available_range[1]).order_by('start')
    unavailable_ranges = [(m.start, m.end) for m in meetings]

    # Add office hours
    office_hour_ranges = []
    start_date = from_dt
    while start_date.date() <= to_dt.date():
        current_day = start_date
        office_hour_ranges.append(
            (current_day.replace(hour=0, minute=0), current_day.replace(hour=office_hours[0], minute=0)))
        office_hour_ranges.append(
            (current_day.replace(hour=office_hours[1], minute=0), current_day.replace(hour=0, minute=0) + timedelta(days=1)))
        start_date += timedelta(days=1)
    unavailable_ranges.extend(office_hour_ranges)
    unavailable_ranges.sort()

    # Merge overlapping meetings
    unavailable_ranges = merge_unavailable_ranges(unavailable_ranges)

    # Get list of available ranges from available range - unavailable_ranges
    # IE [(s,e), (s,e)...]
    # Create new list, available_ranges
    available_ranges = []
    start_range = from_dt
    end_range = to_dt
    for rr in unavailable_ranges:
        current_range = (start_range, rr[0])
        available_ranges.append(current_range)
        start_range = rr[1]
        if start_range > end_range:
            break
    # Last part
    if start_range < end_range:
        available_ranges.append((start_range, end_range))


    # Return slots that are available
    # Take every available range and get the slots from them
    available_slots = []
    for ar in available_ranges:
        current_slot = (ar[0], ar[0] + duration_td)
        while current_slot[1] <= ar[1]:
            available_slots.append(current_slot)
            current_slot = (current_slot[1], current_slot[1] + duration_td)

    logger.debug("unavailable_ranges: {}".format(unavailable_ranges))
    logger.debug("available_ranges: {}".format(available_ranges))
    return available_slots

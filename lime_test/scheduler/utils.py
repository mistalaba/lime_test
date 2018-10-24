import csv
import logging
from dateutil import parser
import pytz

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

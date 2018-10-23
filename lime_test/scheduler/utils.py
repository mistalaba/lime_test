import csv
import logging

logger = logging.getLogger(__name__)

from .models import Particiant

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
                particiant, created = Particiant.objects.get_or_create(participant_id=participant_id, defaults={'name': val})
                if not created:
                    logger.debug("Participant '{}' not created, '{}' found on row {}.".format(val, particiant, reader.line_num))


        # Get data
        csvfile.seek(0)
        for row in reader:
            if len(row) != 2:
                try:
                    participant_id = row[0]
                except IndexError:
                    participant_id = None
                    logger.debug("participant_id == None")
                try:
                    val = row[1]
                except IndexError:
                    val = None
                    logger.debug("val == None, row {}".format(reader.line_num))
                # print(participant_id, val)

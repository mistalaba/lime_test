from django.db import models


class Participant(models.Model):
    class Meta:
        indexes = [models.Index(fields=['participant_id', 'name'])]

    participant_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Schedule(models.Model):
    class Meta:
        indexes = [models.Index(fields=['meeting_notes'])]

    participant = models.ForeignKey('Participant', on_delete=models.CASCADE)
    start = models.DateTimeField()
    end = models.DateTimeField()
    meeting_notes = models.CharField(max_length=512)

    def __str__(self):
        return self.meeting_notes

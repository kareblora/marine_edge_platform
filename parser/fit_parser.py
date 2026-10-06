import logging
from fitparse import FitFile

logger = logging.getLogger("GarminFitParser")

class GarminFitParser:

    def __init__(self, filename):
        self.filename = filename

        try:
            self.fitfile = FitFile(str(filename))

        except Exception as error:
            logger.error(
                "Failed to load FIT file %s: %s",
                self.filename,
                error
            )
            raise

    def get_records(self):
        records = []

        for message in self.fitfile.get_messages("record"):
            record = {}

            for field in message:
                record[field.name] = field.value

            records.append(record)

        return records

    def get_messages(self, message_type):
        messages = []

        for message in self.fitfile.get_messages(message_type):

            data = {}

            for field in message:
                data[field.name] = field.value

            messages.append(data)

        return messages

    def get_session(self):
        messages = self.get_messages("session")

        return messages[0] if messages else {}

    def get_dive_summary(self):
        return self.get_messages("dive_summary")

    def get_dive_settings(self):
        messages = self.get_messages("dive_settings")

        return messages[0] if messages else {}

    def get_dive_gas(self):
        return self.get_messages("dive_gas")

    def get_events(self):
        return self.get_messages("event")
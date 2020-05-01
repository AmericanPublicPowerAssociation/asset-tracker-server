class RecordIdMirror(object):

    def __init__(self):
        self.record_id_by_temporary_id = {}

    def get(self, record_id):
        record_id = str(record_id)
        return self.record_id_by_temporary_id.get(record_id, record_id)

    def set(self, temporary_id, record_id):
        temporary_id = str(temporary_id)
        record_id = str(record_id)
        self.record_id_by_temporary_id[temporary_id] = record_id
        return record_id

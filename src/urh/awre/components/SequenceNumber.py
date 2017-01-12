from urh.awre.components.Component import Component

class SequenceNumber(Component):
    def __init__(self, fieldtypes, priority=2, predecessors=None, enabled=True, backend=None):
        """

        :type fieldtypes: list of FieldType
        :param priority:
        :param predecessors:
        :param enabled:
        :param backend:
        :param messagetypes:
        """
        super().__init__(priority, predecessors, enabled, backend)

        self.seqnr_field_type = next((ft for ft in fieldtypes if ft.function == ft.Function.SEQUENCE_NUMBER), None)
        self.seqnr_field_name = self.seqnr_field_type.caption if self.seqnr_field_type else "Sequence Number"


    def _py_find_field(self, messages):
        raise NotImplementedError("Todo")
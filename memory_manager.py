class ConversationalMemory:
    def __init__(self):
        self.last_question = None
        self.last_document = None

    def update(self, question, document_filename):
        self.last_question = question
        self.last_document = document_filename

    def get_last_document(self):
        return self.last_document

    def has_context(self):
        return self.last_document is not None

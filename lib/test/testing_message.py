class Manual_Testing_Message:
    """A class that mimics a PRAW message class."""
    body = ""
    author = ""
    result = ""

    def __init__(self, body):
        self.body = body
        self.author = "testing class"
        self.result = ""

    def mark_read(self):
        return True

    def reply(self, reply):
        self.result = reply
        print ("result: \n" + str(self.result))
        return True

    def get_result(self):
        return self.result

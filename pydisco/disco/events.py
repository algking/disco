import os, re, sys
from datetime import datetime

class Event(object):
    type             = 'EV'
    tag_re           = re.compile(r'^\w+$')
    timestamp_format = '%y/%m/%d %H:%M:%S'

    def __init__(self, message, tags=()):
        self.message = message
        self.tags    = tags
        self.time    = datetime.now()
        self.log()

    @property
    def timestamp(self):
        return self.time.strftime(self.timestamp_format)

    def log(self):
        sys.stderr.write('%s\n' % self)

    def __str__(self):
        tags = ' '.join(tag for tag in self.tags if self.tag_re.match(tag))
        return '**<%s><%s>[%s] %s' % (self.type, self.timestamp, tags, self.message)

class Message(Event):
    type = 'MSG'

class Signal(Event):
    pass

class DataUnavailable(Signal):
    type = 'DAT'

class EndOfJob(Signal):
    type = 'END'

class OutputURL(Signal):
    type = 'OUT'

class OOBData(Signal):
    type = 'OOB'

    def __init__(self, key, task):
        self.key  = key
        self.task = task
        super(OOBData, self).__init__('%s %s' % (key, os.path.join(task.home, 'oob', key)))

class EventRecord(object):
    type_raw      = r'\*\*<(?P<type>\w+)>'
    timestamp_raw = r'<(?P<timestamp>.+?)>'
    tags_raw      = r'\[(?P<tags>.*?)\]'
    message_raw   = r'(?P<message>.*)'
    event_re = re.compile(r'^%s%s%s %s$' % (type_raw, timestamp_raw, tags_raw, message_raw),
                          re.MULTILINE | re.S)

    def __init__(self, string):
        match = self.event_re.match(string)
        if not match:
            raise TypeError("%s is not in Event format" % string)
        self.type    = match.group('type')
        self.time    = datetime.strptime(match.group('timestamp'), Event.timestamp_format)
        self.tags    = match.group('tags').split()
        self.message = match.group('message')
import pyinotify
import signals

class CreateSignaler(pyinotify.ProcessEvent):
    """
    Simple class which only signals on create events.
    """
    def process_IN_CREATE(self, event):
        signals.in_create.send(sender=self, event=event)

class AllEventsSignaler(pyinotify.ProcessEvent):
    """
    Simple class which signals on every event.
    """
    def process_IN_ACCESS(self, event):
        signals.in_access.send(sender=self, event=event)

    def process_IN_ATTRIB(self, event):
        signals.in_attrib.send(sender=self, event=event)

    def process_IN_CLOSE_NOWRITE(self, event):
        signals.in_close_nowrite.send(sender=self, event=event)

    def process_IN_CLOSE_WRITE(self, event):
        signals.in_close_write.send(sender=self, event=event)

    def process_IN_CREATE(self, event):
        signals.in_create.send(sender=self, event=event)

    def process_IN_DELETE(self, event):
        signals.in_delete.send(sender=self, event=event)

    def process_IN_DELETE_SELF(self, event):
        signals.in_delete_self.send(sender=self, event=event)

    def process_IN_IGNORED(self, event):
        signals.in_ignored.send(sender=self, event=event)

    def process_IN_MODIFY(self, event):
        signals.in_modify.send(sender=self, event=event)

    def process_IN_MOVE_SELF(self, event):
        signals.in_move_self.send(sender=self, event=event)

    def process_IN_MOVED_FROM(self, event):
        signals.in_moved_from.send(sender=self, event=event)

    def process_IN_MOVED_TO(self, event):
        signals.in_moved_to.send(sender=self, event=event)

    def process_IN_OPEN(self, event):
        signals.in_open.send(sender=self, event=event)

    def process_IN_Q_OVERFLOW(self, event):
        signals.in_q_overflow.send(sender=self, event=event)

    def process_IN_UNMOUNT(self, event):
        signals.in_unmount.send(sender=self, event=event)

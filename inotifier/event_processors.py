import pyinotify
import signals


class AllEventsPrinter(pyinotify.ProcessEvent):
    """
    Simple class which prints on every event.
    """
    def process_IN_ACCESS(self, event):
        print "IN ACCESS: %s" % event.pathname

    def process_IN_ATTRIB(self, event):
        print "IN ATTRIB: %s" % event.pathname

    def process_IN_CLOSE_NOWRITE(self, event):
        print "IN CLOSE NOWRITE: %s" % event.pathname

    def process_IN_CLOSE_WRITE(self, event):
        print "IN CLOSE WRITE: %s" % event.pathname

    def process_IN_CREATE(self, event):
        print "IN CREATE: %s" % event.pathname

    def process_IN_DELETE(self, event):
        print "IN DELETE: %s" % event.pathname

    def process_IN_DELETE_SELF(self, event):
        print "IN DELETE SELF: %s" % event.pathname

    def process_IN_IGNORED(self, event):
        print "IN IGNORED: %s" % event.pathname

    def process_IN_MODIFY(self, event):
        print "IN MODIFY: %s" % event.pathname

    def process_IN_MOVE_SELF(self, event):
        print "IN MOVE SELF: %s" % event.pathname

    def process_IN_MOVED_FROM(self, event):
        print "IN MOVED FROM: %s" % event.pathname

    def process_IN_MOVED_TO(self, event):
        print "IN MOVED TO: %s" % event.pathname

    def process_IN_OPEN(self, event):
        print "IN OPEN: %s" % event.pathname

    def process_IN_Q_OVERFLOW(self, event):
        print "IN Q OVERFLOW: %s" % event.pathname

    def process_IN_UNMOUNT(self, event):
        print "IN UNMOUNT: %s" % event.pathname


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


class CreateSignaler(pyinotify.ProcessEvent):
    """
    Simple class which only signals on create events.
    """
    def process_IN_CREATE(self, event):
        signals.in_create.send(sender=self, event=event)


class CreateViaChunksSignaler(pyinotify.ProcessEvent):
    """
    A class which will signal the in_create event after a specific set of
    events has occurred for a file.  A file transfer agent may write partial
    chunks of a file to disk, and then move/rename that partial file to the
    final filename once all chunks are written. For this use, we cannot watch
    only the IN_CREATE event.  Observe the following event history:

    IN CREATE: /path/to/file/filename.part
    IN OPEN: /path/to/file/filename.part
    IN MODIFY: /path/to/file/filename.part
    IN MODIFY: /path/to/file/filename.part
    ...
    IN MODIFY: /path/to/file/filename.part
    IN CLOSE WRITE: /path/to/file/filename.part
    IN MOVED FROM: /path/to/file/filename.part
    IN MOVED TO: /path/to/file/filename

    Since we only want to signal when a new file is created, not just when
    a file is moved/renamed, we will use a state-machine to watch the stream
    of events, and only signal when the proper flow has been observed.
    Watching only the IN_MOVED_TO event would be insufficient because that
    could be triggered by someone manually renaming a file in the directory.

    To accomplish what we want, we will watch the IN_CREATE event and the
    IN_MOVED_TO event. In the special case of moving a file when both the
    source and destination directories are being watched, the IN_MOVED_TO event
    will also have a src_pathname attribute to tell what the original filename
    was. Since we are only concerned with files created and moved within our
    watched directories, this allows us to track the state from the creation
    of the temporary .part file all the way through moving it to the final
    filename.
    """
    def my_init(self):
        """
        Setup a dict we can track .part files in.

        Also define the max_allowable_age for an entry in the tracking dict.
        """
        self.temp_files = {}

        from datetime import timedelta
        self.max_allowed_age = timedelta(hours=6)

    def sleepshop(self):
        """
        Remove values from the temp_files instance variable when they
        have reached an unacceptable age.
        """
        from datetime import datetime
        now = datetime.now()
        for filename, timestamp in dict(self.temp_files).iteritems():
            if now - timestamp > self.max_allowed_age:
                del self.temp_files[filename]

    def process_IN_CREATE(self, event):
        """
        The IN_CREATE event will be the creation of the .part temporary file.

        So instead of sending the in_create signal now, we merely start to
        track the state of this temporary file. We store a current timestamp
        in the tracking dict so we can cull any values which have been around
        too long.
        """
        self.sleepshop()

        if event.pathname.endswith('.part'):
            import datetime
            self.temp_files[event.pathname] = datetime.datetime.now()

    def process_IN_MOVED_TO(self, event):
        """
        If both the source and destination directories are being watched by
        pyinotify, then this event will have a value in src_pathname. This
        value will be the .part filename and event.pathname will be the final
        filename.
        """
        if event.src_pathname and event.src_pathname in self.temp_files:
            del self.temp_files[event.src_pathname]
            signals.in_create.send(sender=self, event=event)

        self.sleepshop()

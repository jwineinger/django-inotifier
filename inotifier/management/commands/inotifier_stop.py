from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Stops monitoring directories for file events'

    def handle(self, *args, **options):
        from django.conf import settings

        import os.path
        try:
            pid_file = os.path.join(settings.PROJECT_PATH, 'inotifier.pid')
        except AttributeError:
            pid_file = os.path.join("/tmp", "inotifier.pid")
        
        if os.path.exists(pid_file):
            pid = int(open(pid_file).read())

            import signal
            try:
                os.kill(pid, signal.SIGHUP)
            except OSError:
                os.remove(pid_file)
                raise CommandError("No process with id %s was found. The pid file has been removed." % pid)

            import time
            time.sleep(2)

            try:
                os.kill(pid, signal.SIGKILL)
            except OSError:
                pass

            os.remove(pid_file)
            print "File watches have been stopped."
        else:
            raise CommandError("No pid file exists at %s." % pid_file)

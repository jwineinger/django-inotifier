from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Starts monitoring configured locations for file events'

    def handle(self, *args, **options):
        from django.conf import settings
        import os.path

        # Verify INOTIFIER_WATCH_PATHS is defined and non-empty
        try:
            assert settings.INOTIFIER_WATCH_PATHS
        except (AttributeError, AssertionError):
            raise CommandError('Missing/empty setting INOTIFIER_WATCH_PATHS')

        # Verify INOTIFIER_WATCH_PATHS is properly formatted
        try:
            len_3 = [len(tup) == 3 for tup in settings.INOTIFIER_WATCH_PATHS]
            assert all(len_3)
        except AssertionError:
            msg = 'setting INOTIFIER_WATCH_PATHS should be an iterable of '
            '3-tuples of the form '
            '[ ("/path1/", <pyinotify event mask>, <processor cls>), ]'
            raise CommandError(msg)

        # Verify monitor_paths exists and processor classes can be imported
        for mon_path, m, processor_cls in settings.INOTIFIER_WATCH_PATHS:
            if not os.path.exists(mon_path):
                err = "%s does not exist or you have insufficient permission" \
                      % mon_path
                raise CommandError(err)
            path = '.'.join(processor_cls.split('.')[0:-1])
            cls = processor_cls.split('.')[-1]
            try:
                mod = __import__(path, globals(), locals(), [cls], -1)
                getattr(mod, cls)
            except ImportError as e:
                err = 'Cannot import event processor module: %s\n\n%s' \
                      % (path, e)
                raise CommandError(err)
            except AttributeError:
                raise CommandError("%s does not exist in %s" % (cls, path))

        # Verify pyinotify is installed
        try:
            import pyinotify
        except ImportError as e:
            raise CommandError("Cannot import pyinotify: %s" % e)

        # Setup watches using pyinotify
        wm = pyinotify.WatchManager()
        for path, mask, processor_cls in settings.INOTIFIER_WATCH_PATHS:
            cls_path = '.'.join(processor_cls.split('.')[0:-1])
            cls = processor_cls.split('.')[-1]

            mod = __import__(cls_path, globals(), locals(), [cls], -1)
            Processor = getattr(mod, cls)

            wm.add_watch(path, mask, proc_fun=Processor())
            print "Adding watch on %s, processed by %s" % (path, processor_cls)

        notifier = pyinotify.Notifier(wm)

        # Setup pid file location. Try to use PROJECT_PATH but default to /tmp
        try:
            pid_file = os.path.join(settings.PROJECT_PATH, 'inotifier.pid')
        except AttributeError:
            pid_file = os.path.join("/tmp", "inotifier.pid")

        # Daemonize, killing any existing process specified in pid file
        daemon_kwargs = {}
        try:
            daemon_kwargs['stdout'] = settings.INOTIFIER_DAEMON_STDOUT
        except AttirbuteError:
            pass

        try:
            daemon_kwargs['stderr'] = settings.INOTIFIER_DAEMON_STDERR
        except AttirbuteError:
            pass

        notifier.loop(daemonize=True, pid_file=pid_file, force_kill=True,
                      **daemon_kwargs)

        print "File monitoring started"

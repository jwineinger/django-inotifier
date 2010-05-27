# First, get the directory which settinsg.py is in. Used in the example below
# but also optionally used in the 'inotifier_start' and 'inotifier_stop'
# management commands to calculate pid file location.  If PROJECT_PATH is not
# set, then /tmp will be assumed for the pid file location.
import os.path
PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))

def generate_watch_paths():
    """
    A simple function to generate an iterable of 3-tuples as the
    configuration to inotifier. The setting INOTIFIER_WATCH_PATHS is used by
    the management command 'inotifier_start'.

    This also keeps pyinotify from being imported directly into the settings
    namespace.
    """
    import pyinotify
    return (
       (
            os.path.join(PROJECT_PATH, 'incoming'),
            pyinotify.IN_CREATE,
            'inotifier.event_processors.CreateSignaler',
       ),
       (
            os.path.join(PROJECT_PATH, 'busy_dir'),
            pyinotify.ALL_EVENTS,
            'inotifier.event_processors.AllEventsSignaler',
       ),
    )
INOTIFIER_WATCH_PATHS = generate_watch_paths()

# OPTIONAL. Leave undefined if unused
INOTIFIER_DAEMON_STDOUT = os.path.join(PROJECT_PATH, 'inotifier_stdout.txt')

# OPTIONAL. Leave undefined if unused
INOTIFIER_DAEMON_STDERR = os.path.join(PROJECT_PATH, 'inotifier_stderr.txt')

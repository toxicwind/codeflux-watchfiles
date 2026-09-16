from .codeflux import ChangeEvent, watch_events, watch_jsonl
from .filters import BaseFilter, DefaultFilter, PythonFilter
from .main import Change, awatch, watch
from .run import arun_process, run_process
from .version import VERSION

__version__ = VERSION
__all__ = (
    'watch',
    'awatch',
    'run_process',
    'arun_process',
    'Change',
    'BaseFilter',
    'DefaultFilter',
    'PythonFilter',
    'VERSION',
    # codeflux fork improvement: structured streaming change events
    'ChangeEvent',
    'watch_events',
    'watch_jsonl',
)

import logging
import sys
from pathlib import Path

from loguru import logger as log

BASE_DIR = Path(__file__).parent.parent.parent.parent

LOG_DIR = Path(Path(BASE_DIR, "logs"))
LOG_DIR.mkdir(exist_ok=True)


def init_logging(old_logger=False, level=logging.INFO, steaming=True):
    log.remove()
    if steaming:
        log.add(sink=sys.stderr, level="TRACE", enqueue=True, diagnose=True)
    log.add(
        sink=Path(LOG_DIR, "main.log"),
        level="TRACE",
        enqueue=True,
        encoding="utf-8",
        diagnose=True,
        rotation="5MB",
        compression="zip",
    )
    if old_logger:

        class InterceptHandler(logging.Handler):
            def emit(self, record):
                # Get corresponding Loguru level if it exists
                try:
                    level = log.level(record.levelname).name
                except ValueError:
                    level = record.levelno

                # Find caller from where originated the logged message
                frame, depth = logging.currentframe(), 2
                while frame.f_code.co_filename == logging.__file__:
                    frame = frame.f_back
                    depth += 1

                log.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

        # logging.basicConfig(
        #     handlers=[InterceptHandler()], level=1
        # )

        handlers = [logging.FileHandler(filename=Path(LOG_DIR, "telethon.log"), encoding="utf-8")]
        if steaming:
            handlers.append(logging.StreamHandler())
        logging.basicConfig(
            encoding="utf-8",
            level=level,
            format="{levelname} [{asctime}] {name}: {message}",
            style="{",
            handlers=handlers,
        )

# logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
#                     level=logging.INFO)
# logger = logging.getLogger(__name__)

# logging.basicConfig(
#     encoding="utf-8",
#     level=logging.INFO,
#     format='{levelname} [{asctime}] {name}: {message}',
#     style="{",
#     handlers=[
#         logging.StreamHandler(),
#         logging.FileHandler(
#             filename=Path(LOG_DIR, "main.log"), encoding="utf-8",
#
#         ),
#     ],
# )


# class PropagateHandler(logging.Handler):
#     def emit(self, record):
#         logging.getLogger(record.name).handle(record)
#
#
# log.add(PropagateHandler(), format="{message}")

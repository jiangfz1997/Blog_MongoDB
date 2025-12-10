import logging
from pymongo.monitoring import CommandListener
from src.logger import get_logger
logger = get_logger(level='warning')


class MongoQueryMonitor(CommandListener):
    def __init__(self):
        # Key: request_id, Value: command_document
        self._commands = {}

    def started(self, event):
        self._commands[event.request_id] = event.command

    def succeeded(self, event):
        command_doc = self._commands.pop(event.request_id, None)

        if command_doc:
            self._log(event, command_doc, "SUCCESS")

    def failed(self, event):
        command_doc = self._commands.pop(event.request_id, None)
        if command_doc:
            self._log(event, command_doc, "FAILED")

    def _log(self, event, command_doc, status):
        duration_ms = event.duration_micros / 1000

        cmd_name = event.command_name
        if cmd_name in ('find', 'insert', 'update', 'delete', 'aggregate'):

            collection_name = command_doc.get(cmd_name, "unknown")

            log_msg = (
                f"[DBQUERYCOST][{status}] Cmd: {cmd_name} | "
                f"Coll: {collection_name} | "
                f"Time: {duration_ms:.2f}ms"
            )

            if duration_ms > 100:
                logger.warning(f"🐢 SLOW QUERY! {log_msg}")
                # logger.warning(f"   Query: {command_doc}")
            else:
                logger.debug(log_msg)
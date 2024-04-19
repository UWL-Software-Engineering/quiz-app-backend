
import logging

from logstash_async.formatter import FlaskLogstashFormatter
from logstash_async.handler import AsynchronousLogstashHandler


class Logger:

    @staticmethod
    def get_logger():

        host = '0.0.0.0'
        port = 8200

        logger = logging.getLogger('python-logstash-logger')
        logger.setLevel(logging.INFO)
        # test_logger.addHandler(AsynchronousLogstashHandler(host, port, database_path='logstash.db'))
        handler = AsynchronousLogstashHandler(host, port, database_path=None)

        logstash_formatter = FlaskLogstashFormatter(
            message_type='python-logstash',
            extra_prefix='',
            extra=dict(application="Quiz-Application", environment='production'))
        handler.setFormatter(logstash_formatter)
        logger.addHandler(handler)

        return logger

import logging


def setup_logging(aws_request_id):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.handlers[0].setFormatter(
        logging.Formatter(
            '%(asctime)s.%(msecs)dZ [{}] %(levelname)s %(message)s\n'.format(
                aws_request_id)
        )
    )
    return logger

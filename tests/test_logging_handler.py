from dataspec import logging_handler


def test_logging_handler():
    """ for coverage sake """
    logging_handler.configure_logging('debug')
    logging_handler.configure_logging('off')

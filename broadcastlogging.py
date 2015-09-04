'''
Module containing additions to the python logging system to send logging
messages via UDP broadcast.

In order to use the provided facilities:
1. Configure an application's logging system to use the
   :obj:`BroadcastHandler`.
2. Start the :obj:`receiver` (e.g. using ``python -m broadcastlogging``) and
   receive the broadcasted logging records locally.

.. codeauthor:: Johannes Wienke <languitar@semipol.de>
'''

import argparse
import logging
import logging.config
import logging.handlers
import pickle
import socket
import struct


LOGGER_NAME = 'broadcastlogging.receiver'


class BroadcastHandler(logging.handlers.DatagramHandler):
    '''
    A handler for the python logging system which is able to broadcast packets.
    '''

    def makeSocket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        return sock


def parse_args():
    '''
    Performs the command line parsing for the receiver utility method.
    '''
    parser = argparse.ArgumentParser(
        description='Receiver for python logging messages '
                    'sent via UDP broadcasts using the BroadcastHandler. '
                    'Received logging messages are fed back into Python\'s '
                    'logging system on this receiver\'s side. Therefore you '
                    'can use the usual configuration mechanisms to determine '
                    'how to handle the received messages.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    logging_group = parser.add_mutually_exclusive_group(required=True)
    logging_group.add_argument(
        '-c', '--basic',
        action='store_true',
        help='Use a basic logging system config printing everything')
    logging_group.add_argument(
        '-f', '--file',
        type=argparse.FileType('r'),
        help='Python logging system config file to configure '
             'how received messages are handled.')

    parser.add_argument(
        '-d', '--debug',
        action='store_true',
        help="Include this receiver's logging in the logging system "
             "by setting the own logger ({}) level to DEBUG.".format(
                 LOGGER_NAME))

    parser.add_argument(
        '-b', '--bind',
        metavar='ADDRESS',
        type=str,
        default='<broadcast>',
        help='Bind address to use')
    parser.add_argument(
        'port',
        metavar='PORT',
        type=int,
        help='Port on which the logging messages are broadcasted')
    return parser.parse_args()


def receiver():
    '''
    Main method to start a process which receives broadcasted logging messages
    sent using :obj:`BroadcastHandler`. The received messages are fed into the
    python logging system on the receiving side again, so that the usual
    configuration mechanisms can also be applied on the local side.
    '''
    args = parse_args()

    if args.basic:
        logging.basicConfig(level=logging.DEBUG)
    elif args.file:
        logging.config.fileConfig(args.file)

    logger = logging.getLogger(LOGGER_NAME)

    if not args.debug:
        logger.setLevel(logging.WARN)

    logger.debug('Binding to address "%s" and port %s', args.bind, args.port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((args.bind, args.port))

    while True:
        # TODO handle packets larger than buffer
        # wait for new data to arrive
        logger.debug('Waiting for new data...')
        data = sock.recv(4096)
        logger.debug('Received %s bytes', len(data))

        # verify that the amount of data is sufficient to at least determine
        # the size of the pickle blob
        if not data or len(data) < 4:
            logger.warn('Received less then 4 bytes of data. '
                        'This is not enough to event contain '
                        'the size of the pickled log record data. '
                        'Skipping this packet.')
            continue

        # determine the log record size
        try:
            record_size = struct.unpack('>L', data[:4])[0]
        except struct.error:
            logger.error('Unexpected error while unpacking the log '
                         'record size via struct. Skipping this packet.',
                         exc_info=True)
            continue

        # ensure that we have received enough bytes to contain the record
        if len(data) < record_size + 4:
            logger.warn('Received a truncated log record. %s bytes missing.'
                        'Skipping this record.',
                        record_size + 4 - len(data))
            continue

        # unpack the log record dict
        try:
            record_data = pickle.loads(data[4:])
        except pickle.PickleError:
            logger.error('Unable to unpickle the log record data. '
                         'Skipping this record.', exc_info=True)
            continue

        record = logging.makeLogRecord(record_data)
        logging.getLogger(record.name).handle(record)


if __name__ == '__main__':
    receiver()

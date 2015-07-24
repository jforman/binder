# Binder Exceptions


class TransferException(Exception):

    """Thrown when an AXFR transfer cannot be performed."""

    pass


class ZoneException(Exception):

    """Thrown when there is an issue dealing with a DNS zone."""

    pass


class RecordException(Exception):

    """Thrown when there is an issue dealign with a Record.

    * Adding or deleting.
    """

    pass


class KeyringException(Exception):

    """Thrown when there is a problem creating the keyring.

    * When the length/padding of the TSIG data is incorrect.
    """

    pass

import binascii

import dns.tsigkeyring

from binder import exceptions


def create_keyring(key_name, key_data):
    """Return a tsigkeyring object from key name and key data.

    Args:
      key_name: String representation of key name
      key_data: String representation of TSIG key hash

    Return:
      keyring object with the key name and TSIG secret.
    """

    try:
        keyring = dns.tsigkeyring.from_text({
                key_name : key_data
                })
    except binascii.Error, err:
        raise exceptions.KeyringException("Error creating keyring. Verify correct key data for key: %s. Reason: %s" % (key_name, err))
    return keyring

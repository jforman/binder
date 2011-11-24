import dns.tsigkeyring
import re
import sys

def create_keyring(key_dict):
    """Accept a TSIG keyfile and a key name to retrieve.
    Return a keyring object with the key name and TSIG secret."""

    keyring = dns.tsigkeyring.from_text({
            key_dict.name : key_dict.data
    })

    return keyring

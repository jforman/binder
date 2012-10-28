import dns.tsigkeyring
import sys
from models import Key

def create_keyring(key_name):
    """Accept a TSIG keyfile and a key name to retrieve.
    Return a keyring object with the key name and TSIG secret."""

    key_dict = Key.objects.get(name=key_name)

    keyring = dns.tsigkeyring.from_text({
            key_dict.name : key_dict.data
    })

    return keyring

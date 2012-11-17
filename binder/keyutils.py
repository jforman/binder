import dns.tsigkeyring

def create_keyring(key_name, key_data):
    """Return a tsigkeyring object from key name and key data.

    Args:
      key_name: String representation of key name
      key_data: String representation of TSIG key hash

    Return:
      keyring object with the key name and TSIG secret."""

    keyring = dns.tsigkeyring.from_text({
            key_name : key_data
    })

    return keyring

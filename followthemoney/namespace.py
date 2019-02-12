import hmac
import hashlib

from followthemoney.util import key_bytes


class Namespace(object):
    """Namespaces are used to partition entity IDs into different units,
    which traditionally represent a dataset, collection or source."""
    SEP = '.'

    def __init__(self, name=None):
        self.bname = key_bytes(name)
        self.hmac = hmac.new(self.bname, digestmod='sha1')

    def parse(self, entity_id):
        if entity_id is None:
            return (None, None)
        try:
            plain_id, checksum = entity_id.rsplit(self.SEP, 1)
            return (plain_id, checksum)
        except ValueError:
            return (entity_id, None)

    def signature(self, entity_id):
        if not len(self.bname) or entity_id is None:
            return None
        digest = self.hmac.copy()
        digest.update(key_bytes(entity_id))
        return digest.hexdigest()

    def sign(self, entity_id):
        entity_id, _ = self.parse(entity_id)
        if not len(self.bname):
            return entity_id
        if entity_id is None:
            return None
        digest = self.signature(entity_id)
        return self.SEP.join((entity_id, digest))

    def verify(self, entity_id):
        entity_id, digest = self.parse(entity_id)
        if digest is None:
            return False
        return hmac.compare_digest(digest, self.signature(entity_id))

    def generate(self, *parts):
        parts = b''.join([key_bytes(p) for p in parts])
        if not len(parts):
            return None
        entity_id = hashlib.sha1(parts).hexdigest()
        return self.sign(entity_id)

    @classmethod
    def make(cls, name):
        if isinstance(name, cls):
            return name
        return cls(name)

    def __eq__(self, other):
        return self.bname == other.bname

    def __repr__(self):
        return '<Namespace(%r)>' % self.bname

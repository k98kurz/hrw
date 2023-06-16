from hashlib import sha256
from math import ceil, log
from typing import Callable


_basic_hash = lambda preimage: sha256(preimage).digest()


def calculate_k(replica_ids: list[bytes]) -> int:
    """Given a list of replica IDs, return the number k that scales the
        number of copies of a piece of content with the log of the
        square of the number of available replicas:
        ceil(log(len(replica_ids)**2)). E.g. 1 replica for 1 node, 2 for
        2, 3 for 3-4, 4 for 5-7, 5 for 8-12, ..., 10 for 91-148, ..., 18
        for 4915-8103, etc.
    """
    if type(replica_ids) not in (list, tuple):
        raise TypeError('replica_ids must be list or tuple of bytes')
    if not all(type(rid) is bytes for rid in replica_ids):
        raise TypeError('replica_ids must be list or tuple of bytes')
    if len(replica_ids) < 1:
        raise ValueError('replica_ids must not be empty')
    return ceil(log(len(replica_ids)**2))


def sort(content_id: bytes, replica_ids: list[bytes], /, *,
           hash_function: Callable[[bytes], bytes] = None) -> list[bytes]:
    """Given a content and a list of replica IDS, sort the replicas by
        descending likelihood that each replica will store/cache the
        content.
        ----------
        Returns the sorted list of replica IDs.
    """
    if type(content_id) is not bytes:
        raise TypeError('content_id must be bytes')
    if type(replica_ids) not in (list, tuple):
        raise TypeError('replica_ids must be list or tuple of bytes')
    if not all(type(rid) is bytes for rid in replica_ids):
        raise TypeError('replica_ids must be list or tuple of bytes')
    if len(replica_ids) < 1:
        raise ValueError('replica_ids must not be empty')
    if not callable(hash_function) and hash_function is not None:
        raise TypeError('hash_function must be Callable[[bytes], bytes]')

    hash_function = hash_function or _basic_hash

    hashes = {}
    for rid in replica_ids:
        hashes[hash_function(content_id + rid)] = rid

    ordered = [n for n in hashes]
    ordered.sort()
    ordered.reverse()
    return [hashes[n] for n in ordered]


def choose(content_id: bytes, replica_ids: list[bytes], /, *, k: int = None,
           hash_function: Callable[[bytes], bytes] = None) -> tuple[list[bytes], list[bytes]]:
    """Given a content ID and a list of replica IDS, sort the replicas
        and choose the k replicas that should hold/cache the content
        item. If k is left equal to None, it will be chosen as
        ceil(log(len(replica_ids)**2)) or 1 and thus adjust
        automatically as the number of replicas changes, e.g. 1 replica
        for 1 replica, 2 for 2, 3 for 3-4, 4 for 5-7, 5 for 8-12, ...,
        10 for 91-148, ..., 18 for 4915-8103, etc. If hash_function is
        provided, that will be used instead of sha256.
        ----------
        Returns the sorted list of chosen replica IDs and the sorted
        list of unchosen replica IDs.
    """
    if type(k) is not int and k is not None:
        raise TypeError('k must be int <= len(replica_ids)')

    k = k or calculate_k(replica_ids) or 1

    if k > len(replica_ids):
        raise ValueError('k must be int <= len(replica_ids)')

    ordered = sort(content_id, replica_ids, hash_function=hash_function)

    return (ordered[:k], ordered[k:])

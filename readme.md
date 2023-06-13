# HRW

Highest random weight (aka rendezvous hashing) is an older, simpler, and more
general algorithm for determining which subset of available replicas should have
a copy of any given piece of content. This is done by hashing the content ID
with each replica ID, then sorting the resulting hashes in descending order and
choosing the replicas associated with the first k hashes.

This algorithm deterministically selects replicas in such a way that any number
of nodes that have the same list of replica IDs will choose the same subset of
replicas for each content ID, and each replica will have an equal chance of
being selected for any given content ID. It is superior to consistent hashing
by reducing the overhead for load balancing and from reindexing during replica
churn: instead of every replica getting a large number of keys on a logical ring
and passing their content "to the right" on the ring when they spin down, each
piece of content is dynamically allotted replicas at the time that it is stored
or accessed using only the IDs used for each replica and the ID of the content.
Additionally, the load balancing proportions between replicas can be managed
precisely by adding replica ID aliases for replicas to increase each replica's
chance of being chosen by HRW; e.g. if one replica has twice the capability of
any other replica, it would be allocated a second replica ID (e.g. the hash of
its initial ID concatenated with a number).

## Installation

```bash
pip install hrw
```

## Usage

The simplest method for using this algorithm is to use the `choose` function
specifying just the `content_id` and the `replica_ids`. Doing so will return a
deterministic, dynamically-sized list of replica IDs.

```python
from hashlib import sha256
from hrw import choose


# some list of bytes replica ids, which should be unique
replica_ids = [i.to_bytes(2) for i in range(256)]

# some content
content = b'Lorem ipsum dolor sit amet, something something darkside.'

# set the content_id as the sha256 hash of the content
content_id = sha256(content).digest()

# choose a subset of replicas for storage/caching of the content
chosen_replica_ids = choose(content_id, replica_ids)

# should print twelve
print([crid.hex() for crid in chosen_replica_ids])

expected = ['004c', '006d', '0047', '004e', '00ee', '008b', '00be', '0016', '0064', '00e2', '0055', '002f']
assert [crid.hex() for crid in chosen_replica_ids] == expected
```

To set the number of replicas to be chosen, supply the int argument `k`:

```python
choose(content_id, replica_ids, k=3)
```

To use a different hashing algorithm, supply the argument `hash_function`:

```python
from hashlib import shake_256
from hrw import choose


hash_func = lambda preimage: shake_256(preimage).digest(20)
replica_ids = [i.to_bytes(2) for i in range(256)]
content = b'Lorem ipsum dolor sit amet, something something darkside.'
content_id = hash_func(content)
chosen_replica_ids = choose(content_id, replica_ids, hash_function=hash_func)

# should print twelve
print([crid.hex() for crid in chosen_replica_ids])
expected = ['00e2', '0061', '000a', '0099', '0024', '00aa', '00bd', '0017', '006b', '00cd', '0079', '00e1']
assert [crid.hex() for crid in chosen_replica_ids] == expected
```

Raises `TypeError` or `ValueError` for invalid arguments.

## ISC License

Copyleft (c) 2023 k98kurz

Permission to use, copy, modify, and/or distribute this software
for any purpose with or without fee is hereby granted, provided
that the above copyleft notice and this permission notice appear in
all copies.

Exceptions: this permission is not granted to Alphabet/Google, Amazon,
Apple, Microsoft, Netflix, Meta/Facebook, Twitter, or Disney; nor is
permission granted to any company that contracts to supply weapons or
logistics to any national military; nor is permission granted to any
national government or governmental agency; nor is permission granted to
any employees, associates, or affiliates of these designated entities.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL
WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE
AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR
CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

from context import functions
from hashlib import md5
import unittest


class TestFunctions(unittest.TestCase):
    def test_calculate_k_raises_TypeError_or_ValueError_for_invalid_arg(self):
        with self.assertRaises(TypeError) as e:
            functions.calculate_k('not a list')
        assert str(e.exception) == 'replica_ids must be list or tuple of bytes'
        with self.assertRaises(TypeError) as e:
            functions.calculate_k([b'bytes', 'not bytes'])
        assert str(e.exception) == 'replica_ids must be list or tuple of bytes'
        with self.assertRaises(ValueError) as e:
            functions.calculate_k([])
        assert str(e.exception) == 'replica_ids must not be empty'

    def test_calculate_k_returns_int(self):
        for i in range(1, 200):
            replica_ids = [t.to_bytes(1) for t in range(i)]
            k = functions.calculate_k(replica_ids)
            assert type(k) is int
            assert k <= i

    def test_sort_raises_TypeError_or_ValueError_for_invalid_args(self):
        good_content_id = b'123'
        bad_content_id = 'not bytes'
        good_replica_ids = [b'123', b'abc']
        bad_replica_ids = [b'bytes', 'not bytes']

        with self.assertRaises(TypeError) as e:
            functions.sort(bad_content_id, good_replica_ids)
        assert str(e.exception) == 'content_id must be bytes'
        with self.assertRaises(TypeError) as e:
            functions.sort(good_content_id, 'not tuple or list')
        assert str(e.exception) == 'replica_ids must be list or tuple of bytes'
        with self.assertRaises(TypeError) as e:
            functions.sort(good_content_id, bad_replica_ids)
        assert str(e.exception) == 'replica_ids must be list or tuple of bytes'
        with self.assertRaises(ValueError) as e:
            functions.sort(good_content_id, [])
        assert str(e.exception) == 'replica_ids must not be empty'
        with self.assertRaises(TypeError) as e:
            functions.sort(good_content_id, good_replica_ids, hash_function='not callable')
        assert str(e.exception) == 'hash_function must be Callable[[bytes], bytes]'

    def test_sort_returns_list_of_bytes(self):
        replica_ids = [i.to_bytes(1) for i in range(200)]
        for rid in replica_ids:
            sorted_rids = functions.sort(rid, replica_ids)
            assert type(sorted_rids) is list
            assert all(type(rid) is bytes for rid in sorted_rids)
            assert all(rid in replica_ids for rid in sorted_rids)
            assert len(sorted_rids) == len(replica_ids)

    def test_sort_sorts_replica_ids_deterministically_and_at_random(self):
        replica_ids = [i.to_bytes(1) for i in range(200)]
        content_id_1 = b'abc'
        content_id_2 = b'abd'

        sorted1 = functions.sort(content_id_1, replica_ids)
        assert sorted1 == functions.sort(content_id_1, replica_ids)

        sorted2 = functions.sort(content_id_2, replica_ids)
        assert sorted2 == functions.sort(content_id_2, replica_ids)
        assert sorted2 != sorted1

    def test_sort_hash_function_arg_changes_order(self):
        replica_ids = [i.to_bytes(1) for i in range(200)]
        content_id = b'abc'

        hash_func = lambda preimage: md5(preimage).digest()
        identity_func = lambda preimage: preimage

        sorted1 = functions.sort(content_id, replica_ids)
        sorted2 = functions.sort(content_id, replica_ids, hash_function=hash_func)
        sorted3 = functions.sort(content_id, replica_ids, hash_function=identity_func)

        assert sorted1 != sorted2 != sorted3

    def test_choose_raises_TypeError_or_ValueError_for_invalid_args(self):
        good_content_id = b'123'
        bad_content_id = 'not bytes'
        good_replica_ids = [b'123', b'abc']
        bad_replica_ids = [b'bytes', 'not bytes']

        with self.assertRaises(TypeError) as e:
            functions.choose(bad_content_id, good_replica_ids)
        assert str(e.exception) == 'content_id must be bytes'
        with self.assertRaises(TypeError) as e:
            functions.choose(good_content_id, 'not tuple or list')
        assert str(e.exception) == 'replica_ids must be list or tuple of bytes'
        with self.assertRaises(TypeError) as e:
            functions.choose(good_content_id, bad_replica_ids)
        assert str(e.exception) == 'replica_ids must be list or tuple of bytes'
        with self.assertRaises(ValueError) as e:
            functions.choose(good_content_id, [])
        assert str(e.exception) == 'replica_ids must not be empty'
        with self.assertRaises(TypeError) as e:
            functions.choose(good_content_id, good_replica_ids, hash_function='not callable')
        assert str(e.exception) == 'hash_function must be Callable[[bytes], bytes]'
        with self.assertRaises(TypeError) as e:
            functions.choose(good_content_id, good_replica_ids, k='not an int')
        assert str(e.exception) == 'k must be int <= len(replica_ids)'
        with self.assertRaises(ValueError) as e:
            functions.choose(good_content_id, good_replica_ids, k=10_000_000)
        assert str(e.exception) == 'k must be int <= len(replica_ids)'

    def test_choose_returns_two_lists_of_replica_ids_without_overlap(self):
        replica_ids = [i.to_bytes(1) for i in range(200)]
        for rid in replica_ids:
            result = functions.choose(rid, replica_ids)
            assert type(result) is tuple
            assert len(result) == 2

            chosen, unchosen = result
            assert type(chosen) is list
            assert type(unchosen) is list

            assert all(type(crid) is bytes for crid in chosen)
            assert all(crid in replica_ids for crid in chosen)
            assert all(crid not in unchosen for crid in chosen)

            assert all(type(urid) is bytes for urid in unchosen)
            assert all(urid in replica_ids for urid in unchosen)
            assert all(urid not in chosen for urid in unchosen)

    def test_choose_results_are_deterministic_and_random(self):
        replica_ids = [i.to_bytes(1) for i in range(200)]
        content_id_1 = b'abc'
        content_id_2 = b'abd'

        result1 = functions.choose(content_id_1, replica_ids)
        assert result1 == functions.choose(content_id_1, replica_ids)
        result2 = functions.choose(content_id_2, replica_ids)
        assert result2 == functions.choose(content_id_2, replica_ids)
        assert result1 != result2

    def test_choose_first_list_is_len_k_and_second_list_is_len_replica_ids_minus_k(self):
        replica_ids = [i.to_bytes(1) for i in range(200)]
        content_id = b'abc'
        chosen, unchosen = functions.choose(content_id, replica_ids, k=2)
        assert len(chosen) == 2
        assert len(unchosen) == len(replica_ids) - 2
        chosen, unchosen = functions.choose(content_id, replica_ids, k=12)
        assert len(chosen) == 12
        assert len(unchosen) == len(replica_ids) - 12

    def test_choose_hash_function_arg_changes_result(self):
        replica_ids = [i.to_bytes(1) for i in range(200)]
        content_id = b'abc'

        hash_func = lambda preimage: md5(preimage).digest()
        identity_func = lambda preimage: preimage

        result1 = functions.choose(content_id, replica_ids)
        result2 = functions.choose(content_id, replica_ids, hash_function=hash_func)
        result3 = functions.choose(content_id, replica_ids, hash_function=identity_func)

        assert result1 != result2 != result3


if __name__ == '__main__':
    unittest.main()

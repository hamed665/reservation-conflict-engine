import unittest
import tempfile
from concurrent.futures import ThreadPoolExecutor
from slotguard.core import Calendar, Conflict, instant

class CalendarTests(unittest.TestCase):
    def setUp(self): self.c = Calendar()
    def tearDown(self): self.c.close()
    def book(self, key='a', start='10:00', end='10:30', tenant='t'):
        return self.c.book(tenant,key,'room',f'2026-11-01T{start}:00+04:00',f'2026-11-01T{end}:00+04:00')
    def test_timezone_equivalence(self):
        self.assertEqual(instant('2026-11-01T10:00:00+04:00'), instant('2026-11-01T06:00:00Z'))
    def test_naive_rejected(self):
        with self.assertRaises(ValueError): instant('2026-11-01T10:00:00')
    def test_overlap_and_adjacency(self):
        self.book()
        with self.assertRaises(Conflict): self.book('b','10:15','10:45')
        self.book('c','10:30','11:00')
    def test_cancel_releases_slot(self):
        self.book(); self.assertTrue(self.c.cancel('t','a')); self.book('b')
        self.assertFalse(self.c.cancel('t','a'))
    def test_idempotency_and_changed_payload(self):
        self.assertEqual(self.book(), self.book())
        with self.assertRaises(Conflict): self.book('a','11:00','11:30')
    def test_isolation(self):
        self.book(); self.book(tenant='other'); self.assertEqual(len(self.c.list('t')),1)
    def test_invalid_range(self):
        with self.assertRaises(ValueError): self.book(start='11:00')
    def test_concurrent_claim(self):
        with tempfile.TemporaryDirectory() as folder:
            path = folder+'/calendar.db'
            Calendar(path).close()
            def attempt(key):
                c = Calendar(path)
                try:
                    c.book('t',key,'r','2026-11-01T10:00:00Z','2026-11-01T11:00:00Z')
                    return True
                except Conflict: return False
                finally: c.close()
            with ThreadPoolExecutor(2) as pool:
                self.assertEqual(sum(pool.map(attempt,['a','b'])),1)

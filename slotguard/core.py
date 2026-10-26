"""UTC persistence, half-open intervals, transactional conflict checks."""
from datetime import datetime, timezone
import sqlite3

class Conflict(ValueError):
    pass

def instant(value: str) -> int:
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError("explicit UTC offset required")
    if dt.microsecond:
        raise ValueError("timestamps must have whole-second precision")
    return int(dt.astimezone(timezone.utc).timestamp())

class Calendar:
    def __init__(self, path=':memory:'):
        self.db = sqlite3.connect(path, isolation_level=None, timeout=5)
        self.db.row_factory = sqlite3.Row
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.execute("""CREATE TABLE IF NOT EXISTS bookings (
          tenant TEXT, booking_id TEXT, resource TEXT, starts INTEGER,
          ends INTEGER, cancelled INTEGER NOT NULL DEFAULT 0,
          PRIMARY KEY (tenant, booking_id), CHECK(ends > starts))""")
        self.db.execute('CREATE INDEX IF NOT EXISTS by_resource ON bookings(tenant,resource,starts,ends)')

    def book(self, tenant, booking_id, resource, start, end):
        if not all(isinstance(v, str) and v.strip() for v in (tenant, booking_id, resource)):
            raise ValueError('nonempty tenant, booking_id and resource required')
        a, b = instant(start), instant(end)
        if b <= a:
            raise ValueError('end must follow start')
        self.db.execute('BEGIN IMMEDIATE')
        try:
            old = self.db.execute('SELECT * FROM bookings WHERE tenant=? AND booking_id=?',
                                  (tenant, booking_id)).fetchone()
            if old:
                if (old['resource'], old['starts'], old['ends']) != (resource, a, b):
                    raise Conflict('idempotency key reused with different booking')
                if old['cancelled']:
                    raise Conflict('cancelled booking cannot be silently reopened')
                self.db.commit()
                return dict(old)
            overlap = self.db.execute("""SELECT booking_id FROM bookings WHERE
              tenant=? AND resource=? AND cancelled=0 AND starts<? AND ends>?""",
              (tenant, resource, b, a)).fetchone()
            if overlap:
                raise Conflict('resource is already reserved')
            self.db.execute('INSERT INTO bookings(tenant,booking_id,resource,starts,ends) VALUES(?,?,?,?,?)',
                            (tenant, booking_id, resource, a, b))
            self.db.commit()
            return dict(self.db.execute('SELECT * FROM bookings WHERE tenant=? AND booking_id=?',
                                        (tenant, booking_id)).fetchone())
        except BaseException:
            self.db.rollback()
            raise

    def cancel(self, tenant, booking_id):
        return self.db.execute('UPDATE bookings SET cancelled=1 WHERE tenant=? AND booking_id=? AND cancelled=0',
                               (tenant, booking_id)).rowcount == 1

    def list(self, tenant):
        return [dict(r) for r in self.db.execute('SELECT * FROM bookings WHERE tenant=? ORDER BY starts,booking_id', (tenant,))]

    def close(self):
        self.db.close()

import json
from .core import Calendar, Conflict

with_demo = Calendar()
with_demo.book('demo-clinic', 'a', 'room-1', '2026-11-01T10:00:00+04:00', '2026-11-01T10:30:00+04:00')
try:
    with_demo.book('demo-clinic', 'b', 'room-1', '2026-11-01T06:15:00+00:00', '2026-11-01T06:45:00+00:00')
except Conflict as error:
    print(json.dumps({'rejected': str(error)}))
with_demo.book('demo-clinic', 'c', 'room-1', '2026-11-01T10:30:00+04:00', '2026-11-01T11:00:00+04:00')
print(json.dumps(with_demo.list('demo-clinic'), indent=2))
with_demo.close()

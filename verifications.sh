
# Checking MQTT client is sending messages
mosquitto_sub \
 -h localhost \
 -t 'marine/telemetry/GARMIN-DIVE-001/DIVE-136' \
 -v

# Checking SQL database
sqlite3 output/publisher.db \
"SELECT COUNT(*) FROM outbox WHERE status='PENDING';"

sqlite3 output/publisher.db \
".schema outbox"

sqlite3 output/publisher.db \
"SELECT
    COUNT(*) AS total,
    SUM(CASE WHEN status = 'PENDING' THEN 1 ELSE 0 END) AS pending,
    SUM(CASE WHEN status = 'SENT' THEN 1 ELSE 0 END) AS sent
FROM outbox;"

# Testing cloud agent
sqlite3 output/publisher.db \
"UPDATE outbox SET cloud_status='PENDING' WHERE message_id='e7c8ff28-29e4-409d-9c54-eff8329fa3af';"

sqlite3 output/publisher.db \
"SELECT message_id, cloud_status, cloud_attempts FROM outbox WHERE message_id='e7c8ff28-29e4-409d-9c54-eff8329fa3af';"

# Kubernetes verification 
kubectl exec -n marine-edge deploy/sync-agent -- \
  python -c "
import sqlite3
c=sqlite3.connect('output/publisher.db')
print(c.execute('SELECT status, COUNT(*) FROM outbox GROUP BY status').fetchall())
"
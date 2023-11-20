kafka-topics --create --bootstrap-server kafka:29092 --replication-factor 1  --partitions 1  --topic source-topic \
--command-config /tmp/client.properties --config cleanup.policy=delete --config delete.retention.ms=86400000 --config retention.ms=43200000

kafka-topics --create --bootstrap-server kafka:29092 --replication-factor 1  --partitions 1  --topic sink-topic \
--command-config /tmp/client.properties --config cleanup.policy=delete --config delete.retention.ms=86400000 --config retention.ms=43200000
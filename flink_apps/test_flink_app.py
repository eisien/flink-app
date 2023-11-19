from pyflink.table import TableEnvironment, EnvironmentSettings

def log_processing():
    env_settings = EnvironmentSettings.in_streaming_mode()
    t_env = TableEnvironment.create(env_settings)
    # specify connector and format jars
    t_env.get_config().set("pipeline.jars", "file:///tmp/flink_jars/flink-sql-connector-kafka-1.16.2.jar;file:///tmp/flink_jars/kafka-clients-2.8.2.jar")
    
    source_ddl = """
            CREATE TABLE source_table(
                log STRING
            ) WITH (
              'connector' = 'kafka',
              'topic' = 'source-topic',
              'properties.bootstrap.servers' = 'kafka:29092',
              'properties.security.protocol' ='SASL_PLAINTEXT',
              'properties.sasl.mechanism' = 'PLAIN',
              'properties.sasl.jaas.config' = 'org.apache.kafka.common.security.plain.PlainLoginModule required username=\"admin\" password=\"admin-secret\";',
              'properties.group.id' = 'test_3',
              'scan.startup.mode' = 'latest-offset',
              'format' = 'raw'
            )
            """

    sink_ddl = """
            CREATE TABLE sink_table(
                a VARCHAR,
                is_json BOOLEAN
            ) WITH (
              'connector' = 'kafka',
              'topic' = 'sink-topic',
              'properties.bootstrap.servers' = 'kafka:29092',
              'properties.security.protocol' ='SASL_PLAINTEXT',
              'properties.sasl.mechanism' = 'PLAIN',
              'properties.sasl.jaas.config' = 'org.apache.kafka.common.security.plain.PlainLoginModule required username=\"admin\" password=\"admin-secret\";',
              'format' = 'json'
            )
            """

    t_env.execute_sql(source_ddl)
    t_env.execute_sql(sink_ddl)

    t_env.sql_query("SELECT JSON_VALUE(log, '$.event_id') as event_id, log IS JSON as is_json  FROM source_table") \
    .insert_into("sink_table")
        # .execute_insert("sink_table").wait()


if __name__ == '__main__':
    log_processing()
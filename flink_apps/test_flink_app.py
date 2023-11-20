from pyflink.table import TableEnvironment, EnvironmentSettings
from pyflink.table.expressions import col
from pyflink.table.types import DataTypes

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
                event_id VARCHAR,
                name VARCHAR,
                log STRING,
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

    query=t_env.sql_query("SELECT log, log IS JSON as is_json  FROM source_table")
    
    processed_query = query.filter(col("is_json")==True)
    t_env.register_table("temp", processed_query)
    processed_query = t_env.sql_query("""
    select 
        JSON_VALUE(log, '$.event_id') as event_id, 
        JSON_VALUE(log, '$.data.name') as name,
        log,
        is_json
    from temp
    """)
    processed_query.execute_insert("sink_table")


    # malformed_ddl = """ 
    #         CREATE TABLE malformed_msg_table(
    #             log STRING,
    #             is_json BOOLEAN
    #         ) WITH (
    #           'connector' = 'kafka',
    #           'topic' = 'sink-malformed-topic',
    #           'properties.bootstrap.servers' = 'kafka:29092',
    #           'properties.security.protocol' ='SASL_PLAINTEXT',
    #           'properties.sasl.mechanism' = 'PLAIN',
    #           'properties.sasl.jaas.config' = 'org.apache.kafka.common.security.plain.PlainLoginModule required username=\"admin\" password=\"admin-secret\";',
    #           'format' = 'json'
    #         )
    #         """
    # t_env.execute_sql(malformed_ddl)
    # query.filter(col("is_json")==False).execute_insert("malformed_msg_table")

if __name__ == '__main__':
    log_processing()
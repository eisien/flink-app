package com.app.test

import com.typesafe.config.{ConfigFactory, ConfigObject, ConfigValue}
import org.apache.flink.table.api.TableEnvironment
import org.apache.flink.table.api.EnvironmentSettings

import scala.collection.JavaConverters._
import java.util.Map.Entry
import org.slf4j.LoggerFactory

import java.util.Properties


object FlinkApp {

    val logger = LoggerFactory.getLogger(getClass.getName)

    val kafkaUser: String = Option(System.getenv("KAFKA_USERNAME")).getOrElse("default_user")
    val kafkaPassword: String = Option(System.getenv("KAFKA_PASSWORD")).getOrElse("default_password")
    val jaasTemplate = "org.apache.kafka.common.security.scram.ScramLoginModule required username=\"%s\" password=\"%s\";"
    val jaasConfig = String.format(jaasTemplate, kafkaUser, kafkaPassword)


    // Load dev config for dev running environment by default
    var env = Option(System.getenv("FLINK_ENV")).getOrElse("local")
    var config = ConfigFactory.load(s"$env.conf")

    def getProperties(): Properties = {
      val trustStoreLocation = config.getString("app_config.ssl_truststore_location")
      val props = new Properties()
      props.put("fetch.min.bytes", "1")
      props.put("max.poll.records", "5000")
      props.put("ssl.truststore.type", "jks")
      props.put("ssl.truststore.location", trustStoreLocation)
      props.put("security.protocol", "SASL_SSL")
      props.put("sasl.mechanism", "SCRAM-SHA-512")
      props.put("sasl.jaas.config", jaasConfig)
      props.put("bootstrap.servers", config.getString("kafka_source_brokers"))  // TODO: can be removed from here if not same for sink

      props
    }

    def get_flink_table_config(config_name: String)={
      val table_config = config.getObject(config_name)
      val config_list = (
        for {
          entry: Entry[String, ConfigValue] <- table_config.entrySet().asScala
          key = entry.getKey
          e_value = entry.getValue.unwrapped.toString
          value = if (key == "properties.sasl.jaas.config") e_value.format(kafkaUser, kafkaPassword) else e_value
        } yield "'%s' = '%s'".format(key, value)
        ).toList
      config_list.mkString(",\n")
    }

    def main(args: Array[String]): Unit = {
      val logger = LoggerFactory.getLogger(getClass.getName)
      logger.info("Starting flink app...")

      logger.info(s"Running environment is $env, loaded prod app config: {}", config.toString)

      // setup streaming env
      val settings = EnvironmentSettings.newInstance().inStreamingMode().build()
      val tableEnv = TableEnvironment.create(settings)
      val configuration = tableEnv.getConfig.getConfiguration
      configuration.setString("table.local-time-zone", "UTC")

      tableEnv.getConfig.
      // Register the Kafka source as a table
      val source_topic_table_config = get_flink_table_config("app_config.flink_table_kafka_source_config")
      val source_ddl = "CREATE TABLE flink_table_streaming_events (" +
        "log STRING\n"+
        ") WITH (\n" +
        source_topic_table_config +
        ")"
      logger.info(source_ddl)
      tableEnv.executeSql(source_ddl)

      // connect sink topic
      val sink_topic_table_config = get_flink_table_config("app_config.flink_table_kafka_sink_config")
      val sink_ddl_create =
        """
          |CREATE TABLE flink_table_nrt(
          |                event_id STRING,
          |                event_type STRING,
          |                data STRING,
          |                is_json BOOLEAN
          |""".stripMargin
      val sink_ddl_config = ") WITH (\n" + sink_topic_table_config + ")"
      val sink_ddl = sink_ddl_create + sink_ddl_config
      logger.info(sink_ddl)
      tableEnv.executeSql(sink_ddl)

      val streaming_query = tableEnv.sqlQuery(
        """
        |   SELECT JSON_VALUE(log, '$.event_id') as event_id, 
        |   JSON_VALUE(log, '$.event_type') as event_type,
        |   JSON_VALUE(log, '$.data') as data,
        |   log IS JSON as is_json 
        |   FROM flink_table_streaming_events
        """.stripMargin)

      streaming_query.executeInsert("flink_table_nrt")

    }
  }

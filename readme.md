<h1>docker-compose for Apache Flink, Kafka and Provectus UI</h1>

* Install Docker desktop from https://www.docker.com/products/docker-desktop/
  - After the installation is complete, select the choices related to personal development only.
  - You can open the app without requiring to sign in
  - Verify the docker and docker-compose commands.
* Clone the repo and get into the repo folder in your terminal
* Run container services:
    - Run Command: ```docker-compose -f docker-compose-kafka-ui-zk-flink-python.yml up -d```
    - You should be able to see the containers running in docker desktop as well.
* Browse provectus Kafka UI: http://0.0.0.0:8080/
Screenshot:
    - **NOTE**: It may take few minutes for kafka to spin up its services before it comes online in the dashboard or allow creation of topics.
    - you can always look for the realtime logs by clicking on the container in Docker-Desktop app.
* Create kafka topics, this will help to run test_flink_app.py flink job.
    - In left side pane of the UI, go to local > Topics. 
    - Click on 'Add a Topic' on right-top corner to create topics manually, or run below command in your terminal.
      - ```docker exec -it kafka /tmp/create_topics.sh```

* Run flink job:
    - Run command: ```docker exec -it flink-jobmanager flink run --detached --python /tmp/flink_apps/test_flink_app.py```
    - Command cancel the job: ```docker exec -it flink-jobmanager flink cancel <JobID>```
* Browse to flink dashboard and select the Running Jobs to see the currently running app : http://0.0.0.0:8081/
* from Kafka UI, push some messages in source_topic using Produce Message button.
* Messages pushed from source_topic can be seen in the sink_topic under Messages tab
* Now, if any changes required to be made in flink app (test_flink_app.py) from your local IDE, then stop the running job by canceling using the Flink UI as below. 
<br>And then follow steps again starting from 10.a.
* It is also possible to run the jar in this flink container named 'docker_env-jobmanager-1'.
* Alternatively, adding the jar through flink dashboard under 'Submit New Job' and then submit the newly added jar file from the list.
* Once done with the work, you can stop all the containers
    - ```docker-compose -f docker-compose-kafka-ui-zk-flink.yml down```
    - this will also remove all the topics created under kafka and configurations if done in any of the containers. And you may need to re-run all the steps as above.


References:
* Flink CLI: https://nightlies.apache.org/flink/flink-docs-master/docs/deployment/cli/
* Built-in Flink SQL Functions: https://nightlies.apache.org/flink/flink-docs-release-1.18/docs/dev/table/functions/systemfunctions/
* Python Flink Table API: https://nightlies.apache.org/flink/flink-docs-release-1.18/docs/dev/python/table/intro_to_table_api/

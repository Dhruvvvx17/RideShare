# RideShare

Rideshare is a microservice application created as part of the **Cloud Computing course** (UE17CS352) at PES University during my 6th Semester (Spring 2020). 

The core technologies include: 
 - Flask: To creating the API's in a RESTful architecture
 - MongoDB: The underlying Database
 - RabbitMQ: Message broker between the compute instances and database orchestrator
 - AWS: Cloud platform for compute, storage, network and load balancer resources.
 - Dockers: Each Reader and Writer Program runs independently in a docker-container within the AWS instance.
 - Zookeeper: A cluster coordinator service.

### Rideshare Architecture

<p align="center">
<img src="https://user-images.githubusercontent.com/35966910/137270935-36c6eda4-ed58-439e-aa43-c8e3062cf656.png" width="600"/>
</p>

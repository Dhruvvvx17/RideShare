# RideShare

Rideshare is a microservice application to create/book a cab (done as part of the 6th Sem Cloud Computing course).
The core technologies include flask for creating the API's in a RESTful architecture, MongoDB as the database and AWS as the cloud platform.

The API's are categorized based on similarity and functionality type and are containerized in separate instances. An application load balancer is used to control traffic flow to the EC2 instances. Nginx is used as the web server and reverse proxy

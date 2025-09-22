mvn clean package
dir target
FROM tomcat:9.0-jdk11
LABEL maintainer="yourname@example.com"

# Remove default ROOT webapp
RUN rm -rf /usr/local/tomcat/webapps/*

# Copy WAR into Tomcat
COPY target/SAH.war /usr/local/tomcat/webapps/ROOT.war

EXPOSE 8080
CMD ["catalina.sh", "run"]

docker build -t smarthub-image .

docker run -d --name smarthub-container -p 8080:8080 smarthub-image
docker logs -f smarthub-container


docker login
docker tag smarthub-image yourdockerhubid/smarthub-image:v1
docker push yourdockerhubid/smarthub-image:v1


# Use a JDK base image to build the app (optional: multi-stage)
FROM openjdk:17-jdk-slim

# Set working directory inside container
WORKDIR /app

# Copy the JAR from target folder
COPY target/YourApp-0.0.1-SNAPSHOT.jar app.jar

# Expose port (if your app runs on 8080)
EXPOSE 8080

# Run the JAR
ENTRYPOINT ["java","-jar","app.jar"]

//////////////////
version: "3.9"

services:
  smarthub-app:
    image: smarthub-image:latest   # use the image you built earlier
    container_name: smarthub-app
    ports:
      - "8080:8080"                 # host:container
    depends_on:
      - smarthub-db                 # start DB before app
    environment:
      - DB_HOST=smarthub-db
      - DB_PORT=3306
      - DB_USER=root
      - DB_PASSWORD=root

  smarthub-db:
    image: mysql:8.0
    container_name: smarthub-db
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: smarthub
      MYSQL_USER: sahuser
      MYSQL_PASSWORD: sahpass
    ports:
      - "3307:3306"                 # avoid clash with local MySQL
    volumes:
      - db_data:/var/lib/mysql

volumes:
  db_data:

mvn clean package
docker build -t smarthub-image .

docker-compose up -d

docker ps

 http://localhost:8080

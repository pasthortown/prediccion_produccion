FROM openjdk:17-alpine
WORKDIR /app
COPY config.properties .
COPY credencial.jar .
ENTRYPOINT ["java", "-jar", "/app/credencial.jar"]
EXPOSE 8090

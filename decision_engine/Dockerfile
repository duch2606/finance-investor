# Etapa 1: Build
FROM gradle:8.7-jdk21 AS builder
WORKDIR /app
COPY build.gradle ./
COPY src ./src
RUN gradle shadowJar --no-daemon

# Etapa 2: Runtime
FROM openjdk:25-ea-jdk-slim
WORKDIR /app
COPY --from=builder /app/build/libs/*-all.jar ./decision-engine.jar

# Optimización de JVM para el motor de decisiones
CMD ["java", "-XX:+UseZGC", "-Xms128m", "-Xmx256m", "-jar", "decision-engine.jar"]
# Etapa 1: Construccion (Build) usando Gradle
FROM gradle:8.7-jdk21 AS builder
WORKDIR /app

# Copiamos la configuracion y el codigo fuente
COPY build.gradle ./
COPY src ./src

# Ejecutamos la tarea de Shadow para crear el Fat JAR
RUN gradle shadowJar --no-daemon

# Etapa 2: Ejecucion (Runtime) usando un entorno JDK 25 (EA)
FROM openjdk:25-ea-jdk-slim
WORKDIR /app

# El plugin Shadow de Gradle guarda el archivo compilado en build/libs/ con el sufijo -all.jar
COPY --from=builder /app/build/libs/*-all.jar ./math-engine.jar

# Ejecucion con configuracion de JVM (ZGC) para rendimiento optimizado
CMD ["java", "-XX:+UseZGC", "-Xms256m", "-Xmx512m", "-jar", "math-engine.jar"]
package com.trading;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

public class Main {
    
    // Usamos un Record para mapear los datos de forma inmutable y eficiente en memoria
    public record PriceData(String ticker, double closePrice) {}

    public static void main(String[] args) {
        System.out.println("[" + LocalDateTime.now() + "] Motor Matematico Cuantitativo (Java) Iniciado.");
        
        String dbUrl = System.getenv("DB_URL");
        String dbUser = System.getenv("DB_USER");
        String dbPassword = System.getenv("DB_PASSWORD");
        
        Connection conn = null;
        
        try {
            System.out.println("[" + LocalDateTime.now() + "] Conectando a PostgreSQL...");
            Thread.sleep(5000); // Espera de seguridad para asegurar que Postgres este listo
            
            conn = DriverManager.getConnection(dbUrl, dbUser, dbPassword);
            System.out.println("[" + LocalDateTime.now() + "] Conexion establecida.");
            
        } catch (Exception e) {
            System.err.println("[" + LocalDateTime.now() + "] Error de conexion: " + e.getMessage());
            return;
        }
        
        // Ciclo principal de procesamiento
        String[] tickers = {"SPY", "AAPL"};
        
        while (true) {
            try {
                System.out.println("--------------------------------------------------");
                for (String ticker : tickers) {
                    analyzeTicker(conn, ticker);
                }
                
                System.out.println("[" + LocalDateTime.now() + "] Calculos finalizados. Motor en espera...");
                Thread.sleep(60000); // Ejecuta los calculos cada 60 segundos
                
            } catch (InterruptedException e) {
                System.err.println("Hilo interrumpido: " + e.getMessage());
                break;
            }
        }
    }

    private static void analyzeTicker(Connection conn, String ticker) {
        // Seleccionamos los ultimos 5 cierres ordenados por fecha descendente
        String query = "SELECT ticker, close FROM daily_prices WHERE ticker = ? ORDER BY date DESC LIMIT 5";
        List<PriceData> prices = new ArrayList<>();
        
        try (PreparedStatement stmt = conn.prepareStatement(query)) {
            stmt.setString(1, ticker);
            ResultSet rs = stmt.executeQuery();
            
            while (rs.next()) {
                prices.add(new PriceData(
                    rs.getString("ticker"),
                    rs.getDouble("close")
                ));
            }
            
            if (prices.isEmpty()) {
                System.out.println("No hay datos suficientes para calcular indicadores de " + ticker);
                return;
            }
            
            // Calculo matematico: Promedio Movil Simple (SMA) de los periodos encontrados
            double sum = 0;
            for (PriceData p : prices) {
                sum += p.closePrice();
            }
            double average = sum / prices.size();
            
            // Formateo de salida a 2 decimales
            System.out.printf("[%s] Analisis de %s: Ultimo cierre = %.2f | SMA (%d dias) = %.2f%n", 
                LocalDateTime.now(), ticker, prices.get(0).closePrice(), prices.size(), average);
            
        } catch (Exception e) {
            System.err.println("Error procesando " + ticker + " (Posiblemente la tabla aun no tiene datos): " + e.getMessage());
        }
    }
}
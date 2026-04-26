package com.trading;

import java.sql.*;
import java.time.LocalDateTime;

public class DecisionMain {
    public static void main(String[] args) throws InterruptedException {
        String dbUrl = System.getenv("DB_URL");
        System.out.println("[" + LocalDateTime.now() + "] Motor de Decisiones Adaptativo Iniciado.");

        while (true) {
            try (Connection conn = DriverManager.getConnection(dbUrl, "admin", "adminpassword")) {
                processStrategy(conn, "SPY");
                processStrategy(conn, "AAPL");
            } catch (SQLException e) {
                System.err.println("Error de BD: " + e.getMessage());
            }
            Thread.sleep(30000); // Reevalúa cada 30 segundos
        }
    }

    private static void processStrategy(Connection conn, String ticker) throws SQLException {
        // 1. Obtener último precio y SMA
        double lastPrice = 0, sma = 0;
        String priceQ = "SELECT close, (SELECT avg(close) FROM (SELECT close FROM daily_prices WHERE ticker=? ORDER BY date DESC LIMIT 5) as sub) as sma FROM daily_prices WHERE ticker=? ORDER BY date DESC LIMIT 1";
        
        try (PreparedStatement st = conn.prepareStatement(priceQ)) {
            st.setString(1, ticker);
            st.setString(2, ticker);
            ResultSet rs = st.executeQuery();
            if (rs.next()) {
                lastPrice = rs.getDouble("close");
                sma = rs.getDouble("sma");
            }
        }

        // 2. Obtener último sentimiento de la IA
        String sentiment = "NEUTRAL";
        double score = 0;
        String aiQ = "SELECT sentimiento, puntuacion FROM daily_news_analysis WHERE ticker=? ORDER BY ingested_at DESC LIMIT 1";
        // Nota: Asegúrate de que el nombre de la tabla coincida con donde Gemini guarda los datos
        
        // LÓGICA DE AJUSTE DINÁMICO
        String signal = (lastPrice > sma) ? "BULLISH_TECH" : "BEARISH_TECH";
        
        System.out.printf("[%s] ESTRATEGIA ACTUALIZADA PARA %s:%n", LocalDateTime.now(), ticker);
        System.out.printf("   > Tecnica: %s (Precio: %.2f / SMA: %.2f)%n", signal, lastPrice, sma);
        
        if (lastPrice > sma) {
            System.out.println("   > POSTURA: MANTENER / INCREMENTAR (Tendencia a favor)");
        } else {
            System.out.println("   > POSTURA: DEFENSIVA (Precio por debajo de promedio)");
        }
        System.out.println("--------------------------------------------------");
    }
}
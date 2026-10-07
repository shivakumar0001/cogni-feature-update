import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { 
  Activity, TrendingUp, AlertCircle, CheckCircle, 
  XCircle, Clock, Target, Zap, BarChart3, RefreshCw 
} from "lucide-react";
import axios from "axios";

export default function FeatureMetrics() {
  const [systemHealth, setSystemHealth] = useState(null);
  const [metrics, setMetrics] = useState({ ML: [], AI: [], Analytics: [] });
  const [recentTests, setRecentTests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setRefreshing(true);
      const token = localStorage.getItem("token");
      const { data } = await axios.get("/api/feature-metrics/dashboard/summary", {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setSystemHealth(data.system_health);
      setMetrics(data.metrics_by_category);
      setRecentTests(data.recent_tests);
      setLoading(false);
    } catch (error) {
      console.error("Error fetching metrics:", error);
    } finally {
      setRefreshing(false);
    }
  };

  const getHealthColor = (status) => {
    switch(status) {
      case "healthy": return "#10b981";
      case "degraded": return "#f59e0b";
      case "critical": return "#ef4444";
      default: return "#6b7280";
    }
  };

  const getHealthIcon = (status) => {
    switch(status) {
      case "healthy": return <CheckCircle size={20} />;
      case "degraded": return <AlertCircle size={20} />;
      case "critical": return <XCircle size={20} />;
      default: return <Activity size={20} />;
    }
  };

  const getMetricColor = (value) => {
    if (!value) return "#6b7280";
    if (value >= 90) return "#10b981";
    if (value >= 75) return "#3b82f6";
    if (value >= 60) return "#f59e0b";
    return "#ef4444";
  };

  const MetricCard = ({ label, value, icon: Icon, suffix = "%" }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      style={{
        background: "linear-gradient(135deg, #1e293b 0%, #0f172a 100%)",
        borderRadius: 16,
        padding: 20,
        border: "1px solid rgba(255,255,255,0.05)"
      }}
    >
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
        <span style={{ color: "#94a3b8", fontSize: 14 }}>{label}</span>
        <Icon size={18} style={{ color: "#6366f1" }} />
      </div>
      <div style={{ fontSize: 32, fontWeight: 700, color: getMetricColor(value) }}>
        {value !== null && value !== undefined ? `${value}${suffix}` : "N/A"}
      </div>
    </motion.div>
  );

  const FeatureCard = ({ feature }) => (
    <motion.div
      whileHover={{ scale: 1.02 }}
      style={{
        background: "linear-gradient(135deg, #1e293b 0%, #0f172a 100%)",
        borderRadius: 16,
        padding: 24,
        border: "1px solid rgba(255,255,255,0.05)",
        position: "relative",
        overflow: "hidden"
      }}
    >
      {/* Health indicator bar */}
      <div style={{
        position: "absolute",
        top: 0,
        left: 0,
        right: 0,
        height: 4,
        background: getHealthColor(feature.health_status)
      }} />

      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
        <h3 style={{ fontSize: 18, fontWeight: 600, color: "#f1f5f9", margin: 0 }}>
          {feature.feature_name}
        </h3>
        <div style={{ 
          display: "flex", 
          alignItems: "center", 
          gap: 6,
          padding: "6px 12px",
          borderRadius: 8,
          background: `${getHealthColor(feature.health_status)}15`,
          color: getHealthColor(feature.health_status),
          fontSize: 12,
          fontWeight: 600
        }}>
          {getHealthIcon(feature.health_status)}
          <span style={{ textTransform: "capitalize" }}>{feature.health_status}</span>
        </div>
      </div>

      {/* Metrics Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 16 }}>
        <div>
          <div style={{ fontSize: 12, color: "#64748b", marginBottom: 4 }}>Accuracy</div>
          <div style={{ fontSize: 24, fontWeight: 700, color: getMetricColor(feature.accuracy) }}>
            {feature.accuracy !== null ? `${feature.accuracy}%` : "N/A"}
          </div>
        </div>
        <div>
          <div style={{ fontSize: 12, color: "#64748b", marginBottom: 4 }}>F1 Score</div>
          <div style={{ fontSize: 24, fontWeight: 700, color: getMetricColor(feature.f1_score) }}>
            {feature.f1_score !== null ? `${feature.f1_score}%` : "N/A"}
          </div>
        </div>
        <div>
          <div style={{ fontSize: 12, color: "#64748b", marginBottom: 4 }}>Precision</div>
          <div style={{ fontSize: 20, fontWeight: 600, color: getMetricColor(feature.precision) }}>
            {feature.precision !== null ? `${feature.precision}%` : "N/A"}
          </div>
        </div>
        <div>
          <div style={{ fontSize: 12, color: "#64748b", marginBottom: 4 }}>Recall</div>
          <div style={{ fontSize: 20, fontWeight: 600, color: getMetricColor(feature.recall) }}>
            {feature.recall !== null ? `${feature.recall}%` : "N/A"}
          </div>
        </div>
      </div>

      {/* Stats */}
      <div style={{ 
        display: "flex", 
        gap: 16, 
        paddingTop: 16, 
        borderTop: "1px solid rgba(255,255,255,0.05)",
        fontSize: 13,
        color: "#94a3b8"
      }}>
        <div style={{ flex: 1 }}>
          <div>Success Rate</div>
          <div style={{ fontWeight: 600, color: getMetricColor(feature.success_rate), marginTop: 4 }}>
            {feature.success_rate !== null ? `${feature.success_rate}%` : "N/A"}
          </div>
        </div>
        <div style={{ flex: 1 }}>
          <div>Avg Response</div>
          <div style={{ fontWeight: 600, color: "#f1f5f9", marginTop: 4 }}>
            {feature.avg_response_time !== null ? `${feature.avg_response_time}s` : "N/A"}
          </div>
        </div>
        <div style={{ flex: 1 }}>
          <div>Requests</div>
          <div style={{ fontWeight: 600, color: "#f1f5f9", marginTop: 4 }}>
            {feature.total_requests}
          </div>
        </div>
      </div>
    </motion.div>
  );

  if (loading) {
    return (
      <div style={{ padding: 40, color: "#e4e4e7", background: "#09090b", minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ textAlign: "center" }}>
          <div style={{ width: 48, height: 48, border: "4px solid rgba(99,102,241,.3)", borderTopColor: "#6366f1", borderRadius: "50%", animation: "spin 0.8s linear infinite", margin: "0 auto 16px" }} />
          <div style={{ fontSize: 16, color: "#64748b" }}>Loading Feature Metrics...</div>
        </div>
      </div>
    );
  }

  const allFeatures = [
    ...(metrics.ML || []),
    ...(metrics.AI || []),
    ...(metrics.Analytics || [])
  ];

  const filteredFeatures = selectedCategory === "all" 
    ? allFeatures
    : metrics[selectedCategory] || [];

  return (
    <div style={{ 
      padding: 40, 
      color: "#e4e4e7", 
      background: "#09090b", 
      minHeight: "100vh",
      overflowY: "auto"
    }}>
      {/* Header */}
      <div style={{ marginBottom: 32 }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 8 }}>
          <h1 style={{ fontSize: 32, fontWeight: 700, color: "#f1f5f9", margin: 0, display: "flex", alignItems: "center", gap: 12 }}>
            <Activity size={32} style={{ color: "#6366f1" }} />
            Feature Performance Metrics
          </h1>
          <button
            onClick={fetchDashboardData}
            disabled={refreshing}
            style={{
              padding: "10px 20px",
              borderRadius: 10,
              border: "none",
              background: refreshing ? "#374151" : "linear-gradient(135deg,#6366f1,#8b5cf6)",
              color: "#fff",
              fontSize: 14,
              fontWeight: 600,
              cursor: refreshing ? "not-allowed" : "pointer",
              display: "flex",
              alignItems: "center",
              gap: 8
            }}
          >
            <RefreshCw size={16} style={{ animation: refreshing ? "spin 1s linear infinite" : "none" }} />
            {refreshing ? "Refreshing..." : "Refresh"}
          </button>
        </div>
        <p style={{ fontSize: 16, color: "#64748b", margin: 0 }}>
          Real-time accuracy, F1 scores, and health status for all AI/ML features
        </p>
      </div>

      {/* System Health Overview */}
      {systemHealth && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          style={{
            background: `linear-gradient(135deg, ${getHealthColor(systemHealth.overall_health)}15 0%, #0f172a 100%)`,
            borderRadius: 20,
            padding: 32,
            marginBottom: 32,
            border: `2px solid ${getHealthColor(systemHealth.overall_health)}40`
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 24 }}>
            <div style={{ 
              width: 64, 
              height: 64, 
              borderRadius: 16,
              background: `${getHealthColor(systemHealth.overall_health)}20`,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: getHealthColor(systemHealth.overall_health)
            }}>
              {getHealthIcon(systemHealth.overall_health)}
            </div>
            <div>
              <h2 style={{ fontSize: 24, fontWeight: 700, color: "#f1f5f9", margin: 0, marginBottom: 4 }}>
                System Health: <span style={{ color: getHealthColor(systemHealth.overall_health), textTransform: "capitalize" }}>
                  {systemHealth.overall_health}
                </span>
              </h2>
              <p style={{ fontSize: 14, color: "#64748b", margin: 0 }}>
                {systemHealth.healthy_features} healthy • {systemHealth.degraded_features} degraded • {systemHealth.critical_features} critical
              </p>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 16 }}>
            <MetricCard label="Avg Accuracy" value={systemHealth.avg_accuracy} icon={Target} />
            <MetricCard label="Avg F1 Score" value={systemHealth.avg_f1_score} icon={TrendingUp} />
            <MetricCard label="Success Rate" value={systemHealth.avg_success_rate} icon={CheckCircle} />
            <MetricCard label="Total Requests" value={systemHealth.total_requests} icon={BarChart3} suffix="" />
          </div>
        </motion.div>
      )}

      {/* Category Filter */}
      <div style={{ display: "flex", gap: 12, marginBottom: 24, flexWrap: "wrap" }}>
        {["all", "ML", "AI", "Analytics"].map(category => (
          <button
            key={category}
            onClick={() => setSelectedCategory(category)}
            style={{
              padding: "10px 20px",
              borderRadius: 10,
              border: selectedCategory === category ? "2px solid #6366f1" : "1px solid rgba(255,255,255,0.1)",
              background: selectedCategory === category ? "#6366f115" : "#1e293b",
              color: selectedCategory === category ? "#6366f1" : "#94a3b8",
              fontSize: 14,
              fontWeight: 600,
              cursor: "pointer",
              textTransform: "capitalize"
            }}
          >
            {category}
            {category !== "all" && (
              <span style={{ 
                marginLeft: 8,
                padding: "2px 8px",
                borderRadius: 6,
                background: selectedCategory === category ? "#6366f1" : "#374151",
                color: "#fff",
                fontSize: 12
              }}>
                {metrics[category]?.length || 0}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Features Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(400px, 1fr))", gap: 24, marginBottom: 32 }}>
        {filteredFeatures.map((feature, idx) => (
          <FeatureCard key={idx} feature={feature} />
        ))}
      </div>

      {filteredFeatures.length === 0 && (
        <div style={{ textAlign: "center", padding: 60, color: "#64748b" }}>
          <Activity size={48} style={{ marginBottom: 16, opacity: 0.5 }} />
          <div style={{ fontSize: 18, fontWeight: 600, marginBottom: 8 }}>No features found</div>
          <div style={{ fontSize: 14 }}>No features match the selected category</div>
        </div>
      )}

      {/* Recent Tests */}
      {recentTests.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          style={{
            background: "linear-gradient(135deg, #1e293b 0%, #0f172a 100%)",
            borderRadius: 16,
            padding: 24,
            border: "1px solid rgba(255,255,255,0.05)"
          }}
        >
          <h3 style={{ fontSize: 20, fontWeight: 700, color: "#f1f5f9", marginBottom: 16, display: "flex", alignItems: "center", gap: 8 }}>
            <Clock size={20} style={{ color: "#6366f1" }} />
            Recent Tests
          </h3>
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", fontSize: 14, borderCollapse: "collapse" }}>
              <thead>
                <tr style={{ borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
                  <th style={{ padding: 12, textAlign: "left", color: "#64748b", fontWeight: 600 }}>Feature</th>
                  <th style={{ padding: 12, textAlign: "left", color: "#64748b", fontWeight: 600 }}>Type</th>
                  <th style={{ padding: 12, textAlign: "center", color: "#64748b", fontWeight: 600 }}>Status</th>
                  <th style={{ padding: 12, textAlign: "right", color: "#64748b", fontWeight: 600 }}>Accuracy</th>
                  <th style={{ padding: 12, textAlign: "right", color: "#64748b", fontWeight: 600 }}>F1 Score</th>
                  <th style={{ padding: 12, textAlign: "right", color: "#64748b", fontWeight: 600 }}>Time</th>
                </tr>
              </thead>
              <tbody>
                {recentTests.slice(0, 10).map((test, idx) => (
                  <tr key={idx} style={{ borderBottom: "1px solid rgba(255,255,255,0.03)" }}>
                    <td style={{ padding: 12, color: "#f1f5f9" }}>{test.feature_name}</td>
                    <td style={{ padding: 12, color: "#94a3b8", textTransform: "capitalize" }}>{test.test_type}</td>
                    <td style={{ padding: 12, textAlign: "center" }}>
                      <span style={{
                        padding: "4px 12px",
                        borderRadius: 6,
                        background: test.test_passed ? "#10b98115" : "#ef444415",
                        color: test.test_passed ? "#10b981" : "#ef4444",
                        fontSize: 12,
                        fontWeight: 600
                      }}>
                        {test.test_passed ? "✓ Passed" : "✗ Failed"}
                      </span>
                    </td>
                    <td style={{ padding: 12, textAlign: "right", color: getMetricColor(test.accuracy), fontWeight: 600 }}>
                      {test.accuracy !== null ? `${test.accuracy}%` : "—"}
                    </td>
                    <td style={{ padding: 12, textAlign: "right", color: getMetricColor(test.f1_score), fontWeight: 600 }}>
                      {test.f1_score !== null ? `${test.f1_score}%` : "—"}
                    </td>
                    <td style={{ padding: 12, textAlign: "right", color: "#94a3b8" }}>
                      {test.execution_time !== null ? `${test.execution_time}s` : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>
      )}

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

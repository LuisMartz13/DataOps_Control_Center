import { useEffect, useState } from "react";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from "recharts";

import jsPDF from "jspdf";
import html2canvas from "html2canvas";

import "./App.css";

function App() {

  const [isAuthenticated, setIsAuthenticated] =
    useState(false);

  const [loginData, setLoginData] = useState({
    username: "",
    password: ""
  });

  const [connections, setConnections] = useState([]);

  const [metrics, setMetrics] = useState([]);

  const [queries, setQueries] = useState([]);

  const [alerts, setAlerts] = useState([]);

  const [recommendations, setRecommendations] =
    useState([]);

  const [formData, setFormData] = useState({
    nombre: "",
    motor: "",
    host: "",
    port: "",
    database_name: "",
    user_name: "",
    status: ""
  });

  async function login(e) {

    e.preventDefault();

    const response = await fetch(
      "http://127.0.0.1:8000/login",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(loginData)
      }
    );

    const data = await response.json();

    if (data.error) {

      alert(data.error);

      return;
    }

    localStorage.setItem(
      "token",
      data.access_token
    );

    localStorage.setItem(
      "isAuthenticated",
      "true"
    );

    setIsAuthenticated(true);
  }

  function getAuthHeaders() {

    const token = localStorage.getItem(
      "token"
    );

    return {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`
    };
  }

  async function loadConnections() {

    const response = await fetch(
      "http://127.0.0.1:8000/connections",
      {
        headers: getAuthHeaders()
      }
    );

    const data = await response.json();

    setConnections(data);
  }

  async function loadMetrics() {

    const response = await fetch(
      "http://127.0.0.1:8000/metrics",
      {
        headers: getAuthHeaders()
      }
    );

    const data = await response.json();

    setMetrics(data);
  }

  async function loadQueries() {

    const response = await fetch(
      "http://127.0.0.1:8000/queries",
      {
        headers: getAuthHeaders()
      }
    );

    const data = await response.json();

    setQueries(data);
  }

  async function loadAlerts() {

    const response = await fetch(
      "http://127.0.0.1:8000/alerts",
      {
        headers: getAuthHeaders()
      }
    );

    const data = await response.json();

    setAlerts(data);
  }

  async function loadRecommendations() {

    const response = await fetch(
      "http://127.0.0.1:8000/ai_recommendations",
      {
        headers: getAuthHeaders()
      }
    );

    const data = await response.json();

    setRecommendations(data);
  }

  async function createConnection(e) {

    e.preventDefault();

    await fetch(
      "http://127.0.0.1:8000/connections",
      {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({
          ...formData,
          port: Number(formData.port)
        })
      }
    );

    loadConnections();

    setFormData({
      nombre: "",
      motor: "",
      host: "",
      port: "",
      database_name: "",
      user_name: "",
      status: ""
    });
  }

  async function deleteConnection(id) {

    await fetch(
      `http://127.0.0.1:8000/connections/${id}`,
      {
        method: "DELETE",
        headers: getAuthHeaders()
      }
    );

    loadConnections();
  }

  async function exportPDF() {

    const input = document.body;

    const canvas = await html2canvas(input);

    const imgData = canvas.toDataURL("image/png");

    const pdf = new jsPDF("p", "mm", "a4");

    const pdfWidth =
      pdf.internal.pageSize.getWidth();

    const pdfHeight =
      (canvas.height * pdfWidth) / canvas.width;

    pdf.addImage(
      imgData,
      "PNG",
      0,
      0,
      pdfWidth,
      pdfHeight
    );

    pdf.save("dataops_dashboard.pdf");
  }

  const averageCPU =
    metrics.length > 0
      ? (
          metrics.reduce(
            (acc, item) => acc + item.cpu,
            0
          ) / metrics.length
        ).toFixed(1)
      : 0;

  const criticalQueries =
    queries.filter(
      (query) =>
        query.category === "CRITICAL"
    ).length;

  useEffect(() => {

    const auth =
      localStorage.getItem(
        "isAuthenticated"
      );

    if (auth === "true") {

      setIsAuthenticated(true);
    }

    loadConnections();

    loadMetrics();

    loadQueries();

    loadAlerts();

    loadRecommendations();

    const interval = setInterval(() => {

      loadMetrics();

      loadQueries();

      loadAlerts();

      loadRecommendations();

    }, 5000);

    return () => clearInterval(interval);

  }, []);

  if (!isAuthenticated) {

    return (

      <div className="login-container">

        <div className="login-card">

          <h1>DataOps Login</h1>

          <form onSubmit={login}>

            <input
              placeholder="Usuario"
              value={loginData.username}
              onChange={(e) =>
                setLoginData({
                  ...loginData,
                  username: e.target.value
                })
              }
            />

            <input
              type="password"
              placeholder="Contraseña"
              value={loginData.password}
              onChange={(e) =>
                setLoginData({
                  ...loginData,
                  password: e.target.value
                })
              }
            />

            <button type="submit">
              Iniciar sesión
            </button>

          </form>

        </div>

      </div>
    );
  }

  return (

    <div className="container">

      <h1>
        Centro de control de DataOps
      </h1>

      <button
        onClick={() => {

          localStorage.removeItem(
            "isAuthenticated"
          );

          localStorage.removeItem(
            "token"
          );

          setIsAuthenticated(false);

        }}
      >
        Cerrar sesión
      </button>

      <button onClick={exportPDF}>
        Exportar PDF
      </button>

      <div className="kpi-container">

        <div className="kpi-card">

          <h3>Conexiones</h3>

          <h2>{connections.length}</h2>

        </div>

        <div className="kpi-card">

          <h3>Alertas</h3>

          <h2>{alerts.length}</h2>

        </div>

        <div className="kpi-card">

          <h3>Queries críticas</h3>

          <h2>{criticalQueries}</h2>

        </div>

        <div className="kpi-card">

          <h3>CPU promedio</h3>

          <h2>{averageCPU}%</h2>

        </div>

      </div>

      <form onSubmit={createConnection}>

        <input
          placeholder="Nombre"
          value={formData.nombre}
          onChange={(e) =>
            setFormData({
              ...formData,
              nombre: e.target.value
            })
          }
        />

        <input
          placeholder="Motor"
          value={formData.motor}
          onChange={(e) =>
            setFormData({
              ...formData,
              motor: e.target.value
            })
          }
        />

        <input
          placeholder="Anfitrión"
          value={formData.host}
          onChange={(e) =>
            setFormData({
              ...formData,
              host: e.target.value
            })
          }
        />

        <input
          placeholder="Puerto"
          value={formData.port}
          onChange={(e) =>
            setFormData({
              ...formData,
              port: e.target.value
            })
          }
        />

        <input
          placeholder="Base de datos"
          value={formData.database_name}
          onChange={(e) =>
            setFormData({
              ...formData,
              database_name: e.target.value
            })
          }
        />

        <input
          placeholder="Usuario"
          value={formData.user_name}
          onChange={(e) =>
            setFormData({
              ...formData,
              user_name: e.target.value
            })
          }
        />

        <input
          placeholder="Estado"
          value={formData.status}
          onChange={(e) =>
            setFormData({
              ...formData,
              status: e.target.value
            })
          }
        />

        <button type="submit">
          Guardar conexión
        </button>

      </form>

      <h2>Alert Engine</h2>

      <div className="alerts-container">

        {alerts.map((alert) => (

          <div
            key={alert.id}
            className={
              alert.severity === "CRITICAL"
                ? "alert-critical"
                : "alert-warning"
            }
          >

            <h3>{alert.title}</h3>

            <p>{alert.message}</p>

            <small>{alert.source}</small>

          </div>

        ))}

      </div>

      <table>

        <thead>

          <tr>

            <th>ID</th>
            <th>Nombre</th>
            <th>Motor</th>
            <th>Host</th>
            <th>Puerto</th>
            <th>Estado</th>
            <th>Acciones</th>

          </tr>

        </thead>

        <tbody>

          {connections.map((connection) => (

            <tr key={connection.id}>

              <td>{connection.id}</td>
              <td>{connection.nombre}</td>
              <td>{connection.motor}</td>
              <td>{connection.host}</td>
              <td>{connection.port}</td>
              <td>{connection.status}</td>

              <td>

                <button
                  onClick={() =>
                    deleteConnection(
                      connection.id
                    )
                  }
                >
                  Eliminar
                </button>

              </td>

            </tr>

          ))}

        </tbody>

      </table>

      <h2>Métricas</h2>

      <div className="metrics-container">

        {metrics.map((metric) => (

          <div
            className="metric-card"
            key={metric.id}
          >

            <h3>
              DB ID: {metric.db_id}
            </h3>

            <p>
              CPU:
              {" "}
              {metric.cpu.toFixed(2)}%
            </p>

            <p>
              RAM:
              {" "}
              {metric.memory.toFixed(2)}%
            </p>

            <p>
              Connections:
              {" "}
              {metric.connections}
            </p>

            <p>
              Locks:
              {" "}
              {metric.locks}
            </p>

            <p>
              Deadlocks:
              {" "}
              {metric.deadlocks}
            </p>

            <p>
              Disk:
              {" "}
              {metric.disk_usage.toFixed(2)}%
            </p>

          </div>

        ))}

      </div>

      <div className="chart-container">

        <h2>Uso de CPU</h2>

        <ResponsiveContainer
          width="100%"
          height={300}
        >

          <LineChart data={metrics}>

            <CartesianGrid
              strokeDasharray="3 3"
            />

            <XAxis dataKey="id" />

            <YAxis />

            <Tooltip />

            <Line
              type="monotone"
              dataKey="cpu"
              stroke="#38bdf8"
            />

          </LineChart>

        </ResponsiveContainer>

      </div>

      <div className="chart-container">

        <h2>Uso de RAM</h2>

        <ResponsiveContainer
          width="100%"
          height={300}
        >

          <LineChart data={metrics}>

            <CartesianGrid
              strokeDasharray="3 3"
            />

            <XAxis dataKey="id" />

            <YAxis />

            <Tooltip />

            <Line
              type="monotone"
              dataKey="memory"
              stroke="#818cf8"
            />

          </LineChart>

        </ResponsiveContainer>

      </div>

      <h2>
        AI Optimization Advisor
      </h2>

      <div className="recommendations-container">

        {recommendations.map(
          (recommendation) => (

            <div
              className="recommendation-card"
              key={recommendation.id}
            >

              <h3>
                {recommendation.title}
              </h3>

              <p>
                {
                  recommendation.recommendation
                }
              </p>

              <span>
                {recommendation.category}
              </span>

              <h4>
                {recommendation.severity}
              </h4>

            </div>

          )
        )}

      </div>

      <h2>Slow Query Analyzer</h2>

      <table>

        <thead>

          <tr>

            <th>ID</th>

            <th>Query</th>

            <th>Duración</th>

            <th>Filas</th>

            <th>Categoría</th>

          </tr>

        </thead>

        <tbody>

          {queries.map((query) => (

            <tr key={query.id}>

              <td>{query.id}</td>

              <td>{query.query_text}</td>

              <td>
                {query.duration_ms} ms
              </td>

              <td>
                {query.rows_returned}
              </td>

              <td>

                <span
                  className={
                    query.category.toLowerCase()
                  }
                >

                  {query.category}

                </span>

              </td>

            </tr>

          ))}

        </tbody>

      </table>

    </div>
  );
}

export default App;
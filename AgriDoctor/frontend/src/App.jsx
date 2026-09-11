import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { useEffect, useState } from 'react';
import api from './services/api';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import ProtectedRoute from './components/ProtectedRoute';
import CameraScanner from './components/CameraScanner';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ANDHRA_PRADESH, ANDHRA_PRADESH_DISTRICTS, ANDHRA_PRADESH_LOCATIONS } from './data/andhraPradeshLocations';

function LandingPage() {
  return (
    <div className="page-shell">
      <section className="hero card">
        <div>
          <p className="eyebrow">Smart farming for Indian farmers</p>
          <h1>AgriDoctor</h1>
          <p>
            Diagnose crop disease, analyze soil, track weather, and receive practical recommendations
            for healthier harvests.
          </p>
          <div className="hero-actions">
            <a href="/login" className="primary-button">Login</a>
            <a href="/register" className="secondary-button">Register</a>
          </div>
        </div>
      </section>

      <section className="grid-3">
        <div className="card feature">
          <h3>Disease detection</h3>
          <p>Upload crop images and use the advisory workflow to assess plant health.</p>
        </div>
        <div className="card feature">
          <h3>Soil analysis</h3>
          <p>Capture soil details and get crop suitability and health recommendations.</p>
        </div>
        <div className="card feature">
          <h3>Smart insights</h3>
          <p>Blend weather, disease, and field context into practical action steps.</p>
        </div>
      </section>
    </div>
  );
}

function LoginPage() {
  const { login } = useAuth();
  const [form, setForm] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await api.post('/auth/login', form);
      const { token, user } = response.data;
      login(user, token);
      window.location.href = '/dashboard';
    } catch (err) {
      setError(err.response?.data?.error || err.response?.data?.message || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-shell form-page">
      <form className="card form-card" onSubmit={handleSubmit}>
        <h2>Login</h2>
        {error && <div className="error-box">{error}</div>}
        <label>
          Email
          <input name="email" type="email" value={form.email} onChange={handleChange} required />
        </label>
        <label>
          Password
          <input name="password" type="password" value={form.password} onChange={handleChange} required />
        </label>
        <button className="primary-button" type="submit" disabled={loading}>
          {loading ? 'Signing in...' : 'Login'}
        </button>
      </form>
    </div>
  );
}

function RegisterPage() {
  const { login } = useAuth();
  const [form, setForm] = useState({
    name: '',
    mobile_number: '',
    email: '',
    password: '',
    state: '',
    district: '',
    village: '',
    farm_area: 1,
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  };

  const handleLocationChange = (event) => {
    const { name, value } = event.target;
    setForm((current) => ({
      ...current,
      [name]: value,
      ...(name === 'state' ? { district: '', village: '' } : {}),
      ...(name === 'district' ? { village: '' } : {}),
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await api.post('/auth/register', {
        ...form,
        farm_area: Number(form.farm_area),
      });
      const { token, user } = response.data;
      login(user, token);
      window.location.href = '/';
    } catch (err) {
      setError(err.response?.data?.error || err.response?.data?.message || 'Registration failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-shell form-page">
      <form className="card form-card" onSubmit={handleSubmit}>
        <h2>Register</h2>
        {error && <div className="error-box">{error}</div>}
        <label>
          Full name
          <input name="name" value={form.name} onChange={handleChange} required />
        </label>
        <label>
          Mobile number
          <input name="mobile_number" value={form.mobile_number} onChange={handleChange} required />
        </label>
        <label>
          Email
          <input name="email" type="email" value={form.email} onChange={handleChange} required />
        </label>
        <label>
          Password
          <input name="password" type="password" value={form.password} onChange={handleChange} required />
        </label>
        <div className="two-col">
          <label>
            State
            <select name="state" value={form.state} onChange={handleLocationChange} required>
              <option value="">Select state</option>
              <option value={ANDHRA_PRADESH}>{ANDHRA_PRADESH}</option>
            </select>
          </label>
          <label>
            District
            <select name="district" value={form.district} onChange={handleLocationChange} required disabled={!form.state}>
              <option value="">Select district</option>
              {ANDHRA_PRADESH_DISTRICTS.map((district) => (
                <option key={district} value={district}>{district}</option>
              ))}
            </select>
          </label>
        </div>
        <div className="two-col">
          <label>
            Village
            <select name="village" value={form.village} onChange={handleLocationChange} required disabled={!form.district}>
              <option value="">Select village</option>
              {(ANDHRA_PRADESH_LOCATIONS[form.district] || []).map((village) => (
                <option key={village} value={village}>{village}</option>
              ))}
            </select>
          </label>
          <label>
            Farm area (acres)
            <input name="farm_area" type="number" min="0" step="0.1" value={form.farm_area} onChange={handleChange} required />
          </label>
        </div>
        <button className="primary-button" type="submit" disabled={loading}>
          {loading ? 'Creating account...' : 'Register'}
        </button>
      </form>
    </div>
  );
}

function DashboardPage() {
  const { user, logout } = useAuth();
  const [dashboard, setDashboard] = useState(null);
  const [soilForm, setSoilForm] = useState({
    nitrogen: '',
    phosphorus: '',
    potassium: '',
    ph: '',
    moisture: '',
    temperature: '',
    rainfall: '',
  });
  const [cropForm, setCropForm] = useState({
    nitrogen: '',
    phosphorus: '',
    potassium: '',
    temperature: '',
    humidity: '',
    ph: '',
    rainfall: '',
  });
  const [soilResult, setSoilResult] = useState(null);
  const [cropResult, setCropResult] = useState(null);
  const [diseaseResult, setDiseaseResult] = useState(null);
  const [weatherResult, setWeatherResult] = useState(null);
  const [scanRecommendation, setScanRecommendation] = useState(null);
  const [diseaseFile, setDiseaseFile] = useState(null);
  const [diseaseCrop, setDiseaseCrop] = useState('Groundnut');
  const [error, setError] = useState('');
  const [loadingAction, setLoadingAction] = useState('');

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        const response = await api.get('/farmer/dashboard');
        setDashboard(response.data);
      } catch (err) {
        setError('Unable to load dashboard data right now.');
      }
    };

    if (user) {
      loadDashboard();
    }
  }, [user]);

  const handleSoilChange = (event) => {
    const { name, value } = event.target;
    setSoilForm((current) => ({ ...current, [name]: value === '' ? '' : Number(value) }));
  };

  const handleCropChange = (event) => {
    const { name, value } = event.target;
    setCropForm((current) => ({ ...current, [name]: Number(value) }));
  };

  const handleSoilSubmit = async (event) => {
    event.preventDefault();
    if (Object.values(soilForm).some((value) => value === '')) {
      setError('Enter all soil values from a laboratory report before analyzing.');
      return;
    }
    setError('');
    setLoadingAction('soil');

    try {
      const response = await api.post('/soil/analyze', soilForm);
      setSoilResult(response.data.result);
    } catch (err) {
      setError(err.response?.data?.error || 'Soil analysis failed.');
    } finally {
      setLoadingAction('');
    }
  };

  const handleCropSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setLoadingAction('crop');

    try {
      const response = await api.post('/crop/recommend', cropForm);
      setCropResult(response.data.result);
    } catch (err) {
      setError(err.response?.data?.error || 'Crop recommendation failed.');
    } finally {
      setLoadingAction('');
    }
  };

  const handleDiseaseSubmit = async (event) => {
    event.preventDefault();
    if (!diseaseFile) {
      setError('Please choose an image before scanning.');
      return;
    }

    setError('');
    setLoadingAction('disease');

    try {
      const formData = new FormData();
      formData.append('image', diseaseFile);
      formData.append('crop', diseaseCrop);
      const response = await api.post('/disease/predict', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      const prediction = response.data.result;
      setDiseaseResult(prediction);
      setDashboard((current) => ({ ...current, disease_risk: prediction.weather_risk }));

      const coordinates = await new Promise((resolve) => {
        if (!navigator.geolocation) {
          resolve({ lat: 17.3850, lon: 78.4867 });
          return;
        }
        navigator.geolocation.getCurrentPosition(
          (position) => resolve({ lat: position.coords.latitude, lon: position.coords.longitude }),
          () => resolve({ lat: 17.3850, lon: 78.4867 }),
          { enableHighAccuracy: false, timeout: 5000 }
        );
      });

      const weatherResponse = await api.get('/weather/current', { params: coordinates });
      const weather = weatherResponse.data;
      setWeatherResult(weather);
      const recommendationResponse = await api.get('/recommendations', {
        params: {
          crop: prediction.crop,
          disease: prediction.disease,
          humidity: weather.humidity,
          forecast: weather.forecast,
        },
      });
      setScanRecommendation(recommendationResponse.data.recommendations?.[0] || null);
      setDashboard((current) => ({ ...current, weather }));
    } catch (err) {
      setError(err.response?.data?.error || 'Disease scan failed.');
    } finally {
      setLoadingAction('');
    }
  };

  return (
    <div className="page-shell dashboard-shell">
      <div className="card welcome-card">
        <div>
          <p className="eyebrow">Farmer dashboard</p>
          <h2>Welcome, {user?.name || 'Farmer'}</h2>
          <p>
            {user?.district ? `${user.district}, ${user.state}` : 'Your field dashboard is ready.'}
          </p>
        </div>
        <button className="secondary-button" onClick={logout}>Logout</button>
      </div>

      {error && <div className="error-box">{error}</div>}

      <div className="stats-grid">
        <div className="card stat-card">
          <span>Temperature</span>
          <strong>{dashboard?.weather?.temperature != null ? `${dashboard.weather.temperature}°C` : '—'}</strong>
        </div>
        <div className="card stat-card">
          <span>Humidity</span>
          <strong>{dashboard?.weather?.humidity != null ? `${dashboard.weather.humidity}%` : '—'}</strong>
        </div>
        <div className="card stat-card">
          <span>Disease risk</span>
          <strong>{dashboard?.disease_risk ?? '—'}</strong>
        </div>
        <div className="card stat-card">
          <span>Notifications</span>
          <strong>{dashboard?.notifications ?? '—'}</strong>
        </div>
      </div>

      {(diseaseResult || weatherResult || scanRecommendation) && (
        <section className="card scan-insights">
          <div>
            <p className="eyebrow">Latest scan insights</p>
            <h3>{diseaseResult ? `${diseaseResult.crop} - ${diseaseResult.disease}` : 'Field report'}</h3>
          </div>
          <div className="insight-grid">
            {diseaseResult && (
              <div className="insight-panel">
                <h4>Disease and pesticides</h4>
                <p><strong>Severity:</strong> {diseaseResult.severity}</p>
                {diseaseResult.treatments?.map((treatment) => (
                  <p key={`${treatment.active_ingredient}-${treatment.product_name}`}>
                    <strong>{treatment.product_name}</strong><br />{treatment.active_ingredient}
                  </p>
                ))}
              </div>
            )}
            {weatherResult && (
              <div className="insight-panel">
                <h4>Weather report</h4>
                {weatherResult.available === false ? <p>{weatherResult.message}</p> : (
                  <>
                    <p><strong>Condition:</strong> {weatherResult.condition}</p>
                    <p><strong>Temperature:</strong> {weatherResult.temperature}°C</p>
                    <p><strong>Humidity:</strong> {weatherResult.humidity}%</p>
                    <p><strong>Forecast:</strong> {weatherResult.forecast}</p>
                  </>
                )}
              </div>
            )}
            {scanRecommendation && (
              <div className="insight-panel">
                <h4>Recommendations</h4>
                {scanRecommendation.recommendation?.map((item) => <p key={item}>{item}</p>)}
              </div>
            )}
            <div className="insight-panel">
              <h4>Soil analysis</h4>
              {soilResult ? (
                <>
                  <p><strong>Condition:</strong> {soilResult.soil_condition}</p>
                  <p><strong>Status:</strong> {soilResult.nutrient_status}</p>
                </>
              ) : <p>Enter soil readings below to add a soil report. A leaf image cannot measure soil nutrients.</p>}
            </div>
          </div>
        </section>
      )}

      <div className="dashboard-grid">
        <form className="card form-card" onSubmit={handleSoilSubmit}>
          <h3>Soil analysis</h3>
          <details className="soil-guide">
            <summary>Where can I get these soil values?</summary>
            <p>Take a soil sample to your nearest government soil-testing laboratory or agriculture office and ask for a Soil Health Card.</p>
            <p>Copy N, P, and K in kg/ha, pH as shown, moisture as a percentage, temperature in °C, and recent rainfall in mm.</p>
            <p>Do not guess these values. If you do not have a report, leave this analysis until your soil is tested.</p>
            <a href="https://soilhealth.dac.gov.in/" target="_blank" rel="noreferrer">Open Soil Health Card portal</a>
          </details>
          <div className="two-col">
            <label>Nitrogen (kg/ha)<input name="nitrogen" type="number" min="0" value={soilForm.nitrogen} onChange={handleSoilChange} required /></label>
            <label>Phosphorus (kg/ha)<input name="phosphorus" type="number" min="0" value={soilForm.phosphorus} onChange={handleSoilChange} required /></label>
          </div>
          <div className="two-col">
            <label>Potassium (kg/ha)<input name="potassium" type="number" min="0" value={soilForm.potassium} onChange={handleSoilChange} required /></label>
            <label>pH<input name="ph" type="number" min="0" max="14" step="0.1" value={soilForm.ph} onChange={handleSoilChange} required /></label>
          </div>
          <div className="two-col">
            <label>Moisture (%)<input name="moisture" type="number" min="0" max="100" value={soilForm.moisture} onChange={handleSoilChange} required /></label>
            <label>Temperature (°C)<input name="temperature" type="number" value={soilForm.temperature} onChange={handleSoilChange} required /></label>
          </div>
          <label>Recent rainfall (mm)<input name="rainfall" type="number" min="0" value={soilForm.rainfall} onChange={handleSoilChange} required /></label>
          <button className="primary-button" type="submit" disabled={loadingAction === 'soil'}>{loadingAction === 'soil' ? 'Analyzing...' : 'Analyze soil'}</button>
          {soilResult && (
            <div className="result-box">
              <h4>Result</h4>
              <p><strong>Condition:</strong> {soilResult.soil_condition}</p>
              <p><strong>Status:</strong> {soilResult.nutrient_status}</p>
              <p><strong>Suitable crops:</strong> {Array.isArray(soilResult.suitable_crops) ? soilResult.suitable_crops.join(', ') : soilResult.suitable_crops}</p>
            </div>
          )}
        </form>

        <form className="card form-card" onSubmit={handleCropSubmit}>
          <h3>Crop recommendation</h3>
          <div className="two-col">
            <label>Nitrogen<input name="nitrogen" type="number" value={cropForm.nitrogen} onChange={handleCropChange} /></label>
            <label>Phosphorus<input name="phosphorus" type="number" value={cropForm.phosphorus} onChange={handleCropChange} /></label>
          </div>
          <div className="two-col">
            <label>Potassium<input name="potassium" type="number" value={cropForm.potassium} onChange={handleCropChange} /></label>
            <label>pH<input name="ph" type="number" step="0.1" value={cropForm.ph} onChange={handleCropChange} /></label>
          </div>
          <div className="two-col">
            <label>Temperature<input name="temperature" type="number" value={cropForm.temperature} onChange={handleCropChange} /></label>
            <label>Humidity<input name="humidity" type="number" value={cropForm.humidity} onChange={handleCropChange} /></label>
          </div>
          <label>Rainfall<input name="rainfall" type="number" value={cropForm.rainfall} onChange={handleCropChange} /></label>
          <button className="primary-button" type="submit" disabled={loadingAction === 'crop'}>{loadingAction === 'crop' ? 'Recommending...' : 'Recommend crop'}</button>
          {cropResult && (
            <div className="result-box">
              <h4>Result</h4>
              <p><strong>Top crops:</strong> {cropResult.top_crops?.map((item) => `${item.crop} (${item.score})`).join(', ') || 'Not available'}</p>
              <p><strong>Confidence:</strong> {cropResult.confidence || 'N/A'}</p>
            </div>
          )}
        </form>

        <form className="card form-card" onSubmit={handleDiseaseSubmit}>
          <h3>Disease scanner</h3>
          <label>
            Crop in the image
            <select value={diseaseCrop} onChange={(event) => setDiseaseCrop(event.target.value)}>
              <option>Groundnut</option>
              <option>Tomato</option>
              <option>Potato</option>
            </select>
          </label>
          <CameraScanner
            onCapture={(blob) => setDiseaseFile(new File([blob], 'leaf-capture.jpg', { type: 'image/jpeg' }))}
          />
          <label>
            Capture or upload a crop image
            <input
              type="file"
              accept="image/*"
              capture="environment"
              onChange={(event) => setDiseaseFile(event.target.files?.[0] || null)}
            />
          </label>
          <button className="primary-button" type="submit" disabled={loadingAction === 'disease'}>{loadingAction === 'disease' ? 'Scanning...' : 'Scan disease'}</button>
          {diseaseResult && (
            <div className="result-box">
              <h4>Scan result</h4>
              <p><strong>Crop:</strong> {diseaseResult.crop}</p>
              <p><strong>Disease:</strong> {diseaseResult.disease}</p>
              <p><strong>Confidence:</strong> {diseaseResult.confidence}</p>
              <p><strong>Severity:</strong> {diseaseResult.severity}</p>
              <div className="treatment-list">
                <h4>Pesticides for {diseaseResult.disease.replaceAll('_', ' ')}</h4>
                {diseaseResult.treatments?.length > 0 ? diseaseResult.treatments.map((treatment) => (
                  <div className="treatment-item" key={`${treatment.active_ingredient}-${treatment.product_name}`}>
                    <strong>{treatment.product_name}</strong>
                    <span>Active ingredient: {treatment.active_ingredient}</span>
                    <small>{treatment.application_guidance}</small>
                  </div>
                )) : <p>No pesticide information is available for this disease yet. Consult your local agriculture officer.</p>}
                {diseaseResult.treatments?.length > 0 && <small className="treatment-warning">Verify the product label and local agricultural guidance before spraying.</small>}
              </div>
            </div>
          )}
        </form>
      </div>
    </div>
  );
}

function AdminPage() {
  const { user, logout } = useAuth();
  const [stats, setStats] = useState(null);
  const [farmers, setFarmers] = useState([]);
  const [diseases, setDiseases] = useState([]);
  const [treatments, setTreatments] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadAdminData = async () => {
      try {
        const [dashboardRes, farmersRes, diseasesRes, treatmentsRes] = await Promise.all([
          api.get('/admin/dashboard'),
          api.get('/admin/farmers'),
          api.get('/admin/diseases'),
          api.get('/admin/treatments'),
        ]);

        setStats(dashboardRes.data.stats);
        setFarmers(farmersRes.data.farmers || []);
        setDiseases(diseasesRes.data.diseases || []);
        setTreatments(treatmentsRes.data.treatments || []);
      } catch (err) {
        setError(err.response?.data?.message || 'Unable to load admin data.');
      }
    };

    if (user) {
      loadAdminData();
    }
  }, [user]);

  return (
    <div className="page-shell admin-shell">
      <div className="card welcome-card">
        <div>
          <p className="eyebrow">Administrator view</p>
          <h2>AgriDoctor Admin</h2>
        </div>
        <button className="secondary-button" onClick={logout}>Logout</button>
      </div>

      {error && <div className="error-box">{error}</div>}

      {stats && (
        <div className="stats-grid">
          <div className="card stat-card">
            <span>Total farmers</span>
            <strong>{stats.total_farmers}</strong>
          </div>
          <div className="card stat-card">
            <span>Total scans</span>
            <strong>{stats.total_scans}</strong>
          </div>
          <div className="card stat-card">
            <span>Total diseases</span>
            <strong>{stats.total_diseases}</strong>
          </div>
          <div className="card stat-card">
            <span>Total treatments</span>
            <strong>{stats.total_treatments}</strong>
          </div>
        </div>
      )}

      <div className="admin-grid">
        <div className="card admin-panel">
          <h3>Registered farmers</h3>
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Role</th>
              </tr>
            </thead>
            <tbody>
              {farmers.map((farmer) => (
                <tr key={farmer.id}>
                  <td>{farmer.name}</td>
                  <td>{farmer.email}</td>
                  <td>{farmer.role}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="card admin-panel">
          <h3>Disease catalog</h3>
          <table>
            <thead>
              <tr>
                <th>Crop</th>
                <th>Disease</th>
                <th>Severity</th>
              </tr>
            </thead>
            <tbody>
              {diseases.map((disease) => (
                <tr key={disease.id}>
                  <td>{disease.crop}</td>
                  <td>{disease.disease_name}</td>
                  <td>{disease.severity}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="card admin-panel wide-panel">
          <h3>Treatment catalog</h3>
          <table>
            <thead>
              <tr>
                <th>Crop</th>
                <th>Disease</th>
                <th>Product</th>
              </tr>
            </thead>
            <tbody>
              {treatments.map((treatment) => (
                <tr key={treatment.id}>
                  <td>{treatment.crop}</td>
                  <td>{treatment.disease}</td>
                  <td>{treatment.product_name}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function AppShell() {
  const { user, logout } = useAuth();

  return (
    <BrowserRouter>
      <Navbar user={user} onLogout={logout} />
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={user ? <Navigate to="/dashboard" replace /> : <LoginPage />} />
        <Route path="/register" element={user ? <Navigate to="/dashboard" replace /> : <RegisterPage />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute user={user}>
              <DashboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin"
          element={
            <ProtectedRoute user={user} role="admin">
              <AdminPage />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      <Footer />
    </BrowserRouter>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppShell />
    </AuthProvider>
  );
}

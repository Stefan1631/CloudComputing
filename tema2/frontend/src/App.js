import React, { useState } from 'react';

function App() {
  /* --- constante pentru primul web service (tema 1) --- */
  const [getGrade, setGetGrade] = useState({ id_student: '', materie: '' });
  const [add_Grade, setAdd_Grade] = useState({ id_student: '', materie: '', nota: '' });
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  /* --- constante pentru al doilea web service(logare) --- */
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState(null);
  const [password, setPassword] = useState(null);

  /* --- constante pentru al treilea web service(weatherApi) --- */
  const [weather,setWeather]=useState(null);

  const fetchWeather = async () =>{
        try{
            const response = await fetch(`http://localhost:8001/weather/Iasi`);
            if (response.ok) {
            const result = await response.json();
            setWeather(result);
            }
        } catch (err) {
            console.error("Eroare la preluarea vremii:", err);
        }
  };

  const register = async () => {
        try{
            const response= await fetch(`http://localhost:8001/register`,
            {
                method: 'POST',
                headers: {'Content-Type': 'application/json',},
                body: JSON.stringify({
                username: user,
                password: password,
                })
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Credentiale incorecte");
            }
            const result = await response.json();
            setSuccess(result.message);
            setPassword('');
           } catch (err) {
                setError(err.message);
            }
  }

  const LogIn = async () => {
        try{
            const response = await fetch(`http://localhost:8001/login`,
            {
                method: 'POST',
                headers: {'Content-Type': 'application/json',},
                body: JSON.stringify({
                username: user,
                password: password,
                }),
            });
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || "Credentiale incorecte");
        }
        setIsLoggedIn(true)
        setUser(user)
        setSuccess('');
        setError('');
        setPassword('');
        fetchWeather();
        } catch (err) {
            setError(err.message);
        }

  }

  const LogOut = () => {
    setIsLoggedIn(false);
    setUser('');
    setPassword('');
    setError('');
    setSuccess('');
    setData(null);
  };

  const fetchGrade = async () => {
    setError('');
    try {
      const response = await fetch(`http://localhost:8001/catalog/${getGrade.id_student}/${getGrade.materie}`);
      if (!response.ok){
            const error=await response.json();
            throw new Error(`Eroare: ${response.status} \n ${error.detail}`);
      }
      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err.message);
      setData(null);
    }
  };


  const updateGrade = async() => {
  setError('');
  setSuccess('');
  try{
    const response = await fetch(`http://localhost:8001/catalog/nota`,
    {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            id_student: parseInt(add_Grade.id_student),
            materie: add_Grade.materie,
            nota: parseInt(add_Grade.nota)
        }),
    });
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Nu s-a putut actualiza nota");
    }

    const result = await response.json();
    setSuccess(result.message);
    setAdd_Grade({...add_Grade, id_student:'',materie:'',nota:''});
    } catch (err) {
        setError(err.message);
    }
  }

  const addGrade = async () => {
  setError('');
  setSuccess('');
  try {
    const response = await fetch(`http://localhost:8001/catalog/nota`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        id_student: parseInt(add_Grade.id_student),
        materie: add_Grade.materie,
        nota: parseInt(add_Grade.nota)
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Nu s-a putut adauga nota");
    }

    const result = await response.json();
    setSuccess(result.message);
    setAdd_Grade({...add_Grade, id_student:'',materie:'',nota:''});
  } catch (err) {
    setError(err.message);
  }
};

  return (
  <div style={{
    padding: '20px', minHeight: '100vh', display: 'flex',
    flexDirection: 'column', backgroundColor: '#f0f2f5', justifyContent: isLoggedIn ? 'flex-start' : 'center', alignItems: 'center'
  }}>
    {!isLoggedIn ? (
      /* --- ecran cu div pentru login --- */
      <div style={cardStyle}>
        <h2>Login</h2>
        <input
          style={inputStyle}
          type="text"
          value={user || ''}
          onChange={(e) => setUser(e.target.value)}
          placeholder="username"
        />
        <input
          style={inputStyle}
          type="password"
          value={password || ''}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="parola"
        />
        <button onClick={LogIn} style={buttonStyle}>Log in</button>
        <button onClick={register} style={{ ...buttonStyle, backgroundColor: '#6c757d' }}>Register</button>
        <div style={{ marginTop: '20px', width: '100%' }}>
          {error && <div style={errorBanner}>{error}</div>}
          {success && <div style={successBanner}>{success}</div>}
        </div>
      </div>
    ) : (
      /* --- div care schimba ecranul la catalog --- */
      <div style={{ width: '100%', maxWidth: '1200px' }}>

        {/* pentru vreme */}
        {weather && (
          <div style={{
            background: 'linear-gradient(135deg, #007bff, #00d4ff)',
            color: 'white',
            padding: '15px',
            borderRadius: '8px',
            marginBottom: '20px',
            display: 'flex',
            alignItems: 'center',
            gap: '15px',
            boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
            width: 'fit-content',
            margin: '0 auto 20px auto'
          }}>
            <img
              src={`http://openweathermap.org/img/wn/${weather.icon}@2x.png`}
              alt="weather icon"
              style={{ width: '50px' }}
            />
            <div>
              <h4 style={{ margin: 0 }}>Vremea în {weather.oras}</h4>
              <p style={{ margin: 0, fontSize: '1.2rem', fontWeight: 'bold' }}>{weather.temperatura}°C</p>
              <p style={{ margin: 0, fontSize: '0.8rem', textTransform: 'capitalize' }}>{weather.conditii}</p>
            </div>
          </div>
        )}

        <header style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '15px',
            backgroundColor: 'white',
            borderRadius: '8px',
            boxShadow: '0 2px 5px rgba(0,0,0,0.1)'
        }}>
          <span>Bun venit, <strong>{user}</strong>!</span>
          <button onClick={LogOut} style={{ ...buttonStyle, width: 'auto', backgroundColor: '#dc3545' }}>Logout</button>
        </header>

        <div className="catalog" style={{ padding: '40px', fontFamily: 'sans-serif' }}>
          <h1 style={{ textAlign: 'center' }}>Catalog Studenti</h1>

          <div style={{ display: 'flex', gap: '20px', justifyContent: 'center', flexWrap: 'wrap' }}>
            {/* div pentru gasirea notelor */}
            <div style={cardStyle}>
              <h3>Consulta Nota</h3>
              <input
                style={inputStyle}
                type="number"
                value={getGrade.id_student}
                onChange={(e) => setGetGrade({...getGrade, id_student: e.target.value})}
                placeholder="ID Student"
              />
              <input
                style={inputStyle}
                type="text"
                value={getGrade.materie}
                onChange={(e) => setGetGrade({...getGrade, materie: e.target.value})}
                placeholder="Materia"
              />
              <button onClick={fetchGrade} style={buttonStyle}>Vezi Nota</button>
            </div>

            {/* Secțiunea Add/Update */}
            <div style={{ ...cardStyle, borderTop: '4px solid #28a745' }}>
              <h3>Gestionare Note</h3>
              <input
                style={inputStyle}
                type="number"
                value={add_Grade.id_student}
                onChange={(e) => setAdd_Grade({...add_Grade, id_student: e.target.value})}
                placeholder="ID Student"
              />
              <input
                style={inputStyle}
                type="text"
                value={add_Grade.materie}
                onChange={(e) => setAdd_Grade({...add_Grade, materie: e.target.value})}
                placeholder="Materia"
              />
              <input
                style={inputStyle}
                type="number"
                value={add_Grade.nota}
                onChange={(e) => setAdd_Grade({...add_Grade, nota: e.target.value})}
                placeholder="Nota (1-10)"
              />
              <button onClick={addGrade} style={{ ...buttonStyle, backgroundColor: '#28a745' }}>Adauga</button>
              <button onClick={updateGrade} style={{ ...buttonStyle, backgroundColor: '#ffc107', color: 'black' }}>Actualizeaza</button>
            </div>
          </div>

          <div style={{ maxWidth: '820px', margin: '20px auto' }}>
            {error && <div style={errorBanner}>{error}</div>}
            {success && <div style={successBanner}>{success}</div>}

            {data && (
              <div style={resultCard}>
                <h2 style={{ margin: 0 }}>{data.nume} {data.prenume}</h2>
                <p><strong>Disciplina:</strong> {data.materie}</p>
                <p><strong>Nota:</strong> <span style={{ color: '#007bff', fontWeight: 'bold' }}>{data.nota}</span></p>
              </div>
            )}
          </div>
        </div>
      </div>
    )}
  </div>
)}

// --- css styles ---
const cardStyle = {
  background: 'white',
  padding: '20px',
  borderRadius: '8px',
  boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
  width: '300px',
  display: 'flex',
  flexDirection: 'column',
  gap: '10px'
};

const inputStyle = {
  padding: '10px',
  borderRadius: '4px',
  border: '1px solid #ddd'
};

const buttonStyle = {
  padding: '10px',
  backgroundColor: '#007bff',
  color: 'white',
  border: 'none',
  borderRadius: '4px',
  cursor: 'pointer',
  fontWeight: 'bold'
};

const resultCard = {
  background: 'white',
  padding: '20px',
  borderRadius: '8px',
  marginTop: '20px',
  borderLeft: '5px solid #007bff'
};

const errorBanner = { color: '#721c24', background: '#f8d7da', padding: '10px', borderRadius: '4px', marginBottom: '10px' };
const successBanner = { color: '#155724', background: '#d4edda', padding: '10px', borderRadius: '4px', marginBottom: '10px' };

export default App;
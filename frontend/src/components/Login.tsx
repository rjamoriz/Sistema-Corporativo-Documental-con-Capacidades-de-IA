import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

export const Login: React.FC = () => {
  const [username, setUsername] = useState('admin.demo');
  const [password, setPassword] = useState('Demo2025!');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  
  const navigate = useNavigate();
  const { login } = useAuthStore();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      if (!username || !password) {
        setError('Por favor ingresa usuario y contraseña');
        setIsLoading(false);
        return;
      }

      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
      
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      const response = await fetch(`${API_BASE_URL.replace('/api/v1', '')}/api/v1/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Usuario o contraseña incorrectos');
      }

      const data = await response.json();
      const token = data.access_token;

      const userResponse = await fetch(`${API_BASE_URL}/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!userResponse.ok) {
        throw new Error('Error al obtener información del usuario');
      }

      const userData = await userResponse.json();
      
      login(token, {
        id: userData.username,
        email: userData.email,
        name: userData.full_name,
        role: userData.role,
        is_active: true,
        created_at: new Date().toISOString()
      });

      navigate('/dashboard');
    } catch (err) {
      console.error('Error en login:', err);
      setError(err instanceof Error ? err.message : 'Error al iniciar sesión');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-slate-900 to-black">
      {/* Animated background effects */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -inset-[10px] opacity-50">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-indigo-500/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
        </div>
      </div>

      <div className="relative max-w-md w-full space-y-8 p-10 bg-gray-800/50 backdrop-blur-xl shadow-2xl rounded-2xl border border-gray-700/50">
        <div className="text-center">
          {/* Logo con efecto de brillo */}
          <div className="mx-auto h-16 w-16 flex items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 shadow-lg shadow-blue-500/50">
            <svg className="h-10 w-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          
          {/* Título Principal Impactante */}
          <h1 className="mt-6 text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400">
            FinancIA 2030
          </h1>
          
          <h2 className="mt-3 text-xl font-bold text-gray-200">
            Sistema Corporativo Documental
          </h2>
          
          <p className="mt-2 text-sm text-gray-400 leading-relaxed">
            Plataforma Inteligente de Gestión Documental<br/>
            con IA Generativa y Procesamiento Avanzado
          </p>
          
          <div className="mt-4 flex items-center justify-center gap-2 flex-wrap">
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-green-500/20 text-green-400 border border-green-500/30">
              ✓ 100% RFP Coverage
            </span>
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-blue-500/20 text-blue-400 border border-blue-500/30">
              🚀 Production Ready
            </span>
          </div>
        </div>

        <form onSubmit={handleLogin} className="mt-8 space-y-6">
          {error && (
            <div className="rounded-lg bg-red-500/10 border border-red-500/30 p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-red-400">{error}</p>
                </div>
              </div>
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-300">
                Usuario
              </label>
              <input
                id="username"
                name="username"
                type="text"
                autoComplete="username"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="mt-1 block w-full px-4 py-3 bg-gray-700/50 border border-gray-600 rounded-lg shadow-sm placeholder-gray-500 text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all sm:text-sm"
                placeholder="admin.demo"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-300">
                Contraseña
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="mt-1 block w-full px-4 py-3 bg-gray-700/50 border border-gray-600 rounded-lg shadow-sm placeholder-gray-500 text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all sm:text-sm"
                placeholder="Demo2025!"
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={isLoading}
              className="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-lg text-sm font-semibold text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-[1.02]"
            >
              {isLoading ? (
                <span className="flex items-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Iniciando sesión...
                </span>
              ) : (
                'Iniciar Sesión'
              )}
            </button>
          </div>
        </form>

        <div className="mt-6 border-t border-gray-700/50 pt-6">
          <p className="text-xs text-gray-400 font-semibold mb-3">
            👤 Usuarios de Demostración
          </p>
          <div className="space-y-2 text-xs text-gray-400">
            <p className="flex items-center gap-2">
              <code className="bg-gray-700/50 px-2 py-1 rounded border border-gray-600 text-blue-400">admin.demo</code> 
              <span className="text-gray-500">→</span>
              <span>Administrador completo</span>
            </p>
            <p className="flex items-center gap-2">
              <code className="bg-gray-700/50 px-2 py-1 rounded border border-gray-600 text-green-400">revisor.demo</code>
              <span className="text-gray-500">→</span>
              <span>Revisor de documentos</span>
            </p>
            <p className="flex items-center gap-2">
              <code className="bg-gray-700/50 px-2 py-1 rounded border border-gray-600 text-yellow-400">usuario.demo</code>
              <span className="text-gray-500">→</span>
              <span>Usuario estándar</span>
            </p>
            <p className="flex items-center gap-2">
              <code className="bg-gray-700/50 px-2 py-1 rounded border border-gray-600 text-purple-400">lectura.demo</code>
              <span className="text-gray-500">→</span>
              <span>Solo lectura</span>
            </p>
          </div>
          <div className="mt-3 pt-3 border-t border-gray-700/30">
            <p className="text-xs text-gray-500">
              🔑 Contraseña única: <code className="bg-gray-700/50 px-2 py-1 rounded font-mono text-indigo-400 border border-gray-600">Demo2025!</code>
            </p>
          </div>
        </div>

        <div className="mt-4 text-center space-y-1">
          <p className="text-xs text-gray-500">
            Versión 1.0 • Octubre 2025
          </p>
          <p className="text-xs text-gray-600">
            Powered by IA Generativa & Machine Learning
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;

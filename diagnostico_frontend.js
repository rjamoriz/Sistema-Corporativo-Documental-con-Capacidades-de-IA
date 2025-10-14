// ========================================
// DIAGNÓSTICO: Datos Sintéticos - Frontend
// ========================================
// Ejecuta este código en la consola del navegador (F12)
// DESPUÉS de hacer login en la aplicación

console.log('%c=== DIAGNÓSTICO FRONTEND ===', 'color: cyan; font-size: 16px; font-weight: bold');

// 1. Verificar token en localStorage
console.log('\n%c1. Token en localStorage:', 'color: yellow; font-weight: bold');
const token = localStorage.getItem('token');
if (token) {
    console.log('✅ Token existe');
    console.log('📝 Token:', token.substring(0, 50) + '...');
    
    // Decodificar JWT (solo para ver contenido, no validar)
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        console.log('📋 Token payload:', payload);
        console.log('⏰ Expira:', new Date(payload.exp * 1000).toLocaleString());
        
        const now = Date.now() / 1000;
        if (payload.exp < now) {
            console.log('❌ TOKEN EXPIRADO!');
        } else {
            console.log('✅ Token aún válido');
        }
    } catch (e) {
        console.log('⚠️ No se pudo decodificar token');
    }
} else {
    console.log('❌ NO HAY TOKEN - Necesitas hacer login');
}

// 2. Test directo al backend
console.log('\n%c2. Test directo a templates endpoint:', 'color: yellow; font-weight: bold');

if (token) {
    fetch('http://localhost:8000/api/v1/synthetic/templates', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
    .then(async response => {
        console.log('📊 Status:', response.status);
        console.log('📋 Headers:', Object.fromEntries(response.headers.entries()));
        
        if (response.ok) {
            const data = await response.json();
            console.log('✅ Templates cargados:', data.length);
            console.log('📄 Templates:', data);
        } else {
            const error = await response.json();
            console.log('❌ Error:', error);
        }
    })
    .catch(error => {
        console.log('❌ Error de red:', error.message);
        console.log('💡 Verifica que el backend esté en http://localhost:8000');
    });
} else {
    console.log('⚠️ Saltando test - no hay token');
}

// 3. Verificar configuración de CORS
console.log('\n%c3. Verificando CORS:', 'color: yellow; font-weight: bold');
console.log('🌐 Origen actual:', window.location.origin);
console.log('🎯 API objetivo: http://localhost:8000');

// 4. Información del navegador
console.log('\n%c4. Info del navegador:', 'color: yellow; font-weight: bold');
console.log('🔍 User Agent:', navigator.userAgent);
console.log('🍪 Cookies habilitadas:', navigator.cookieEnabled);

console.log('\n%c=== FIN DIAGNÓSTICO ===', 'color: cyan; font-size: 16px; font-weight: bold');
console.log('\n💡 Si ves "TOKEN EXPIRADO", haz logout y login nuevamente');
console.log('💡 Si ves error de CORS, el backend necesita reiniciarse');
console.log('💡 Si no hay token, necesitas hacer login primero');

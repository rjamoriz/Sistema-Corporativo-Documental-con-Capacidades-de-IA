// DIAGNÓSTICO: Ejecuta esto en la CONSOLA DEL NAVEGADOR (F12 → Console)

console.log('=== DIAGNÓSTICO TOKEN ===');
console.log('1. Token en localStorage:', localStorage.getItem('auth_token'));
console.log('2. Token en localStorage (backup):', localStorage.getItem('token'));
console.log('3. Todos los items en localStorage:', Object.keys(localStorage));
console.log('========================');

// Si no hay token, haz login de nuevo
// Si hay token, intenta cargar templates manualmente:
if (localStorage.getItem('auth_token')) {
    fetch('http://localhost:8000/api/v1/synthetic/templates', {
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('auth_token')
        }
    })
    .then(r => {
        console.log('Response status:', r.status);
        return r.json();
    })
    .then(data => console.log('Templates:', data))
    .catch(err => console.error('Error:', err));
}

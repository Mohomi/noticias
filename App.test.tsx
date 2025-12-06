// Archivo de prueba para verificar que React funciona
import React from 'react';

function TestApp() {
  return (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <h1>Test - React está funcionando</h1>
      <p>Si ves esto, React está renderizando correctamente</p>
      <button onClick={() => alert('Botón funcionando!')}>
        Probar Botón
      </button>
    </div>
  );
}

export default TestApp;


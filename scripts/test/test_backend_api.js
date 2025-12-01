
// const fetch = require('node-fetch'); // Built-in in Node 18+

const BACKEND_URL = 'http://192.168.32.3:8000'; // Trying port 8000

async function testBackend() {
    const stockCode = '108320';
    console.log(`Testing backend for stock: ${stockCode}`);

    try {
        const response = await fetch(`${BACKEND_URL}/api/indicators/calculate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                stock_code: stockCode,
                indicators: [
                    { name: "ma", params: { period: 20 } }
                ],
                days: 60
            })
        });

        if (!response.ok) {
            console.error(`HTTP Error: ${response.status} ${response.statusText}`);
            const text = await response.text();
            console.error('Response body:', text);
            return;
        }

        const data = await response.json();
        console.log('Backend Response:', JSON.stringify(data, null, 2));

        if (data.stock_name === stockCode) {
            console.error('FAIL: Backend returned stock code instead of name.');
        } else {
            console.log(`SUCCESS: Backend returned name: ${data.stock_name}`);
        }

    } catch (error) {
        console.error('Connection failed:', error.message);
        console.log('Please verify the NAS IP and Port.');
    }
}

testBackend();

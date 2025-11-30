
const axios = require('axios');

const API_URL = 'http://localhost:8001/api/indicators/calculate';

async function testBackendApi() {
    console.log(`Testing Backend API at ${API_URL}...`);

    const payload = {
        stock_code: "005930", // Samsung Electronics (usually has data)
        indicators: [
            { name: "ma", params: { period: 20 } },
            { name: "stochastic", params: { period: 14 } },
            { name: "rsi", params: { period: 14 } }
        ],
        days: 100
    };

    try {
        const response = await axios.post(API_URL, payload);
        console.log('API Call Successful!');
        console.log('Status:', response.status);
        console.log('Data:', JSON.stringify(response.data, null, 2));
    } catch (error) {
        console.error('API Call Failed!');
        if (error.response) {
            console.error('Status:', error.response.status);
            console.error('Data:', error.response.data);
        } else {
            console.error('Error:', error.message);
        }
    }
}

testBackendApi();

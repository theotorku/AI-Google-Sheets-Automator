import axios from 'axios';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export default async function handler(req, res) {
    if (req.method !== 'POST') {
        return res.status(405).json({ message: 'Method not allowed' });
    }

    try {
        const { prompt, token } = req.body;

        // Proxy to backend
        const response = await axios.post(`${BACKEND_URL}/generate-script`,
            { user_prompt: prompt },
            {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            }
        );

        res.status(200).json(response.data);
    } catch (error) {
        console.error("Backend Proxy Error:", error.response?.data || error.message);
        res.status(error.response?.status || 500).json({
            error: error.response?.data?.detail || "Backend communication failed"
        });
    }
}

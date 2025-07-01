import { useState } from 'react';
import { useRouter } from 'next/router';
import { GoogleLogin } from '@react-oauth/google';
import { signInWithCustomToken, getAuth } from 'firebase/auth';
import { initializeApp } from 'firebase/app';
import axios from 'axios';
import { toast, Toaster } from 'react-hot-toast';

// Firebase config
const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
};
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

export default function Home() {
  const [code, setCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleGoogleAuth = async (credential) => {
    const res = await axios.post('/api/auth', { token: credential });
    await signInWithCustomToken(auth, res.data.firebase_token);
    toast.success("Logged in!");
  };

  const generateCode = async (prompt) => {
    setIsLoading(true);
    try {
      const res = await axios.post('/api/generate', { prompt });
      setCode(res.data.code);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to generate code");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container">
      <Toaster />
      <GoogleLogin onSuccess={handleGoogleAuth} />
      <button onClick={() => generateCode("Fetch Shopify orders")}>
        {isLoading ? "Generating..." : "Test Automation"}
      </button>
      <pre>{code}</pre>
    </div>
  );
}
import { useState, useEffect } from 'react';
import axios from 'axios';
import { toast, Toaster } from 'react-hot-toast';
import { supabase } from '../lib/supabase';

export default function Home() {
  const [code, setCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Check active session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null);
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
    });

    return () => subscription.unsubscribe();
  }, []);

  const handleLogin = async () => {
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
    });
    if (error) toast.error(error.message);
  };

  const handleLogout = async () => {
    await supabase.auth.signOut();
    toast.success("Logged out");
  };

  const generateCode = async (prompt) => {
    if (!user) {
      toast.error("Please login first");
      return;
    }

    setIsLoading(true);
    try {
      // Get session token to pass to backend
      const { data: { session } } = await supabase.auth.getSession();

      const res = await axios.post('/api/generate', {
        prompt,
        token: session?.access_token
      });
      setCode(res.data.code);
      toast.success("Code generated!");
    } catch (err) {
      toast.error(err.response?.data?.error || "Failed to generate code");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container" style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <Toaster />
      <h1>AI Sheets Automator</h1>

      {!user ? (
        <button onClick={handleLogin}>Log in with Google</button>
      ) : (
        <div style={{ marginBottom: '20px' }}>
          <p>Welcome, {user.email} <button onClick={handleLogout}>Logout</button></p>

          <div style={{ display: 'flex', gap: '10px' }}>
            <button
              onClick={() => generateCode("Fetch Shopify orders and add to active sheet")}
              disabled={isLoading}
            >
              {isLoading ? "Generating..." : "Generate Script"}
            </button>
          </div>
        </div>
      )}

      {code && (
        <div style={{ marginTop: '20px' }}>
          <h3>Generated Code:</h3>
          <pre style={{ background: '#f4f4f4', padding: '10px', borderRadius: '5px' }}>
            {code}
          </pre>
        </div>
      )}
    </div>
  );
}
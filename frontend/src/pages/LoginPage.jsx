import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import TextField from '../components/ui/TextField.jsx';
import { useAuth } from '../hooks/useAuth.js';

function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();
  const [form, setForm] = useState({
    email: '',
    password: '',
  });
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const from = location.state?.from?.pathname || '/dashboard';

  const updateField = (field, value) => {
    setForm((current) => ({ ...current, [field]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setSubmitting(true);

    try {
      await login(form);
      navigate(from, { replace: true });
    } catch (requestError) {
      setError(requestError.response?.data?.message || 'Unable to login. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <section className="mx-auto grid max-w-6xl gap-10 px-4 py-12 sm:px-6 lg:grid-cols-[0.9fr_1fr] lg:px-8">
      <div className="flex flex-col justify-center">
        <p className="text-sm font-semibold uppercase tracking-wide text-brand-700">Secure access</p>
        <h1 className="mt-3 text-3xl font-bold text-slate-950 sm:text-4xl">Login to GuardianPath AI</h1>
        <p className="mt-4 max-w-xl text-slate-600">
          Your dashboard stores trusted contacts and prepares your account for live tracking, route safety, and SOS alerts.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="rounded-lg border border-slate-200 bg-white p-6 shadow-soft">
        <div className="space-y-5">
          <TextField
            id="email"
            label="Email"
            type="email"
            value={form.email}
            onChange={(event) => updateField('email', event.target.value)}
            placeholder="you@example.com"
            autoComplete="email"
            required
          />
          <TextField
            id="password"
            label="Password"
            type="password"
            value={form.password}
            onChange={(event) => updateField('password', event.target.value)}
            placeholder="Enter your password"
            autoComplete="current-password"
            required
          />
        </div>

        {error ? <p className="mt-4 rounded-md bg-red-50 px-4 py-3 text-sm text-red-700">{error}</p> : null}

        <button
          type="submit"
          disabled={submitting}
          className="mt-6 w-full rounded-md bg-brand-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-70"
        >
          {submitting ? 'Logging in...' : 'Login'}
        </button>

        <p className="mt-5 text-center text-sm text-slate-600">
          New to GuardianPath?{' '}
          <Link className="font-semibold text-brand-700 hover:text-brand-600" to="/signup">
            Create an account
          </Link>
        </p>
      </form>
    </section>
  );
}

export default LoginPage;

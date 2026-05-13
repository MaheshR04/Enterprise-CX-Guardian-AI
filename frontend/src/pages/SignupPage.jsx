import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import GuardianContactsEditor from '../components/forms/GuardianContactsEditor.jsx';
import TextField from '../components/ui/TextField.jsx';
import { useAuth } from '../hooks/useAuth.js';

function SignupPage() {
  const navigate = useNavigate();
  const { signup } = useAuth();
  const [form, setForm] = useState({
    name: '',
    email: '',
    phoneNumber: '',
    password: '',
  });
  const [guardianContacts, setGuardianContacts] = useState([]);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const updateField = (field, value) => {
    setForm((current) => ({ ...current, [field]: value }));
  };

  const cleanedContacts = guardianContacts.filter(
    (contact) => contact.name.trim() && contact.phoneNumber.trim(),
  );

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setSubmitting(true);

    try {
      await signup({
        ...form,
        guardianContacts: cleanedContacts,
      });
      navigate('/dashboard', { replace: true });
    } catch (requestError) {
      setError(requestError.response?.data?.message || 'Unable to create account. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <section className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">
      <div className="mb-8 max-w-3xl">
        <p className="text-sm font-semibold uppercase tracking-wide text-brand-700">User signup</p>
        <h1 className="mt-3 text-3xl font-bold text-slate-950 sm:text-4xl">Create your safety profile</h1>
        <p className="mt-4 text-slate-600">
          Save your core identity and trusted guardian contacts now. Later steps will use this data for SOS SMS alerts and live tracking rooms.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="rounded-lg border border-slate-200 bg-white p-6 shadow-soft">
        <div className="grid gap-5 md:grid-cols-2">
          <TextField
            id="name"
            label="Full name"
            value={form.name}
            onChange={(event) => updateField('name', event.target.value)}
            placeholder="Mahesh Rathod"
            autoComplete="name"
            required
          />
          <TextField
            id="phoneNumber"
            label="Phone number"
            value={form.phoneNumber}
            onChange={(event) => updateField('phoneNumber', event.target.value)}
            placeholder="+91..."
            autoComplete="tel"
            required
          />
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
            placeholder="Minimum 8 characters"
            autoComplete="new-password"
            minLength={8}
            required
          />
        </div>

        <div className="mt-8">
          <GuardianContactsEditor contacts={guardianContacts} onChange={setGuardianContacts} />
        </div>

        {error ? <p className="mt-5 rounded-md bg-red-50 px-4 py-3 text-sm text-red-700">{error}</p> : null}

        <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:items-center">
          <button
            type="submit"
            disabled={submitting}
            className="rounded-md bg-brand-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-70"
          >
            {submitting ? 'Creating account...' : 'Create Account'}
          </button>
          <p className="text-sm text-slate-600">
            Already registered?{' '}
            <Link className="font-semibold text-brand-700 hover:text-brand-600" to="/login">
              Login
            </Link>
          </p>
        </div>
      </form>
    </section>
  );
}

export default SignupPage;

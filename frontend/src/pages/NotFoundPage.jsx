import { Link } from 'react-router-dom';

function NotFoundPage() {
  return (
    <section className="mx-auto max-w-3xl px-4 py-20 text-center sm:px-6 lg:px-8">
      <p className="text-sm font-semibold uppercase tracking-wide text-brand-700">404</p>
      <h1 className="mt-3 text-3xl font-bold text-slate-950">Page not found</h1>
      <p className="mt-4 text-slate-600">The route you requested does not exist in the MVP shell.</p>
      <Link
        to="/"
        className="mt-8 inline-flex rounded-md bg-brand-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-brand-700"
      >
        Back Home
      </Link>
    </section>
  );
}

export default NotFoundPage;

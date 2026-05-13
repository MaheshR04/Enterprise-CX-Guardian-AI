import { Plus, Trash2 } from 'lucide-react';
import TextField from '../ui/TextField.jsx';

const emptyContact = {
  name: '',
  phoneNumber: '',
  relationship: 'Guardian',
};

function GuardianContactsEditor({ contacts, onChange, maxContacts = 5 }) {
  const canAdd = contacts.length < maxContacts;

  const updateContact = (index, field, value) => {
    onChange(
      contacts.map((contact, contactIndex) =>
        contactIndex === index ? { ...contact, [field]: value } : contact,
      ),
    );
  };

  const removeContact = (index) => {
    onChange(contacts.filter((_contact, contactIndex) => contactIndex !== index));
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h2 className="text-sm font-semibold text-slate-900">Trusted guardian contacts</h2>
          <p className="text-sm text-slate-500">These contacts will be used for SOS alerts later.</p>
        </div>
        <button
          type="button"
          onClick={() => onChange([...contacts, emptyContact])}
          disabled={!canAdd}
          className="inline-flex h-10 w-10 items-center justify-center rounded-md border border-slate-300 bg-white text-slate-700 transition hover:border-brand-500 hover:text-brand-700 disabled:cursor-not-allowed disabled:opacity-40"
          aria-label="Add guardian contact"
          title="Add guardian contact"
        >
          <Plus size={18} aria-hidden="true" />
        </button>
      </div>

      {contacts.length === 0 ? (
        <p className="rounded-md border border-dashed border-slate-300 bg-slate-50 px-4 py-3 text-sm text-slate-500">
          No guardian contacts added yet.
        </p>
      ) : null}

      {contacts.map((contact, index) => (
        <div key={index} className="rounded-lg border border-slate-200 bg-slate-50 p-4">
          <div className="mb-3 flex items-center justify-between">
            <span className="text-sm font-semibold text-slate-700">Guardian {index + 1}</span>
            <button
              type="button"
              onClick={() => removeContact(index)}
              className="inline-flex h-9 w-9 items-center justify-center rounded-md text-slate-500 transition hover:bg-white hover:text-red-600"
              aria-label={`Remove guardian ${index + 1}`}
              title="Remove guardian"
            >
              <Trash2 size={17} aria-hidden="true" />
            </button>
          </div>
          <div className="grid gap-3 sm:grid-cols-3">
            <TextField
              id={`guardian-name-${index}`}
              label="Name"
              value={contact.name}
              onChange={(event) => updateContact(index, 'name', event.target.value)}
              placeholder="Guardian name"
              required
            />
            <TextField
              id={`guardian-phone-${index}`}
              label="Phone"
              value={contact.phoneNumber}
              onChange={(event) => updateContact(index, 'phoneNumber', event.target.value)}
              placeholder="+91..."
              required
            />
            <TextField
              id={`guardian-relation-${index}`}
              label="Relation"
              value={contact.relationship}
              onChange={(event) => updateContact(index, 'relationship', event.target.value)}
              placeholder="Parent"
            />
          </div>
        </div>
      ))}
    </div>
  );
}

export default GuardianContactsEditor;

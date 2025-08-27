import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { fetchEventSummary, EventSummary } from '../api';

export default function EventDetail() {
  const { id } = useParams();
  const { data: summary } = useQuery<EventSummary>({
    queryKey: ['summary', id],
    queryFn: () => fetchEventSummary(id as string),
    enabled: !!id,
  });

  if (!summary) {
    return <div className="p-8">Loading...</div>;
  }

  return (
    <div className="p-8 space-y-4">
      <Link to="/" className="text-blue-600 underline">
        ← Back
      </Link>
      <h1 className="text-2xl font-bold">Event Summary</h1>
      <Link
        to={`/events/${id}/timeline`}
        className="text-blue-600 underline"
      >
        View Timeline
      </Link>
      {summary.selling_points.length === 0 ? (
        <p>No data.</p>
      ) : (
        summary.selling_points.map((sp) => (
          <div key={sp.id} className="border p-2">
            <h2 className="font-semibold">
              {sp.name} - {(sp.total_cents / 100).toFixed(2)}
            </h2>
            <ul className="ml-4 list-disc">
              {sp.epts.map((ept) => (
                <li key={ept.id}>
                  {ept.label}: {(ept.total_cents / 100).toFixed(2)}
                </li>
              ))}
            </ul>
          </div>
        ))
      )}
    </div>
  );
}

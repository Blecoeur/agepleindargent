export interface Event {
  id: string;
  name: string;
  start_at: string;
  end_at: string;
}

export interface EPTSummary {
  id: string;
  label: string;
  total_cents: number;
}

export interface SellingPointSummary {
  id: string;
  name: string;
  total_cents: number;
  epts: EPTSummary[];
}

export interface EventSummary {
  event_id: string;
  selling_points: SellingPointSummary[];
}

export interface TimelineSeries {
  selling_point_id: string;
  lat: number;
  lng: number;
  cumulative: number[];
}

export interface EventTimeline {
  event: { start_at: string; end_at: string };
  buckets: string[];
  series: TimelineSeries[];
}

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

export async function fetchEvents(): Promise<Event[]> {
  const res = await fetch(`${API_URL}/events/`);
  if (!res.ok) throw new Error('Failed to fetch events');
  return res.json();
}

export async function createEvent(data: {
  name: string;
  start_at: string;
  end_at: string;
}): Promise<Event> {
  const res = await fetch(`${API_URL}/events/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to create event');
  return res.json();
}

export async function fetchEventSummary(id: string): Promise<EventSummary> {
  const res = await fetch(`${API_URL}/events/${id}/summary`);
  if (!res.ok) throw new Error('Failed to fetch summary');
  return res.json();
}

export async function fetchEventTimeline(id: string): Promise<EventTimeline> {
  const res = await fetch(`${API_URL}/events/${id}/timeline`);
  if (!res.ok) throw new Error('Failed to fetch timeline');
  return res.json();
}

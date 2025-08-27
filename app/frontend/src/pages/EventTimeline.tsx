import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { MapContainer, TileLayer, CircleMarker } from 'react-leaflet';
import { useState, useEffect } from 'react';
import { fetchEventTimeline, EventTimeline } from '../api';
import 'leaflet/dist/leaflet.css';

export default function EventTimelinePage() {
  const { id } = useParams();
  const { data } = useQuery<EventTimeline>({
    queryKey: ['timeline', id],
    queryFn: () => fetchEventTimeline(id as string),
    enabled: !!id,
  });
  const [index, setIndex] = useState(0);
  const [playing, setPlaying] = useState(false);

  useEffect(() => {
    if (!playing) return;
    const timer = setInterval(() => {
      setIndex((i) => (data ? (i + 1) % data.buckets.length : i));
    }, 1000);
    return () => clearInterval(timer);
  }, [playing, data]);

  if (!data) return <div className="p-8">Loading...</div>;

  const center: [number, number] =
    data.series.length > 0 ? [data.series[0].lat, data.series[0].lng] : [0, 0];

  return (
    <div className="p-4 space-y-4">
      <Link to={`/events/${id}`} className="text-blue-600 underline">
        ← Back
      </Link>
      <div className="flex items-center gap-2">
        <button
          onClick={() => setPlaying(!playing)}
          className="bg-blue-500 text-white px-2 py-1"
        >
          {playing ? 'Pause' : 'Play'}
        </button>
        <input
          type="range"
          min={0}
          max={data.buckets.length - 1}
          value={index}
          onChange={(e) => setIndex(Number(e.target.value))}
        />
        <span>{new Date(data.buckets[index]).toLocaleTimeString()}</span>
      </div>
      <MapContainer
        center={center}
        zoom={13}
        style={{ height: '400px', width: '100%' }}
      >
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        {data.series.map((s) => (
          <CircleMarker
            key={s.selling_point_id}
            center={[s.lat, s.lng]}
            radius={Math.sqrt(s.cumulative[index]) / 10}
          />
        ))}
      </MapContainer>
    </div>
  );
}

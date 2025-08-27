import { Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { createEvent, fetchEvents } from '../api';
import type { Event } from '../api';

const schema = z.object({
  name: z.string().min(1),
  start_at: z.string(),
  end_at: z.string(),
});

type FormData = z.infer<typeof schema>;

export default function EventsList() {
  const queryClient = useQueryClient();
  const { data: events } = useQuery<Event[]>({
    queryKey: ['events'],
    queryFn: fetchEvents,
  });

  const { register, handleSubmit, reset } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const mutation = useMutation({
    mutationFn: createEvent,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['events'] });
      reset();
    },
  });

  const onSubmit = (data: FormData) => mutation.mutate(data);

  return (
    <div className="p-8 space-y-4">
      <h1 className="text-2xl font-bold">Events</h1>

      <form onSubmit={handleSubmit(onSubmit)} className="flex gap-2">
        <input {...register('name')} placeholder="Name" className="border p-1" />
        <input {...register('start_at')} type="datetime-local" className="border p-1" />
        <input {...register('end_at')} type="datetime-local" className="border p-1" />
        <button type="submit" className="bg-blue-500 text-white px-2 py-1">Create</button>
      </form>

      <table className="min-w-full border">
        <thead>
          <tr className="bg-gray-100">
            <th className="p-2 text-left">Name</th>
            <th className="p-2">Start</th>
            <th className="p-2">End</th>
          </tr>
        </thead>
        <tbody>
          {events?.map((ev) => (
            <tr key={ev.id} className="border-t">
              <td className="p-2 text-blue-600 underline">
                <Link to={`/events/${ev.id}`}>{ev.name}</Link>
              </td>
              <td className="p-2">{new Date(ev.start_at).toLocaleString()}</td>
              <td className="p-2">{new Date(ev.end_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

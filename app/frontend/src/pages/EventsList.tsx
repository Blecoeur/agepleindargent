import { Link as RouterLink } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Box,
  Heading,
  Link,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Input,
  Button,
  Flex,
} from '@chakra-ui/react';
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
    <Box p={8}>
      <Heading size="lg" mb={4}>
        Events
      </Heading>

      <form onSubmit={handleSubmit(onSubmit)}>
        <Flex gap={2} mb={4} wrap="wrap">
          <Input {...register('name')} placeholder="Name" />
          <Input {...register('start_at')} type="datetime-local" />
          <Input {...register('end_at')} type="datetime-local" />
          <Button type="submit" colorScheme="blue">
            Create
          </Button>
        </Flex>
      </form>

      <Table variant="simple">
        <Thead>
          <Tr>
            <Th>Name</Th>
            <Th>Start</Th>
            <Th>End</Th>
          </Tr>
        </Thead>
        <Tbody>
          {events?.map((ev) => (
            <Tr key={ev.id}>
              <Td>
                <Link as={RouterLink} to={`/events/${ev.id}`} color="blue.500">
                  {ev.name}
                </Link>
              </Td>
              <Td>{new Date(ev.start_at).toLocaleString()}</Td>
              <Td>{new Date(ev.end_at).toLocaleString()}</Td>
            </Tr>
          ))}
        </Tbody>
      </Table>
    </Box>
  );
}

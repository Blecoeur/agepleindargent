import { useParams, Link as RouterLink } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Box,
  Heading,
  Link,
  UnorderedList,
  ListItem,
  Stack,
  Select,
  Input,
  Button,
} from '@chakra-ui/react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { fetchEventSummary, createEPT, type EventSummary, type EPTProvider } from '../api';

type EPTForm = {
  provider: EPTProvider;
  label: string;
};

function AddEPTForm({ spId, eventId }: { spId: string; eventId: string }) {
  const queryClient = useQueryClient();
  const schema = z.object({
    provider: z.enum(['worldline', 'sumup', 'other']),
    label: z.string().min(1),
  });
  const { register, handleSubmit, reset } = useForm<EPTForm>({
    resolver: zodResolver(schema),
  });
  const mutation = useMutation({
    mutationFn: (data: EPTForm) => createEPT(spId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['summary', eventId] });
      reset();
    },
  });
  const onSubmit = (data: EPTForm) => mutation.mutate(data);
  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <Stack direction={{ base: 'column', md: 'row' }} mt={2} spacing={2}>
        <Select placeholder="Provider" {...register('provider')}>
          <option value="worldline">Worldline</option>
          <option value="sumup">SumUp</option>
          <option value="other">Other</option>
        </Select>
        <Input placeholder="Label" {...register('label')} />
        <Button type="submit" colorScheme="blue">
          Add EPT
        </Button>
      </Stack>
    </form>
  );
}

export default function EventDetail() {
  const { id } = useParams();
  const { data: summary } = useQuery<EventSummary>({
    queryKey: ['summary', id],
    queryFn: () => fetchEventSummary(id as string),
    enabled: !!id,
  });

  if (!summary) {
    return <Box p={8}>Loading...</Box>;
  }

  return (
    <Box p={8}>
      <Link as={RouterLink} to="/" color="blue.500">
        ← Back
      </Link>
      <Heading size="lg" my={4}>
        Event Summary
      </Heading>
      <Link as={RouterLink} to={`/events/${id}/timeline`} color="blue.500">
        View Timeline
      </Link>
      {summary.selling_points.length === 0 ? (
        <Box mt={4}>No data.</Box>
      ) : (
        <Stack mt={4} spacing={4}>
          {summary.selling_points.map((sp) => (
            <Box key={sp.id} borderWidth="1px" p={2} borderRadius="md">
              <Heading size="md" mb={2}>
                {sp.name} - {(sp.total_cents / 100).toFixed(2)}
              </Heading>
              <UnorderedList ml={4}>
                {sp.epts.map((ept) => (
                  <ListItem key={ept.id}>
                    {ept.label}: {(ept.total_cents / 100).toFixed(2)}
                  </ListItem>
                ))}
              </UnorderedList>
              <AddEPTForm spId={sp.id} eventId={id as string} />
            </Box>
          ))}
        </Stack>
      )}
    </Box>
  );
}

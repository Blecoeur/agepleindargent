import { BrowserRouter, Routes, Route } from 'react-router-dom';
import EventsList from './pages/EventsList';
import EventDetail from './pages/EventDetail';
import EventTimelinePage from './pages/EventTimeline';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<EventsList />} />
        <Route path="/events/:id" element={<EventDetail />} />
        <Route path="/events/:id/timeline" element={<EventTimelinePage />} />
      </Routes>
    </BrowserRouter>
  );
}

import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from '@/components/layout/app-layout';
import { Dashboard } from '@/pages/dashboard';
import { Chat } from '@/pages/chat';
import { Tools } from '@/pages/tools';
import { Skill } from '@/pages/skill';
import { Help } from '@/pages/help';
import { Apps } from '@/pages/apps';
import { Status } from '@/pages/status';
import { Settings } from '@/pages/settings';
import { Plugins } from '@/pages/plugins';
import { Editor } from '@/pages/editor';
import { Operations } from '@/pages/operations';
import { Diagnostics } from '@/pages/diagnostics';

function App() {
  return (
    <Router>
      <AppLayout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/editor" element={<Editor />} />
          <Route path="/operations" element={<Operations />} />
          <Route path="/diagnostics" element={<Diagnostics />} />
          <Route path="/plugins" element={<Plugins />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/tools" element={<Tools />} />
          <Route path="/skill" element={<Skill />} />
          <Route path="/apps" element={<Apps />} />
          <Route path="/status" element={<Status />} />
          <Route path="/help" element={<Help />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AppLayout>
    </Router>
  );
}

export default App;

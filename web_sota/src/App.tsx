import {
  Navigate,
  Route,
  BrowserRouter as Router,
  Routes,
} from "react-router-dom";
import { AppLayout } from "@/components/layout/app-layout";
import { Apps } from "@/pages/apps";
import { Chat } from "@/pages/chat";
import { Dashboard } from "@/pages/dashboard";
import { Diagnostics } from "@/pages/diagnostics";
import { Editor } from "@/pages/editor";
import { Help } from "@/pages/help";
import Logging from "@/pages/Logging";
import { Operations } from "@/pages/operations";
import { Plugins } from "@/pages/plugins";
import { Settings } from "@/pages/settings";
import { Skill } from "@/pages/skill";
import { Status } from "@/pages/status";
import { Tools } from "@/pages/tools";

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
          <Route path="/logging" element={<Logging />} />
          <Route path="/help" element={<Help />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AppLayout>
    </Router>
  );
}

export default App;

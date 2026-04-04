import { useState } from "react";

import { AppShell, type PageKey } from "./components/layout/AppShell";
import { OverviewPage } from "./pages/OverviewPage";
import { HoldingsPage } from "./pages/HoldingsPage";

function App() {
  const [currentPage, setCurrentPage] = useState<PageKey>("overview");

  return (
    <AppShell currentPage={currentPage} onNavigate={setCurrentPage}>
      {currentPage === "overview" ? <OverviewPage /> : <HoldingsPage />}
    </AppShell>
  );
}

export default App;
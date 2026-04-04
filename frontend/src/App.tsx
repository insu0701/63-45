import { useState } from "react";

import { AllocationPage } from "./pages/AllocationPage";
import { AppShell, type PageKey } from "./components/layout/AppShell";
import { HoldingsPage } from "./pages/HoldingsPage";
import { OverviewPage } from "./pages/OverviewPage";
import { SyncPage } from "./pages/SyncPage";

function App() {
  const [currentPage, setCurrentPage] = useState<PageKey>("overview");

  return (
    <AppShell currentPage={currentPage} onNavigate={setCurrentPage}>
      {currentPage === "overview" && <OverviewPage />}
      {currentPage === "holdings" && <HoldingsPage />}
      {currentPage === "allocation" && <AllocationPage />}
      {currentPage === "sync" && <SyncPage />}
    </AppShell>
  );
}

export default App;
import { useState } from "react";

import { AllocationPage } from "./pages/AllocationPage";
import { AppShell, type PageKey } from "./components/layout/AppShell";
import { OverviewPage } from "./pages/OverviewPage";
import { HoldingsPage } from "./pages/HoldingsPage";

function App() {
  const [currentPage, setCurrentPage] = useState<PageKey>("overview");

  return (
    <AppShell currentPage={currentPage} onNavigate={setCurrentPage}>
      {currentPage === "overview" && <OverviewPage />}
      {currentPage === "holdings" && <HoldingsPage />}
      {currentPage === "allocation" && <AllocationPage />}
    </AppShell>
  );
}

export default App;
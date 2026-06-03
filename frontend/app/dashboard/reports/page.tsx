import { SectionPage } from "../_components/SectionPage";

export default function ReportsPage() {
  return (
    <SectionPage
      title="Reports"
      description="Generate and review simple clinical summaries."
      cards={[
        { title: "Daily Summary", value: "12", detail: "Reports available for today." },
        { title: "Weekly Summary", value: "5", detail: "Recent overview exports." },
        { title: "Pending Export", value: "1", detail: "Report waiting to be shared." },
      ]}
    />
  );
}
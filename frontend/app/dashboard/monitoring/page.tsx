import { SectionPage } from "../_components/SectionPage";

export default function MonitoringPage() {
  return (
    <SectionPage
      title="Monitoring"
      description="Track vitals and monitoring sessions in one place."
      cards={[
        { title: "Open Sessions", value: "18", detail: "Patients with live or recent monitoring." },
        { title: "Alerts", value: "2", detail: "Sessions needing clinician review." },
        { title: "Avg FHR", value: "142", detail: "Current fetal heart rate summary." },
      ]}
    />
  );
}
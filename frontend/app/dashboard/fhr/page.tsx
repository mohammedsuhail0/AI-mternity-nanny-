import { SectionPage } from "../_components/SectionPage";

export default function FhrPage() {
  return (
    <SectionPage
      title="Fetal Heart Rate"
      description="Review FHR trends and quick summaries."
      cards={[
        { title: "Baseline", value: "142 bpm", detail: "Within the expected range." },
        { title: "Accelerations", value: "3", detail: "Recent accelerations recorded." },
        { title: "Decelerations", value: "0", detail: "No decelerations in the latest sample." },
      ]}
    />
  );
}
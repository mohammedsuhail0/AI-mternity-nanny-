import { SectionPage } from "../_components/SectionPage";

export default function AIAssessmentPage() {
  return (
    <SectionPage
      title="AI Risk Assessment"
      description="View model-generated pregnancy risk summaries."
      cards={[
        { title: "High Risk", value: "2", detail: "Cases needing immediate review." },
        { title: "Moderate Risk", value: "4", detail: "Cases to keep on close watch." },
        { title: "Model Status", value: "Ready", detail: "Fallback mode is available when no trained model exists." },
      ]}
    />
  );
}
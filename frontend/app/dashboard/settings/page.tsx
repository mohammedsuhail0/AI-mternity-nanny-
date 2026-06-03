import { SectionPage } from "../_components/SectionPage";

export default function SettingsPage() {
  return (
    <SectionPage
      title="Settings"
      description="Adjust basic account and application preferences."
      cards={[
        { title: "Profile", value: "Update", detail: "Manage clinician profile details." },
        { title: "Security", value: "JWT", detail: "Token-based auth is enabled." },
        { title: "Theme", value: "Responsive", detail: "Layout adapts to phones and tablets." },
      ]}
    />
  );
}
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";

interface SectionPageProps {
  title: string;
  description: string;
  cards: Array<{
    title: string;
    value: string;
    detail: string;
  }>;
}

export function SectionPage({ title, description, cards }: SectionPageProps) {
  return (
    <div className="space-y-6 pb-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100 sm:text-3xl">{title}</h1>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400 sm:text-base">{description}</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {cards.map((card) => (
          <Card key={card.title} className="h-full">
            <CardHeader>
              <CardTitle>{card.title}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold text-slate-900 dark:text-slate-100">{card.value}</p>
              <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">{card.detail}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
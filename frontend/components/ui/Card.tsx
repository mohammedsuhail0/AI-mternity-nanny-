import { ReactNode } from "react";

type CardVariant = "default" | "elevated" | "outlined" | "glass";

interface CardProps {
  children: ReactNode;
  className?: string;
  variant?: CardVariant;
  onClick?: () => void;
  hoverable?: boolean;
}

const variantStyles: Record<CardVariant, string> = {
  default: "bg-white border border-gray-200",
  elevated: "bg-white shadow-md border-0",
  outlined: "bg-transparent border-2 border-primary-200",
  glass: "bg-white/70 backdrop-blur-sm border border-white/30",
};

export function Card({
  children,
  className = "",
  variant = "default",
  onClick,
  hoverable = false,
}: CardProps) {
  return (
    <div
      className={`
        rounded-xl p-4 transition-all duration-200
        ${variantStyles[variant]}
        ${hoverable ? "hover:shadow-lg hover:-translate-y-0.5 cursor-pointer" : ""}
        ${onClick ? "cursor-pointer focus-visible:ring-2 focus-visible:ring-primary-500" : ""}
        ${className}
      `}
      onClick={onClick}
      role={onClick ? "button" : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={
        onClick
          ? (e) => {
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                onClick();
              }
            }
          : undefined
      }
    >
      {children}
    </div>
  );
}

interface CardHeaderProps {
  children: ReactNode;
  className?: string;
  subtitle?: string;
  action?: ReactNode;
}

export function CardHeader({
  children,
  className = "",
  subtitle,
  action,
}: CardHeaderProps) {
  return (
    <div className={`flex items-start justify-between mb-3 ${className}`}>
      <div className="min-w-0">
        <div className="text-lg font-semibold text-gray-900 truncate">{children}</div>
        {subtitle && <p className="text-sm text-gray-500 mt-0.5">{subtitle}</p>}
      </div>
      {action && <div className="ml-3 flex-shrink-0">{action}</div>}
    </div>
  );
}

interface CardTitleProps {
  children: ReactNode;
  className?: string;
}

export function CardTitle({ children, className = "" }: CardTitleProps) {
  return <div className={`text-lg font-semibold text-gray-900 truncate ${className}`}>{children}</div>;
}

interface CardBodyProps {
  children: ReactNode;
  className?: string;
}

export function CardBody({ children, className = "" }: CardBodyProps) {
  return <div className={className}>{children}</div>;
}

export function CardContent({ children, className = "" }: CardBodyProps) {
  return <CardBody className={className}>{children}</CardBody>;
}

interface CardFooterProps {
  children: ReactNode;
  className?: string;
  bordered?: boolean;
}

export function CardFooter({ children, className = "", bordered = false }: CardFooterProps) {
  return (
    <div
      className={`
        mt-4 pt-4 flex items-center justify-between
        ${bordered ? "border-t border-gray-100" : ""}
        ${className}
      `}
    >
      {children}
    </div>
  );
}

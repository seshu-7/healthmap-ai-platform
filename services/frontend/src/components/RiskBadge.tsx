interface Props { score: number; level: string; }

export default function RiskBadge({ score, level }: Props) {
  const cls = score >= 9 ? 'badge-critical' : score >= 7 ? 'badge-high'
    : score >= 4 ? 'badge-moderate' : 'badge-low';
  return (
    <span className={`badge ${cls}`} style={{ fontSize: 12 }}>
      {score}/10 {level}
    </span>
  );
}
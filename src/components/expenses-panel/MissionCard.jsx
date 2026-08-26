import Card from '../common/Card';
import Button from '../common/Button';

export default function MissionCard({
  imageSrc,
  title = 'Serenity in Vicinity',
  description,
  ctaLabel = 'Our Mission',
  onCtaClick,
}) {
  const cardStyle = { padding: 'var(--space-5)', display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 'var(--space-2)' };
  const imageWrapStyle = { width: '100%', height: 96, display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 'var(--space-2)' };
  const imageStyle = { maxHeight: '100%', objectFit: 'contain' };
  const titleStyle = { margin: 0, fontSize: 20, fontWeight: 800, color: 'var(--color-text-heading)' };
  const descriptionStyle = { margin: '0 0 var(--space-4)', fontSize: 14, lineHeight: 1.5, color: 'var(--color-text-muted)' };

  return (
    <Card style={cardStyle}>
      <div style={imageWrapStyle}>
        {imageSrc && <img src={imageSrc} alt="" style={imageStyle} />}
      </div>
      <h3 style={titleStyle}>{title}</h3>
      <p style={descriptionStyle}>{description}</p>
      <Button onClick={onCtaClick}>{ctaLabel}</Button>
    </Card>
  );
}
import ExpenseItem from './ExpenseItem';
import MissionCard from './MissionCard';

export default function ExpensesPanel({ title, items = [], mission }) {
  const panelStyle = {
    width: 320,
    flexShrink: 0,
    padding: 'var(--space-6) var(--space-5)',
    boxSizing: 'border-box',
  };

  const titleStyle = {
    margin: '0 0 var(--space-6)',
    fontSize: 22,
    fontWeight: 800,
    color: 'var(--color-text-on-dark)',
<<<<<<< HEAD
=======
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
>>>>>>> prototype1
  };

  const listStyle = {
    display: 'flex',
    flexDirection: 'column',
    gap: 'var(--space-5)',
    marginBottom: 'var(--space-6)',
  };

  return (
    <aside className="expenses-panel" style={panelStyle}>
      <h2 style={titleStyle}>{title}</h2>
      <div style={listStyle}>
        {items.map((item) => (
          <ExpenseItem
            key={item.id}
            label={item.label}
            value={item.value}
            percent={item.percent}
<<<<<<< HEAD
=======
            color={item.color}
            severity={item.severity}
            model={item.model}
>>>>>>> prototype1
          />
        ))}
      </div>
      {mission && (
        <MissionCard
          imageSrc={mission.imageSrc}
          title={mission.title}
          description={mission.description}
          ctaLabel={mission.ctaLabel}
        />
      )}
    </aside>
  );
}
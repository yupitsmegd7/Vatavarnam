import PageSection from '../components/dashboard/PageSection';
import DashboardHeader from '../components/dashboard/DashboardHeader';
import BarChart from '../components/dashboard/BarChart';
import ProgressBar from '../components/common/ProgressBar';
import MapPanel from '../components/map/MapPanel';
import { useForecastData } from '../hooks/useForecastData';
import { formatNumber } from '../utils/formatNumber';

export default function Forecast3() {
  const { items, chartData, hotspots, isLive, lastUpdated, activeSource } = useForecastData(3);

  const sectionTitleStyle = {
    margin: '0 0 var(--space-5)',
    fontSize: 24,
    fontWeight: 800,
    color: 'var(--color-text-heading)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
  };

  const listStyle = {
    display: 'flex',
    flexDirection: 'column',
    gap: 'var(--space-6)',
  };

  const rowHeaderStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'baseline',
    marginBottom: 6,
  };

  const labelStyle = { 
    fontSize: 15, 
    fontWeight: 600, 
    color: 'var(--color-text-heading)',
    display: 'flex',
    alignItems: 'center',
    gap: 8,
  };

  const valueStyle = { 
    fontSize: 14, 
    fontWeight: 600, 
    color: 'var(--color-text-muted)' 
  };

  const statusBadgeStyle = {
    fontSize: 11,
    fontWeight: 600,
    color: '#059669',
    background: 'rgba(5, 150, 105, 0.12)',
    padding: '3px 10px',
    borderRadius: 'var(--radius-full)',
    display: 'inline-flex',
    alignItems: 'center',
    gap: 6,
  };

  const pulseDotStyle = {
    width: 6,
    height: 6,
    borderRadius: '50%',
    backgroundColor: '#10b981',
    boxShadow: '0 0 6px #10b981',
  };

  const modelBadgeStyle = {
    fontSize: 10,
    fontWeight: 600,
    padding: '2px 7px',
    borderRadius: 'var(--radius-full)',
    background: 'rgba(92, 107, 192, 0.15)',
    color: '#4f46e5',
  };

  const targetDate = new Date();
  targetDate.setDate(targetDate.getDate() + 3); // 3 Days from now
  const dateString = targetDate.toLocaleDateString('en-GB', { day: '2-digit', month: 'long', year: 'numeric' });
  const dateRange = lastUpdated ? `${dateString} • Updated ${lastUpdated}` : dateString;

  return (
    <PageSection id="forecast-3" rightPanel={<MapPanel hotspots={hotspots} alt="Delhi NCR hotspot map" />}>
      <DashboardHeader
        title="Forecast (72h)"
        dateRange={dateRange}
      />
      <BarChart data={chartData} />

      <section style={{ marginTop: 'var(--space-6)' }}>
        <div style={sectionTitleStyle}>
          <span>Prediction Map Day 3</span>
          {isLive && (
            <span style={statusBadgeStyle} title={activeSource}>
              <span style={pulseDotStyle} />
              6 ML Models Active
            </span>
          )}
        </div>
        <div style={listStyle}>
          {items.map((item) => (
            <div key={item.id}>
              <div style={rowHeaderStyle}>
                <span style={labelStyle}>
                  {item.label}
                  {item.model && <span style={modelBadgeStyle}>{item.model}</span>}
                </span>
                <span style={valueStyle}>
                  {formatNumber(item.value)} {item.unit || ''}
                </span>
              </div>
              <ProgressBar percent={item.percent} />
            </div>
          ))}
        </div>
      </section>
    </PageSection>
  );
}

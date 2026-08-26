import PageSection from '../components/dashboard/PageSection';
import DashboardHeader from '../components/dashboard/DashboardHeader';
import BarChart from '../components/dashboard/BarChart';
import ProgressBar from '../components/common/ProgressBar';
import MapPanel from '../components/map/MapPanel';
import { useForecastData } from '../hooks/useForecastData';
import { formatNumber } from '../utils/formatNumber';

const collaborators = [{ id: 1 }, { id: 2 }, { id: 3 }, { id: 4 }];

export default function Forecast() {
  const { items, chartData, isLive, lastUpdated, activeSource } = useForecastData();

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
    gap: 'var(--space-5)',
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

  return (
    <PageSection id="forecast" rightPanel={<MapPanel alt="Delhi NCR hotspot map" />}>
      <DashboardHeader
        title="Forecast"
        dateRange={lastUpdated ? `01 - 25 March, 2020 • Updated ${lastUpdated}` : "01 - 25 March, 2020"}
        collaborators={collaborators}
      />
      <BarChart data={chartData} />

      <section style={{ marginTop: 'var(--space-6)' }}>
        <div style={sectionTitleStyle}>
          <span>Prediction Map Day 1</span>
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

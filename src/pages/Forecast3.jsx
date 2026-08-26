import PageSection from '../components/dashboard/PageSection';
import DashboardHeader from '../components/dashboard/DashboardHeader';
import BarChart from '../components/dashboard/BarChart';
import ProgressBar from '../components/common/ProgressBar';
import MapPanel from '../components/map/MapPanel';
import { chartData } from '../data/chartData';
import { forecastPanelData } from '../data/forecastPanelData';
import { formatNumber } from '../utils/formatNumber';

const collaborators = [{ id: 1 }, { id: 2 }, { id: 3 }, { id: 4 }];

export default function Forecast3() {
  const sectionTitleStyle = {
    margin: '0 0 var(--space-5)',
    fontSize: 24,
    fontWeight: 800,
    color: 'var(--color-text-heading)',
  };

  const listStyle = {
    display: 'flex',
    flexDirection: 'column',
    gap: 'var(--space-5)',
  };

  const rowHeaderStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    marginBottom: 6,
  };

  const labelStyle = { fontSize: 15, fontWeight: 600, color: 'var(--color-text-heading)' };
  const valueStyle = { fontSize: 14, fontWeight: 600, color: 'var(--color-text-muted)' };

  return (
    <PageSection id="forecast-3" rightPanel={<MapPanel alt="Delhi NCR hotspot map" />}>
      <DashboardHeader
        title="Forecast"
        dateRange="01 - 25 March, 2020"
        collaborators={collaborators}
      />
      <BarChart data={chartData} />

      <section style={{ marginTop: 'var(--space-6)' }}>
        <h2 style={sectionTitleStyle}>Where your money go?</h2>
        <div style={listStyle}>
          {forecastPanelData.map((item) => (
            <div key={item.id}>
              <div style={rowHeaderStyle}>
                <span style={labelStyle}>{item.label}</span>
                <span style={valueStyle}>{formatNumber(item.value)}</span>
              </div>
              <ProgressBar percent={item.percent} />
            </div>
          ))}
        </div>
      </section>
    </PageSection>
  );
}

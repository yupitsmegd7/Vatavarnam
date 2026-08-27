<<<<<<< HEAD
import DashboardLayout from '../layouts/DashboardLayout';
import DashboardHeader from '../components/dashboard/DashboardHeader';
import BarChart from '../components/dashboard/BarChart';
import TodayList from '../components/dashboard/TodayList';
import { chartData } from '../data/chartData';
import { todayData } from '../data/todayData';

const collaborators = [
  { id: 1, src: '' },
  { id: 2, src: '' },
  { id: 3, src: '' },
  { id: 4, src: '' },
];



export default function Meteorology() {
  return (
    <DashboardLayout>
      <DashboardHeader
        title="Meteorology"
        dateRange="1-25 March, 2020"
        collaborators={collaborators}
      />
      <BarChart data={chartData} />
      <TodayList items={todayData} />
    </DashboardLayout>
  );
}
=======
import { useState, useEffect } from 'react';
import PageSection from '../components/dashboard/PageSection';
import DashboardHeader from '../components/dashboard/DashboardHeader';
import BarChart from '../components/dashboard/BarChart';
import TodayList from '../components/dashboard/TodayList';
import ExpensesPanel from '../components/expenses-panel/ExpensesPanel';
import { chartData as initialChartData } from '../data/chartData';
import { todayData as initialTodayData } from '../data/todayData';
import { expensesData as initialExpensesData } from '../data/expensesData';

function getSeverityInfo(targetId, percent) {
  const pct = Number(percent);
  const isHigherBad = targetId === 'asthma-index' || targetId === 'flight-delay';

  if (isHigherBad) {
    if (pct <= 30) return { severity: 'Good / Low Risk', color: '#10b981' };
    if (pct <= 55) return { severity: 'Moderate Risk', color: '#f59e0b' };
    if (pct <= 75) return { severity: 'High Risk', color: '#f97316' };
    return { severity: 'Severe / Hazardous', color: '#ef4444' };
  } else {
    if (pct >= 70) return { severity: 'Optimal / Safe', color: '#10b981' };
    if (pct >= 45) return { severity: 'Moderate / Fair', color: '#f59e0b' };
    if (pct >= 25) return { severity: 'Poor / Caution', color: '#f97316' };
    return { severity: 'Hazardous / Inadvisable', color: '#ef4444' };
  }
}

export default function Meteorology() {
  const [liveTodayData, setLiveTodayData] = useState(initialTodayData);
  const [liveChartData, setLiveChartData] = useState(initialChartData);
  const [liveActivityData, setLiveActivityData] = useState(
    initialExpensesData.map((item) => ({
      ...item,
      ...getSeverityInfo(item.id, item.percent),
    }))
  );

  useEffect(() => {
    const fetchApiData = async () => {
      // 1. Try Fetching Activity Predictions from Python ML Backend
      try {
        const actRes = await fetch('/api/activity/predictions');
        if (actRes.ok) {
          const actJson = await actRes.json();
          if (actJson.items && actJson.items.length > 0) {
            setLiveActivityData(actJson.items);
          }
        }
      } catch (actErr) {
        console.log('Backend activity endpoint connecting...');
      }

      // 2. Fetch Open-Meteo Weather & Air Quality for Delhi NCR
      try {
        const [weatherRes, airRes] = await Promise.all([
          fetch(
            'https://api.open-meteo.com/v1/forecast?latitude=28.6139&longitude=77.2090&current=temperature_2m,relative_humidity_2m&daily=temperature_2m_max,precipitation_sum,shortwave_radiation_sum&timezone=Asia%2FKolkata'
          ),
          fetch(
            'https://air-quality-api.open-meteo.com/v1/air-quality?latitude=28.6139&longitude=77.2090&hourly=pm10,pm2_5,carbon_monoxide,european_aqi&timezone=Asia%2FKolkata&past_days=1'
          ),
        ]);

        const weatherData = await weatherRes.json();
        const airData = await airRes.json();

        const now = new Date();
        const nowTime = now.getTime();
        let currentHourIndex = airData.hourly.time.findIndex((timeStr) => {
          const timeMs = new Date(timeStr + '+05:30').getTime();
          return timeMs >= nowTime - 1800000;
        });
        if (currentHourIndex === -1) currentHourIndex = 24 + now.getHours();

        const currentAqi = airData.hourly.european_aqi[currentHourIndex] || 50;
        const currentPm25 = airData.hourly.pm2_5[currentHourIndex] || 35;
        const currentPm10 = airData.hourly.pm10[currentHourIndex] || 60;
        const currentCo = airData.hourly.carbon_monoxide[currentHourIndex] || 400;
        const currentTempNow = weatherData.current?.temperature_2m || 30;
        const currentHumidity = weatherData.current?.relative_humidity_2m || 60;
        const currentTempMax = weatherData.daily.temperature_2m_max[0] || 30;
        const currentPrecip = weatherData.daily.precipitation_sum[0] || 0;
        const currentRadiation = weatherData.daily.shortwave_radiation_sum[0] || 15;

        const updatedToday = [
          {
            id: 'temp-now',
            label: 'Current Temp.',
            time: 'Right Now',
            place: 'Delhi',
            value: currentTempNow,
            unit: '°C',
            icon: 'bus',
            color: 'var(--icon-orange)',
          },
          {
            id: 'aqi',
            label: 'Current AQI',
            time: 'Right Now',
            place: 'Delhi',
            value: currentAqi,
            unit: 'EAQI',
            icon: 'home',
            color: 'var(--icon-purple)',
          },
          {
            id: 'temp-max',
            label: 'Max Temp.',
            time: 'Today',
            place: 'Delhi',
            value: currentTempMax,
            unit: '°C',
            icon: 'bus',
            color: 'var(--icon-orange)',
          },
          {
            id: 'co',
            label: 'Carbon Monoxide',
            time: 'Current',
            place: 'Delhi',
            value: currentCo,
            unit: 'μg/m³',
            icon: 'cart',
            color: 'var(--icon-blue)',
          },
          {
            id: 'pm25',
            label: 'PM 2.5',
            time: 'Current',
            place: 'Delhi',
            value: currentPm25,
            unit: 'μg/m³',
            icon: 'home',
            color: 'var(--icon-green)',
          },
          {
            id: 'pm10',
            label: 'PM 10',
            time: 'Current',
            place: 'Delhi',
            value: currentPm10,
            unit: 'μg/m³',
            icon: 'home',
            color: 'var(--icon-navy)',
          },
          {
            id: 'precipitation',
            label: 'Precipitation',
            time: 'Today',
            place: 'Delhi',
            value: currentPrecip,
            unit: 'mm',
            icon: 'cart',
            color: 'var(--icon-blue)',
          },
          {
            id: 'radiation',
            label: 'Radiation',
            time: 'Today',
            place: 'Delhi',
            value: currentRadiation,
            unit: 'MJ/m²',
            icon: 'home',
            color: 'var(--icon-purple)',
          },
        ];
        setLiveTodayData(updatedToday);

        // Fallback calculation for activity data if backend was offline
        setLiveActivityData((prev) => {
          if (prev.some((p) => p.model)) return prev;
          const walkPct = Math.min(95, Math.max(5, Math.round(100 - (currentPm25 / 150) * 45 - (currentPm10 / 250) * 20)));
          const outingPct = Math.min(95, Math.max(5, Math.round(100 - (currentAqi / 120) * 55)));
          const visPct = Math.min(95, Math.max(5, Math.round(100 - (currentPm25 / 250) * 45 - (currentHumidity / 100) * 20)));
          const drivePct = Math.min(95, Math.max(5, Math.round(100 - (currentPm25 / 180) * 40 - 15)));
          const shipPct = Math.min(95, Math.max(5, Math.round(100 - (currentPrecip * 15) - (currentPm10 / 300) * 20)));
          const asthmaPct = Math.min(98, Math.max(5, Math.round((currentPm25 / 140) * 65 + 15)));
          const flightPct = Math.min(98, Math.max(5, Math.round((currentPm25 / 160) * 40 + (currentPrecip > 2 ? 35 : 10))));

          const calculated = [
            { id: 'walking', label: 'Walking', value: Math.round(walkPct * 18.5 * 10) / 10, percent: walkPct, ...getSeverityInfo('walking', walkPct) },
            { id: 'outing', label: 'Outing', value: Math.round(outingPct * 19.8 * 10) / 10, percent: outingPct, ...getSeverityInfo('outing', outingPct) },
            { id: 'visibility', label: 'Visibility', value: Math.round(visPct * 17.5 * 10) / 10, percent: visPct, ...getSeverityInfo('visibility', visPct) },
            { id: 'long-drive', label: 'Long Drive', value: Math.round(drivePct * 16.2 * 10) / 10, percent: drivePct, ...getSeverityInfo('long-drive', drivePct) },
            { id: 'shipment-safety', label: 'Shipment Safety', value: Math.round(shipPct * 14.0 * 10) / 10, percent: shipPct, ...getSeverityInfo('shipment-safety', shipPct) },
            { id: 'asthma-index', label: 'Asthma Index', value: Math.round(asthmaPct * 13.5 * 10) / 10, percent: asthmaPct, ...getSeverityInfo('asthma-index', asthmaPct) },
            { id: 'flight-delay', label: 'Flight Delay', value: Math.round(flightPct * 13.5 * 10) / 10, percent: flightPct, ...getSeverityInfo('flight-delay', flightPct) },
          ];
          return calculated;
        });

        // 3. Update Hourly Pollution Bar Chart (6 hrs before, 10 hrs after = 17 bars)
        const maxPollutionPossible = 250;
        const startIndex = Math.max(0, currentHourIndex - 6);
        const endIndex = Math.min(airData.hourly.time.length, currentHourIndex + 11);
        const hourlySlice = airData.hourly.time.slice(startIndex, endIndex);

        const updatedChart = hourlySlice.map((dateString, i) => {
          const actualIndex = startIndex + i;
          const pm25 = airData.hourly.pm2_5[actualIndex];
          const pm10 = airData.hourly.pm10[actualIndex];
          const aqi = airData.hourly.european_aqi[actualIndex];

          const ratio = Math.min(pm25 / maxPollutionPossible, 1.0);
          const dateObj = new Date(dateString);
          const hourStr = dateObj.getHours().toString().padStart(2, '0') + ':00';

          return {
            id: dateString,
            value: ratio > 0 ? ratio : 0.05,
            label: hourStr,
            topLabel: aqi,
            tooltip: `AQI: ${aqi} | PM2.5: ${pm25} μg/m³ | PM10: ${pm10} μg/m³`,
            highlighted: aqi > 100,
          };
        });
        setLiveChartData(updatedChart);
      } catch (error) {
        console.error('Error fetching meteorology data:', error);
      }
    };

    fetchApiData();
    const interval = setInterval(fetchApiData, 30 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const todayDate = new Date();
  const dateString = todayDate.toLocaleDateString('en-GB', { day: '2-digit', month: 'long', year: 'numeric' });
  const dateRange = `${dateString} (Hourly Air Quality 24h)`;

  return (
    <PageSection
      id="meteorology"
      rightPanel={
        <ExpensesPanel
          title="Activity Prediction"
          items={liveActivityData}
          mission={{
            title: 'Serenity in Vicinity',
            description:
              'Creating awareness about the air that surrounds us and our loved ones.',
            ctaLabel: 'Our Mission',
          }}
        />
      }
    >
      <DashboardHeader
        title="Meteorology"
        dateRange={dateRange}
      />
      <BarChart data={liveChartData} />
      <TodayList items={liveTodayData} />
    </PageSection>
  );
}
>>>>>>> prototype1

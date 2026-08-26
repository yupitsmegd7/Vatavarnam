import { useState, useEffect } from 'react';
import PageSection from '../components/dashboard/PageSection';
import DashboardHeader from '../components/dashboard/DashboardHeader';
import BarChart from '../components/dashboard/BarChart';
import TodayList from '../components/dashboard/TodayList';
import ExpensesPanel from '../components/expenses-panel/ExpensesPanel';
import { chartData as initialChartData } from '../data/chartData';
import { todayData as initialTodayData } from '../data/todayData';
import { expensesData } from '../data/expensesData';

const collaborators = [{ id: 1 }, { id: 2 }, { id: 3 }, { id: 4 }];

export default function Meteorology() {
  const [liveTodayData, setLiveTodayData] = useState(initialTodayData);
  const [liveChartData, setLiveChartData] = useState(initialChartData);

  useEffect(() => {
    const fetchApiData = async () => {
      try {
        // Fetch Weather and Air Quality (with past_days=1 to ensure we have data 6 hours ago even at midnight)
        const [weatherRes, airRes] = await Promise.all([
          fetch('https://api.open-meteo.com/v1/forecast?latitude=28.6139&longitude=77.2090&daily=temperature_2m_max,precipitation_sum,shortwave_radiation_sum&timezone=Asia%2FKolkata'),
          fetch('https://air-quality-api.open-meteo.com/v1/air-quality?latitude=28.6139&longitude=77.2090&hourly=pm10,pm2_5,carbon_monoxide,european_aqi&timezone=Asia%2FKolkata&past_days=1')
        ]);
        
        const weatherData = await weatherRes.json();
        const airData = await airRes.json();
        
        // --- 1. UPDATE TODAY'S STATS ---
        // Find current hour index dynamically
        const now = new Date();
        const nowTime = now.getTime();
        let currentHourIndex = airData.hourly.time.findIndex(timeStr => {
            const timeMs = new Date(timeStr + '+05:30').getTime(); 
            return timeMs >= nowTime - 1800000;
        });
        if (currentHourIndex === -1) currentHourIndex = 24 + now.getHours();

        const updatedToday = [
           { 
             id: 'temp-max', 
             label: 'Max Temp.', 
             time: 'Today', 
             place: 'Delhi', 
             value: weatherData.daily.temperature_2m_max[0], 
             unit: '°C',
             icon: 'bus', 
             color: 'var(--icon-orange)' 
           },
           { 
             id: 'aqi', 
             label: 'AVG AQI', 
             time: 'Current', 
             place: 'Delhi', 
             value: airData.hourly.european_aqi[currentHourIndex], 
             unit: 'EAQI',
             icon: 'home', 
             color: 'var(--icon-purple)' 
           },
           { 
             id: 'co', 
             label: 'Carbon Monoxide', 
             time: 'Current', 
             place: 'Delhi', 
             value: airData.hourly.carbon_monoxide[currentHourIndex], 
             unit: 'μg/m³',
             icon: 'cart', 
             color: 'var(--icon-blue)' 
           },
           { 
             id: 'pm25', 
             label: 'PM 2.5', 
             time: 'Current', 
             place: 'Delhi', 
             value: airData.hourly.pm2_5[currentHourIndex], 
             unit: 'μg/m³',
             icon: 'home', 
             color: 'var(--icon-green)' 
           },
           { 
             id: 'pm10', 
             label: 'PM 10', 
             time: 'Current', 
             place: 'Delhi', 
             value: airData.hourly.pm10[currentHourIndex], 
             unit: 'μg/m³',
             icon: 'home', 
             color: 'var(--icon-navy)' 
           },
           { 
             id: 'precipitation', 
             label: 'Precipitation', 
             time: 'Today', 
             place: 'Delhi', 
             value: weatherData.daily.precipitation_sum[0], 
             unit: 'mm',
             icon: 'cart', 
             color: 'var(--icon-blue)' 
           },
           { 
             id: 'radiation', 
             label: 'Radiation', 
             time: 'Today', 
             place: 'Delhi', 
             value: weatherData.daily.shortwave_radiation_sum[0], 
             unit: 'MJ/m²',
             icon: 'home', 
             color: 'var(--icon-purple)' 
           },
        ];
        setLiveTodayData(updatedToday);

        // --- 2. UPDATE BAR CHART (HOURLY POLLUTION) ---
        const maxPollutionPossible = 250; 
        
        // Take 6 hours before and 6 hours after current time
        const startIndex = Math.max(0, currentHourIndex - 6);
        const endIndex = Math.min(airData.hourly.time.length, currentHourIndex + 7);
        const hourlySlice = airData.hourly.time.slice(startIndex, endIndex);
        
        const updatedChart = hourlySlice.map((dateString, i) => {
           const actualIndex = startIndex + i;
           const pm25 = airData.hourly.pm2_5[actualIndex];
           const pm10 = airData.hourly.pm10[actualIndex];
           const aqi = airData.hourly.european_aqi[actualIndex];
           
           const ratio = Math.min(pm25 / maxPollutionPossible, 1.0);
           
           // Format label to show hour like "14:00"
           const dateObj = new Date(dateString);
           const hourStr = dateObj.getHours().toString().padStart(2, '0') + ':00';

           return {
             id: dateString,
             value: ratio > 0 ? ratio : 0.05, 
             label: hourStr,
             topLabel: aqi, 
             tooltip: `AQI: ${aqi} | PM2.5: ${pm25} μg/m³ | PM10: ${pm10} μg/m³`,
             highlighted: aqi > 100 // Highlight bars where AQI is bad
           };
        });
        setLiveChartData(updatedChart);

      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchApiData();

    // Refetch every 30 minutes
    const interval = setInterval(fetchApiData, 30 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <PageSection
      id="meteorology"
      rightPanel={
        <ExpensesPanel
          title="Activity Prediction"
          items={expensesData}
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
        dateRange="Hourly Air Quality (24h)"
        collaborators={collaborators}
      />
      <BarChart data={liveChartData} />
      <TodayList items={liveTodayData} />
    </PageSection>
  );
}

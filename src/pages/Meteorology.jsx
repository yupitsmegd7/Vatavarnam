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
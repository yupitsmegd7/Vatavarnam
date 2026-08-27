import DashboardLayout from '../layouts/DashboardLayout';
import Meteorology from './Meteorology';
import Forecast from './Forecast';
import Forecast2 from './Forecast2';
import Forecast3 from './Forecast3';

export default function Home() {
  return (
    <DashboardLayout>
      <Meteorology />
      <Forecast />
      <Forecast2 />
      <Forecast3 />
    </DashboardLayout>
  );
}

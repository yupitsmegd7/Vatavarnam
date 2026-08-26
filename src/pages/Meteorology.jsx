import PageSection from '../components/dashboard/PageSection';
import DashboardHeader from '../components/dashboard/DashboardHeader';
import BarChart from '../components/dashboard/BarChart';
import TodayList from '../components/dashboard/TodayList';
import ExpensesPanel from '../components/expenses-panel/ExpensesPanel';
import { chartData } from '../data/chartData';
import { todayData } from '../data/todayData';
import { expensesData } from '../data/expensesData';

const collaborators = [{ id: 1 }, { id: 2 }, { id: 3 }, { id: 4 }];

export default function Meteorology() {
  return (
    <PageSection
      id="meteorology"
      rightPanel={
        <ExpensesPanel
          title="Where your money go?"
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
        dateRange="01 - 25 March, 2020"
        collaborators={collaborators}
      />
      <BarChart data={chartData} />
      <TodayList items={todayData} />
    </PageSection>
  );
}

import { useState, useEffect } from 'react';
import { chartData as staticChartData } from '../data/chartData';

/**
 * Provides the hourly-prediction bar chart data.
 * Currently returns the static mock data immediately, but is structured
 * so it can later be swapped for a real API call (e.g. fetch('/api/hourly'))
 * without changing how BarChart.jsx or Meteorology.jsx consume it.
 */
export function useChartData() {
  const [data, setData] = useState(staticChartData);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Placeholder for a future async fetch. Left synchronous for now
    // since the data is static, but the loading/error states are wired
    // up so components don't need to change when this becomes a real call.
    setIsLoading(true);
    try {
      setData(staticChartData);
      setError(null);
    } catch (err) {
      setError(err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { data, isLoading, error };
}
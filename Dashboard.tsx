import React, { useEffect, useState } from "react";
import axios from "axios";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend);

const API_KEY = process.env.REACT_APP_CRYPTO_API_KEY;
const API_URL = "https://api.example.com/data";

interface Investment {
  id: string;
  name: string;
  amountInvested: number;
  currentPrice: number;
}

interface MarketNews {
  title: string;
  description: string;
  url: string;
}

interface ErrorState {
  hasError: boolean;
  message?: string;
}

const CryptoLedgerDashboard: React.FC = () => {
  const [investments, setInvestments] = useState<Investment[]>([]);
  const [marketNews, setMarketNews] = useState<MarketNews[]>([]);
  const [chartData, setChartData] = useState({});
  const [error, setError] = useState<ErrorState>({ hasError: false, message: "" });

  useEffect(() => {
    fetchDashboardData();
  }, []);

  useEffect(() => {
    if (investments.length > 0) {
      updateChartData(investments);
    }
  }, [investments]);

  const logDataToConsole = (data: any, context: string) => {
    console.log(`Logging ${context}: `, data);
  };

  const fetchDashboardData = async () => {
    try {
      const [investmentsResponse, marketNewsResponse] = await Promise.all([
        axios.get(`${API_URL}/investments?apiKey=${API_KEY}`),
        axios.get(`${API_URL}/news?apiKey=${API_KEY}`),
      ]);

      logDataToConsole(investmentsResponse.data, "Investments Data");
      logDataToConsole(marketNewsResponse.data, "Market News Data");

      setInvestments(investmentsResponse.data);
      setMarketNews(marketNewsResponse.data);
    } catch (error) {
      console.error("Error fetching dashboard data:", error);
      setError({ hasError: true, message: "Failed to fetch dashboard data." });
      logDataToConsole(error, "Error");
    }
  };

  const updateChartData = (investments: Investment[]) => {
    const labels = investments.map((investment) => investment.name);
    const data = {
      labels,
      datasets: [
        {
          label: "Current Investment Value",
          backgroundColor: "rgba(53, 162, 235, 0.5)",
          borderColor: "rgba(53, 162, 235, 1)",
          data: investments.map((investment) => investment.currentPrice * investment.amountInvested),
        },
      ],
    };
    logDataToConsole(data, "Chart Data");
    setChartData(data);
  };

  if (error.hasError) {
    return <div>Error: {error.message}</div>;
  }

  return (
    <div>
      <h1>CryptoLedger Dashboard</h1>
      <InvestmentList investments={investments} />
      <AssetTrends chartData={chartData} />
      <MarketNewsList marketNews={marketNews} />
    </div>
  );
};

const InvestmentList: React.FC<{ investments: Investment[] }> = ({ investments }) => (
  <div>
    <h2>Investment Values</h2>
    <ul>
      {investments.map((investment) => (
        <li key={investment.id}>
          {investment.name}: ${investment.currentPrice * investment.amountInvested}
        </li>
      ))}
    </ul>
  </div>
);

const AssetTrends: React.FC<{ chartData: any }> = ({ chartData }) => (
  <div>
    <h2>Asset Trends</h2>
    <Line data={chartData} />
  </div>
);

const MarketNewsList: React.FC<{ marketNews: MarketNews[] }> = ({ marketNews }) => (
  <div>
    <h2>Market News</h2>
    {marketNews.map((news) => (
      <div key={news.title}>
        <h3>{news.title}</h3>
        <p>{news.description}</p>
        <a href={news.url} target="_blank" rel="noreferrer">
          Read more
        </a>
      </div>
    ))}
  </div>
);

export default CryptoLedgerDashboard;
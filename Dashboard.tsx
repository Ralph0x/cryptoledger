import React, { useEffect, useState } from "react";
import axios from "axios";
import { Line } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend);

const API_KEY = process.env.REACT_APP_CRYPTO_API_KEY;
const API_URL = 'https://api.example.com/data';

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

const CryptoLedgerDashboard: React.FC = () => {
  const [investments, setInvestments] = useState<Investment[]>([]);
  const [marketNews, setMarketNews] = useState<MarketNews[]>([]);
  const [chartData, setChartData] = useState({});

  useEffect(() => {
    const fetchInvestments = async () => {
      const response = await axios.get(`${API_URL}/investments?apiKey=${API_KEY}`);
      setInvestments(response.data);
    };

    const fetchMarketNews = async () => {
      const response = await axios.get(`${API_URL}/news?apiKey=${API_KEY}`);
      setMarketNews(response.data);
    };

    fetchInvestments();
    fetchMarketNews();
  }, []);

  useEffect(() => {
    const labels = investments.map(investment => investment.name);
    const data = {
      labels,
      datasets: [
        {
          label: 'Current Investment Value',
          backgroundColor: 'rgba(53, 162, 235, 0.5)',
          borderColor: 'rgba(53, 162, 235, 1)',
          data: investments.map(investment => investment.currentPrice * investment.amountInvested),
        },
      ],
    };
    setChartData(data);
  }, [investments]);

  return (
    <div>
      <h1>CryptoLedger Dashboard</h1>
      
      <div>
        <h2>Investment Values</h2>
        <ul>
          {investments.map(investment => (
            <li key={investment.id}>
              {investment.name}: ${investment.currentPrice * investment.amountInvested}
            </li>
          ))}
        </ul>
      </div>

      <div>
        <h2>Asset Trends</h2>
        <Line data={chartData} />
      </div>
      
      <div>
        <h2>Market News</h2>
        {marketNews.map(news => (
          <div key={news.title}>
            <h3>{news.title}</h3>
            <p>{news.description}</p>
            <a href={news.url} target="_blank" rel="noreferrer">Read more</a>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CryptoLedgerDashboard;
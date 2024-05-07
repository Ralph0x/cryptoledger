import axios from 'axios';

const { REACT_APP_API_BASE_URL } = process.env;

interface PortfolioUpdate {
  assetId: string;
  quantity: number;
}

interface HistoricalDataParams {
  assetId: string;
  from: string;
  to: string;
}

class MarketDataAPI {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async fetchMarketData(): Promise<any> {
    try {
      const response = await axios.get(`${this.baseUrl}/market-data`);
      return response.data;
    } catch (error) {
      console.error('Error fetching market data:', error);
      throw error;
    }
  }

  async updatePortfolio(updateDetails: PortfolioUpdate): Promise<any> {
    try {
      const response = await axios.post(`${this.baseUrl}/portfolio`, updateDetails);
      return response.data;
    } catch (error) {
      console.error('Error updating portfolio:', error);
      throw error;
    }
  }

  async analyzeHistoricalPerformance(params: HistoricalDataParams): Promise<any> {
    try {
      const response = await axios.get(`${this.baseUrl}/historical-performance`, { params });
      return response.data;
    } catch (error) {
      console.error('Error analyzing historical performance:', error);
      throw error;
    }
  }
}

const marketDataAPI = new MarketDataAPI(REACT_APP_API_BASE_URL);

export default marketDataAPI;
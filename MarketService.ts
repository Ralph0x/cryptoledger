import axios, { AxiosError, AxiosResponse } from 'axios';

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

  private async makeRequest<T>(method: 'get' | 'post', url: string, data?: any): Promise<T> {
    try {
      const options = {
        method,
        url,
        ...(method === 'get' ? { params: data } : { data }),
      };
      const response: AxiosResponse<T> = await axios(options);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        // Handling Axios errors specifically
        const axiosError = error as AxiosError;
        if (axiosError.response) {
          console.error(`Axios error response for ${url}:`, axiosError.response);
        } else if (axiosError.request) {
          console.error(`Request made but no response received for ${url}.`, axiosError.request);
        } else {
          console.error(`Error setting up request to ${url}.`, axiosError.message);
        }
      } else {
        // Handling non-Axios errors
        console.error(`Non-Axios error with request to ${url}:`, error);
      }
      throw error;
    }
  }

  fetchMarketData(): Promise<any> {
    return this.makeRequest('get', `${this.baseUrl}/market-data`);
  }

  updatePortfolio(updateDetails: PortfolioUpdate): Promise<any> {
    return this.makeRequest('post', `${this.baseUrl}/portfolio`, updateDetails);
  }

  analyzeHistoricalPerformance(params: HistoricalDataParams): Promise<any> {
    return this.makeRequest('get', `${this.baseUrl}/historical-performance`, params);
  }
}

const marketDataAPI = new MarketDataAPI(REACT_APP_API_BASE_URL);

export default marketDataAPI;
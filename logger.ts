import dotenv from 'dotenv';
import fs from 'fs';
import path from 'path';

dotenv.config();

enum LogLevel {
  DEBUG = 'DEBUG',
  INFO = 'INFO',
  WARN = 'WARN',
  ERROR = 'ERROR',
}

interface LogOptions {
  timestamp?: boolean;
  toFile?: boolean;
}

class Logger {
  private logLevel: LogLevel;
  private filePath: string;
  private defaultOptions: LogOptions = {
    timestamp: true,
    toFile: false,
  };

  constructor() {
    this.logLevel = (process.env.LOG_LEVEL as LogLevel) ?? LogLevel.DEBUG;
    this.filePath = process.env.LOG_FILE_PATH ?? path.join(__dirname, 'app.log');
  }

  private log(level: LogLevel, message: string, options?: LogOptions): void {
    const { timestamp, toFile } = { ...this.defaultOptions, ...options };
    const formattedMessage = `[${level}]${timestamp ? ` [${new Date().toISOString()}]` : ''}: ${message}`;

    if (level >= this.logLevel) {
      console.log(formattedMessage);

      if (toFile) {
        fs.appendFile(this.filePath, formattedMessage + '\n', (err) => {
          if (err) {
            console.error(`Failed to write log to file: ${err}`);
          }
        });
      }
    }
  }

  debug(message: string, options?: LogOptions): void {
    this.log(LogLevel.DEBUG, message, options);
  }

  info(message: string, options?: LogOptions): void {
    this.log(LogLevel.INFO, message, options);
  }

  warn(message: string, options?: LogOptions): void {
    this.log(LogLevel.WARN, message, options);
  }

  error(message: string, options?: LogOptions): void {
    this.log(LogLevel.ERROR, message, options);
  }
}

const logger = new Logger();

export default logger;
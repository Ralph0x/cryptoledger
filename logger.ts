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
        this.logLevel = process.env.LOG_LEVEL as LogLevel ?? LogLevel.DEBUG;
        this.filePath = process.env.LOG_FILE_PATH ?? path.join(__dirname, 'app.log');
    }

    private shouldLog(level: LogLevel): boolean {
        const order = [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARN, LogLevel.ERROR];
        return order.indexOf(level) >= order.indexOf(this.logLevel);
    }

    private formatMessage(level: LogLevel, message: string, { timestamp = true }: LogOptions = {}): string {
        const timeString = timestamp ? ` [${new Date().toISOString()}]` : '';
        return `[${level}]${timeString}: ${message}`;
    }

    private writeToFile(message: string): void {
        fs.appendFile(this.filePath, message + '\n', (err) => {
            if (err) {
                this.log(LogLevel.ERROR, `Failed to write log to file: ${err}`, { toFile: false });
            }
        });
    }

    private log(level: LogLevel, message: string, options: LogOptions = {}): void {
        if (this.shouldLog(level)) {
            const mergedOptions = { ...this.defaultOptions, ...options };
            const formattedMessage = this.formatMessage(level, message, mergedOptions);
            console.log(formattedMessage);

            if (mergedOptions.toFile) {
                this.writeToFile(formattedMessage);
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
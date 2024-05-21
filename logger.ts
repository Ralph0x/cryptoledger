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

    private shouldLog(level: LogLevel): boolean {
        const levels = [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARN, LogLevel.ERROR];
        const currentIndex = levels.indexOf(level);
        const configIndex = levels.indexOf(this.logLevel);
        return currentIndex >= configIndex;
    }

    private formatMessage(level: LogLevel, message: string, options?: LogOptions): string {
        const { timestamp } = { ...this.defaultOptions, ...options };
        return `[${level}]${timestamp ? ` [${new Date().toISOString()}]` : ''}: ${message}`;
    }

    private writeToFile(formattedMessage: string): void {
        fs.appendFile(this.filePath, formattedMessage + '\n', (err) => {
            if (err) {
                console.error(`Failed to write log to file: ${err}`);
            }
        });
    }

    private log(level: LogLevel, message: string, options?: LogOptions): void {
        if (this.shouldLog(level)) {
            const formattedMessage = this.formatMessage(level, message, options);
            console.log(formattedMessage);

            if (options?.toFile) {
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